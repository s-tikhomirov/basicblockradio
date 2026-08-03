#!/usr/bin/env python3
"""Align Format A SRT with a diarized TXT track; promote Format B into NNN-raw.srt."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SRT_TIME_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)
TXT_HEADER_RE = re.compile(
    r"^(.+?)\s+\((\d{1,2}:\d{2}(?::\d{2})?)\)$"
)
FORMAT_B_RE = re.compile(
    r"^\[\d{2}:\d{2}:\d{2}:\d{2}\s*-\s*\d{2}:\d{2}:\d{2}:\d{2}\]"
)
TOKEN_RE = re.compile(r"[0-9a-zа-яё]+", re.IGNORECASE)

MIN_OVERLAP_MS = 1
WEAK_SCORE = 0.15
TXT_COVER_RECALL = 0.55
EPSILON_MS = 1000


@dataclass
class Cue:
    start_ms: int
    end_ms: int
    text: str
    speaker: str | None = None
    flagged: bool = False
    source: str = "srt"  # srt | txt


@dataclass
class Turn:
    start_ms: int
    end_ms: int
    speaker: str
    text: str


def parse_clock_to_ms(value: str) -> int:
    parts = value.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        hours = "0"
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"bad clock value: {value!r}")
    return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000


def ms_to_format_b(ms: int) -> str:
    if ms < 0:
        ms = 0
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    centis = millis // 10
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{centis:02d}"


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def jaccard(a: list[str], b: list[str]) -> float:
    if not a and not b:
        return 0.0
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def token_recall(query: list[str], haystack: list[str]) -> float:
    if not query:
        return 1.0
    if not haystack:
        return 0.0
    hq = set(haystack)
    hit = sum(1 for t in query if t in hq)
    return hit / len(query)


def first_non_empty_line(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return line.strip()
    return ""


def parse_srt(path: Path) -> list[Cue]:
    raw = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", raw.strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 2:
            continue
        time_line = lines[1].strip() if SRT_TIME_RE.match(lines[1].strip()) else None
        text_start = 2
        if time_line is None and SRT_TIME_RE.match(lines[0].strip()):
            time_line = lines[0].strip()
            text_start = 1
        if time_line is None:
            continue
        m = SRT_TIME_RE.match(time_line)
        if not m:
            continue
        start_ms = (
            int(m.group(1)) * 3_600_000
            + int(m.group(2)) * 60_000
            + int(m.group(3)) * 1000
            + int(m.group(4))
        )
        end_ms = (
            int(m.group(5)) * 3_600_000
            + int(m.group(6)) * 60_000
            + int(m.group(7)) * 1000
            + int(m.group(8))
        )
        text = normalize_space(" ".join(lines[text_start:]))
        if not text:
            continue
        cues.append(Cue(start_ms=start_ms, end_ms=end_ms, text=text))
    return cues


def parse_txt(path: Path) -> list[Turn]:
    lines = path.read_text(encoding="utf-8").splitlines()
    turns: list[Turn] = []
    i = 0
    while i < len(lines):
        header = lines[i].strip()
        m = TXT_HEADER_RE.match(header)
        if not m:
            i += 1
            continue
        speaker = m.group(1).strip()
        start_ms = parse_clock_to_ms(m.group(2))
        i += 1
        chunk: list[str] = []
        while i < len(lines):
            stripped = lines[i].strip()
            if TXT_HEADER_RE.match(stripped):
                break
            if stripped:
                chunk.append(stripped)
            elif chunk:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and TXT_HEADER_RE.match(lines[j].strip()):
                    break
            i += 1
        text = normalize_space(" ".join(chunk))
        if text:
            turns.append(Turn(start_ms=start_ms, end_ms=start_ms, speaker=speaker, text=text))
        continue
    return turns


def finalize_turn_ends(turns: list[Turn], fallback_end_ms: int) -> None:
    """End at the next strictly later TXT start so same-second turns share a window."""
    for idx, turn in enumerate(turns):
        end = fallback_end_ms
        for nxt in turns[idx + 1 :]:
            if nxt.start_ms > turn.start_ms:
                end = nxt.start_ms
                break
        turn.end_ms = max(turn.start_ms + 1, end)


def overlap_ms(a0: int, a1: int, b0: int, b1: int) -> int:
    return max(0, min(a1, b1) - max(a0, b0))


def assign_speakers(cues: list[Cue], turns: list[Turn]) -> list[int]:
    flagged_ms: list[int] = []
    prev_speaker: str | None = None
    for cue in cues:
        cue_toks = tokens(cue.text)
        cue_dur = max(1, cue.end_ms - cue.start_ms)
        short_cue = cue_dur <= 2500 or len(cue_toks) <= 3
        best_idx = -1
        best_score = -1.0
        for idx, turn in enumerate(turns):
            ov = overlap_ms(cue.start_ms, cue.end_ms, turn.start_ms, turn.end_ms)
            start_delta = abs(cue.start_ms - turn.start_ms)
            near = max(0.0, 1.0 - start_delta / 4000.0)
            ov_score = ov / cue_dur
            lex = jaccard(cue_toks, tokens(turn.text))
            # Short cues often share a coarse TXT second; prefer wording.
            if short_cue:
                score = lex * 0.65 + near * 0.25 + ov_score * 0.10
            else:
                score = ov_score * 0.55 + lex * 0.35 + near * 0.10
            if ov < MIN_OVERLAP_MS and near < 0.25 and lex < 0.2:
                continue
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx < 0:
            best_idx = min(
                range(len(turns)),
                key=lambda i: abs(turns[i].start_ms - cue.start_ms),
            )
            best_score = 0.0
            cue.flagged = True
            flagged_ms.append(cue.start_ms)
        elif best_score < WEAK_SCORE:
            if prev_speaker and any(t.speaker == prev_speaker for t in turns):
                contenders = [
                    i
                    for i, t in enumerate(turns)
                    if t.speaker == prev_speaker
                    and (
                        overlap_ms(cue.start_ms, cue.end_ms, t.start_ms, t.end_ms) > 0
                        or abs(t.start_ms - cue.start_ms) <= 2500
                    )
                ]
                if contenders:
                    best_idx = contenders[0]
            # Continuity/best-effort without chat flag; reconstructed TXT gaps are flagged separately
        cue.speaker = turns[best_idx].speaker
        prev_speaker = cue.speaker
    return flagged_ms


def reconstruct_missing_turns(
    cues: list[Cue], turns: list[Turn]
) -> tuple[list[Cue], list[int], list[int]]:
    reconstructed: list[Cue] = []
    flagged_ms: list[int] = []
    epsilon_flags: list[int] = []
    srt_starts = [c.start_ms for c in cues]

    for idx, turn in enumerate(turns):
        window_start = max(0, turn.start_ms - 3000)
        window_end = turn.end_ms + 3000
        nearby = [
            c
            for c in cues
            if overlap_ms(c.start_ms, c.end_ms, window_start, window_end) > 0
            or abs(c.start_ms - turn.start_ms) <= 3000
        ]
        haystack: list[str] = []
        for c in nearby:
            haystack.extend(tokens(c.text))
        recall = token_recall(tokens(turn.text), haystack)
        if recall >= TXT_COVER_RECALL:
            continue

        next_txt = turns[idx + 1].start_ms if idx + 1 < len(turns) else None
        next_srt = None
        for start in srt_starts:
            if start > turn.start_ms:
                next_srt = start
                break
        candidates = [v for v in (next_txt, next_srt) if v is not None]
        if candidates:
            end_ms = min(candidates)
        else:
            end_ms = turn.start_ms + EPSILON_MS
        if end_ms <= turn.start_ms:
            end_ms = turn.start_ms + EPSILON_MS
            epsilon_flags.append(turn.start_ms)
            flagged_ms.append(turn.start_ms)

        reconstructed.append(
            Cue(
                start_ms=turn.start_ms,
                end_ms=end_ms,
                text=turn.text,
                speaker=turn.speaker,
                flagged=True,
                source="txt",
            )
        )
        flagged_ms.append(turn.start_ms)
    return reconstructed, flagged_ms, epsilon_flags


def render_format_b(blocks: list[Cue]) -> str:
    parts: list[str] = []
    for block in blocks:
        speaker = block.speaker or "Unknown"
        parts.append(
            f"[{ms_to_format_b(block.start_ms)} - {ms_to_format_b(block.end_ms)}]\n"
            f"{speaker}\n"
            f"{block.text}\n"
        )
    return "\n".join(parts).rstrip() + "\n"


def format_ts(ms: int) -> str:
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds = rem // 1000
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def undiarized_path_for(srt: Path) -> Path:
    if srt.name.endswith("-raw.srt"):
        return srt.with_name(srt.name.replace("-raw.srt", "-raw-undiaried.srt"))
    return srt.with_name(srt.stem + "-undiaried" + srt.suffix)


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if args.episode is not None:
        nnn = str(int(args.episode))
        base = Path("content/episodes") / nnn
        srt = base / f"{nnn}-raw.srt"
        txt = base / f"{nnn}-raw-diarized.txt"
        out = Path(args.out) if args.out else srt
        return srt, txt, out
    if not args.srt or not args.txt:
        raise SystemExit("Provide --episode or both --srt and --txt")
    srt = Path(args.srt)
    txt = Path(args.txt)
    out = Path(args.out) if args.out else srt
    return srt, txt, out


def promote_format_b(srt_path: Path, out_path: Path, body: str) -> Path | None:
    """Write Format B to out_path. If overwriting the Format A source, preserve it first."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    preserved: Path | None = None
    if out_path.resolve() == srt_path.resolve():
        preserved = undiarized_path_for(srt_path)
        if preserved.exists():
            preserved.unlink()
        srt_path.replace(preserved)
    out_path.write_text(body, encoding="utf-8")
    return preserved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", type=int, help="Episode number (uses content/episodes/NNN/ conventions)")
    parser.add_argument("--srt", help="Path to Format A NNN-raw.srt")
    parser.add_argument("--txt", help="Path to NNN-raw-diarized.txt")
    parser.add_argument(
        "--out",
        help="Output Format B path (default: same as --srt / NNN-raw.srt; Format A preserved as NNN-raw-undiaried.srt)",
    )
    args = parser.parse_args(argv)

    srt_path, txt_path, out_path = resolve_paths(args)

    if not srt_path.is_file():
        print(f"ERROR: missing SRT: {srt_path}", file=sys.stderr)
        return 2
    if not txt_path.is_file():
        print(f"ERROR: missing diarized TXT: {txt_path}", file=sys.stderr)
        return 2

    first = first_non_empty_line(srt_path)
    if FORMAT_B_RE.match(first):
        print(
            f"ERROR: {srt_path} looks like Format B already; prep skill stops.",
            file=sys.stderr,
        )
        return 3

    cues = parse_srt(srt_path)
    turns = parse_txt(txt_path)
    if not cues:
        print(f"ERROR: no Format A cues parsed from {srt_path}", file=sys.stderr)
        return 4
    if not turns:
        print(f"ERROR: no labeled turns parsed from {txt_path}", file=sys.stderr)
        return 4

    fallback_end = max(c.end_ms for c in cues)
    finalize_turn_ends(turns, fallback_end)
    weak_flags = assign_speakers(cues, turns)
    reconstructed, recon_flags, epsilon_flags = reconstruct_missing_turns(cues, turns)

    blocks = list(cues) + reconstructed
    blocks.sort(key=lambda b: (b.start_ms, 0 if b.source == "srt" else 1, b.end_ms))

    preserved = promote_format_b(srt_path, out_path, render_format_b(blocks))

    labels = sorted({t.speaker for t in turns})
    flagged = sorted(set(weak_flags + recon_flags + epsilon_flags))

    print(f"Wrote {out_path}")
    if preserved is not None:
        print(f"Preserved Format A as {preserved}")
    print(f"SRT cues: {len(cues)}")
    print(f"TXT turns: {len(turns)}")
    print(f"Output blocks: {len(blocks)} (reconstructed TXT-only: {len(reconstructed)})")
    print(f"Export labels: {', '.join(labels)}")
    if reconstructed:
        print("Reconstructed starts:")
        for b in reconstructed:
            print(f"  {format_ts(b.start_ms)} {b.speaker}: {b.text[:80]}")
    if flagged:
        print("Flagged timestamps for manual check:")
        print("  " + ", ".join(format_ts(ms) for ms in flagged))
    else:
        print("Flagged timestamps for manual check: none")
    if epsilon_flags:
        print(
            "Epsilon end-time used (end clamped) at: "
            + ", ".join(format_ts(ms) for ms in sorted(set(epsilon_flags)))
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
