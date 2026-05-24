#!/usr/bin/env python3
"""
Merge chunk readable bodies into NNN-readable.md (structure only).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from transcript_io import (
    blocks_to_body,
    load_document,
)

STATUS_LINE_RE = re.compile(r"^\s*status:.*(?:\n|$)", re.MULTILINE | re.IGNORECASE)


def readable_frontmatter_from_transcript(fm: str) -> str:
    if not fm.strip():
        return "---\n---\n"
    cleaned = STATUS_LINE_RE.sub("", fm)
    if not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


def load_blocks_from_chunk(path: Path) -> list:
    doc = load_document(path=path)
    return doc.blocks


def merge_paths(
    chunk_paths: list[Path],
    frontmatter: str,
) -> tuple[str, list, list[str]]:
    all_blocks = []
    warnings: list[str] = []
    prev_seconds: int | None = None

    for path in chunk_paths:
        blocks = load_blocks_from_chunk(path)
        for b in blocks:
            if prev_seconds is not None and b.seconds < prev_seconds:
                warnings.append(
                    f"Non-monotonic timestamp at line {b.line_no} in {path.name}: "
                    f"{b.seconds} < {prev_seconds}"
                )
            prev_seconds = b.seconds
        all_blocks.extend(blocks)

    body = blocks_to_body(all_blocks)
    fm = readable_frontmatter_from_transcript(frontmatter)
    if body and not fm.endswith("\n"):
        out = fm + "\n\n" + body
    elif body:
        out = fm + "\n" + body
    else:
        out = fm + "\n"
    return out, all_blocks, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge ordered chunk readable files into one NNN-readable.md"
    )
    parser.add_argument(
        "chunks",
        nargs="*",
        type=Path,
        help="chunk-001-readable.md ... (or use --chunks-dir)",
    )
    parser.add_argument(
        "--chunks-dir",
        type=Path,
        help="Directory containing chunk-*-readable.md (sorted by name)",
    )
    parser.add_argument(
        "--pattern",
        default="chunk-*-readable.md",
        help="Glob under --chunks-dir (default: chunk-*-readable.md)",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        required=True,
        help="Source NNN-transcript.md for frontmatter template",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output NNN-readable.md path",
    )
    parser.add_argument(
        "--expected-blocks",
        type=int,
        default=None,
        help="Block count from source transcript (default: count from --transcript)",
    )
    parser.add_argument(
        "--min-length-ratio",
        type=float,
        default=0.45,
        help="Warn when readable block length / transcript block length below this",
    )
    parser.add_argument(
        "--qc",
        action="store_true",
        help="Run length-ratio QC against --transcript blocks",
    )
    args = parser.parse_args()

    src = load_document(path=args.transcript)
    expected = args.expected_blocks if args.expected_blocks is not None else src.block_count

    if args.chunks_dir:
        chunk_paths = sorted(args.chunks_dir.glob(args.pattern))
    else:
        chunk_paths = list(args.chunks)

    if not chunk_paths:
        print("error: no chunk files found", file=sys.stderr)
        return 1

    merged, merged_blocks, warnings = merge_paths(
        chunk_paths, src.frontmatter
    )

    if len(merged_blocks) != expected:
        warnings.append(
            f"Block count mismatch: merged {len(merged_blocks)}, expected {expected}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(merged, encoding="utf-8")

    if args.qc:
        if len(merged_blocks) != len(src.blocks):
            warnings.append("QC skipped: merged block count differs from transcript")
        else:
            for i, (src_b, out_b) in enumerate(zip(src.blocks, merged_blocks)):
                if src_b.seconds != out_b.seconds or src_b.speaker != out_b.speaker:
                    warnings.append(
                        f"QC block {i + 1}: timestamp/speaker mismatch vs transcript"
                    )
                src_len = len(src_b.text)
                out_len = len(out_b.text)
                if src_len > 80 and out_len < src_len * args.min_length_ratio:
                    warnings.append(
                        f"Short readable block {i + 1} ({out_b.seconds}s): "
                        f"len {out_len} vs transcript {src_len} "
                        f"(ratio {out_len / src_len:.2f})"
                    )

    report = {
        "output": str(args.output),
        "chunk_files": [str(p) for p in chunk_paths],
        "merged_blocks": len(merged_blocks),
        "expected_blocks": expected,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    return 1 if any("mismatch" in w.lower() for w in warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
