#!/usr/bin/env python3
"""
Split NNN-transcript.md into mechanical chunks for pass 2 (transcript-to-readable).
Structure only — no Russian text transformation.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from transcript_io import (
    Block,
    TranscriptDocument,
    format_timestamp,
    load_document,
    write_chunk_body,
)


@dataclass
class ChunkPlan:
    chunk_id: int
    start_block_index: int  # 0-based in blocks list
    end_block_index: int  # inclusive
    start_line: int
    end_line: int
    first_timestamp: str
    last_timestamp: str
    block_count: int
    span_seconds: int


def chunk_span_seconds(blocks: list[Block]) -> int:
    if not blocks:
        return 0
    return blocks[-1].seconds - blocks[0].seconds


def find_speaker_split_index(blocks: list[Block], min_blocks: int = 5) -> int | None:
    """Index of last block in chunk (inclusive) where next block changes speaker, if any."""
    if len(blocks) < min_blocks + 1:
        return None
    for i in range(len(blocks) - 2, min_blocks - 2, -1):
        if blocks[i].speaker != blocks[i + 1].speaker:
            return i
    return None


def plan_chunks(
    doc: TranscriptDocument,
    max_blocks: int,
    max_span_seconds: int | None,
    min_chunk_blocks: int = 5,
) -> list[ChunkPlan]:
    blocks = doc.blocks
    if not blocks:
        return []

    plans: list[ChunkPlan] = []
    start = 0
    chunk_id = 0

    while start < len(blocks):
        chunk_id += 1
        end = start
        while end < len(blocks):
            candidate = blocks[start : end + 1]
            count = len(candidate)
            span = chunk_span_seconds(candidate)
            over_blocks = count >= max_blocks
            over_span = (
                max_span_seconds is not None
                and count > 1
                and span >= max_span_seconds
            )
            if not over_blocks and not over_span:
                end += 1
                continue
            if count == 1:
                end += 1
                break
            break

        if end >= len(blocks):
            slice_blocks = blocks[start:]
            cut_end = len(blocks) - 1
        else:
            slice_blocks = blocks[start:end]
            cut_end = end - 1
            if len(slice_blocks) >= min_chunk_blocks:
                split_at = find_speaker_split_index(slice_blocks, min_chunk_blocks)
                if split_at is not None:
                    cut_end = start + split_at

        chunk_blocks = blocks[start : cut_end + 1]
        plans.append(
            ChunkPlan(
                chunk_id=chunk_id,
                start_block_index=start,
                end_block_index=cut_end,
                start_line=chunk_blocks[0].line_no,
                end_line=chunk_blocks[-1].line_no,
                first_timestamp=format_timestamp(chunk_blocks[0].seconds),
                last_timestamp=format_timestamp(chunk_blocks[-1].seconds),
                block_count=len(chunk_blocks),
                span_seconds=chunk_span_seconds(chunk_blocks),
            )
        )
        start = cut_end + 1

    return plans


def default_chunks_dir(transcript_path: Path) -> Path:
    return transcript_path.parent / ".chunks"


def write_chunk_files(
    doc: TranscriptDocument,
    plans: list[ChunkPlan],
    out_dir: Path,
    prefix: str,
) -> list[Path]:
    paths: list[Path] = []
    for plan in plans:
        chunk_blocks = doc.blocks[plan.start_block_index : plan.end_block_index + 1]
        name = f"{prefix}-{plan.chunk_id:03d}.md"
        path = out_dir / name
        write_chunk_body(path, chunk_blocks)
        paths.append(path)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split a transcript into fixed-size chunks (between timestamp lines only)."
    )
    parser.add_argument(
        "transcript",
        nargs="?",
        type=Path,
        help="Path to NNN-transcript.md (omit to read stdin)",
    )
    parser.add_argument(
        "--max-blocks",
        type=int,
        default=22,
        help="Maximum blocks per chunk (default: 22); secondary to --max-span-seconds",
    )
    parser.add_argument(
        "--max-span-seconds",
        type=int,
        default=900,
        help="Wall-clock span from first to last block timestamp in chunk (default: 900 = 15 minutes)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory for chunk-NNN.md files (default: episodes/NNN/.chunks/)",
    )
    parser.add_argument(
        "--prefix",
        default="chunk",
        help="Filename prefix for chunks (default: chunk → chunk-001.md)",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Print JSON manifest to stdout; do not write chunk files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary and manifest; do not write chunk files",
    )
    args = parser.parse_args()

    if args.transcript:
        doc = load_document(path=args.transcript)
        transcript_path = args.transcript.resolve()
    else:
        doc = load_document(stream=sys.stdin)
        transcript_path = None

    plans = plan_chunks(doc, args.max_blocks, args.max_span_seconds)
    manifest = {
        "block_count": doc.block_count,
        "span_seconds": doc.span_seconds,
        "max_blocks": args.max_blocks,
        "max_span_seconds": args.max_span_seconds,
        "chunk_count": len(plans),
        "chunks": [asdict(p) for p in plans],
    }

    if args.dry_run or args.manifest_only:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        if args.dry_run and not args.manifest_only:
            print(
                f"# {doc.block_count} blocks, span {doc.span_seconds}s, "
                f"{len(plans)} chunks",
                file=sys.stderr,
            )
        return 0

    if transcript_path is None:
        print("error: writing chunk files requires a transcript path", file=sys.stderr)
        return 1

    out_dir = args.out_dir or default_chunks_dir(transcript_path)
    paths = write_chunk_files(doc, plans, out_dir, args.prefix)
    manifest["out_dir"] = str(out_dir)
    manifest["files"] = [str(p) for p in paths]
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
