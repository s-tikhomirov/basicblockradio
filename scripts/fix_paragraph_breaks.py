#!/usr/bin/env python3
"""
Fix paragraph breaks mid-sentence in transcript files.

Merges consecutive paragraphs from the same speaker when the first paragraph
ends mid-sentence (i.e., doesn't end with a sentence terminator).

Usage:
    python fix_paragraph_breaks.py <input_file> [output_file]

If output_file is not specified, the input file will be overwritten.
"""

import re
import sys
from typing import List, Tuple


def is_sentence_ended(text: str) -> bool:
    """
    Check if text ends with a sentence terminator.
    """
    text = text.rstrip()
    # Sentence terminators: . ! ? ... — (em-dash at end)
    # But not abbreviations like "т.д." or "т.е." or "др."
    if text.endswith('...'):
        return True
    if text.endswith('—') or text.endswith('-'):
        return True
    if text.endswith('.') or text.endswith('!') or text.endswith('?'):
        # Check it's not an abbreviation
        # Common abbreviations in Russian: т.д., т.е., т.п., и.т.д., и.т.п., д.р.
        abbrev_pattern = r'\b(т\.д\.|т\.е\.|т\.п\.|и\.т\.д\.|и\.т\.п\.|д\.р\.|м\.б\.|т\.н\.|н\.э\.|д\.н\.)$'
        if re.search(abbrev_pattern, text, re.IGNORECASE):
            return False
        return True
    return False


def parse_transcript(content: str) -> Tuple[str, List[Tuple[str, str, str]]]:
    """
    Parse transcript into frontmatter and paragraphs.
    Returns (frontmatter, list of (timestamp, speaker, text) tuples).
    """
    # Extract frontmatter
    frontmatter_match = re.match(r'^(---\n.*?\n---\n)', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        body = content[frontmatter_match.end():]
    else:
        frontmatter = ''
        body = content

    # Parse paragraphs
    paragraphs = []
    pattern = r'^\[(\d{2}:\d{2}:\d{2})\] \*\*(.+?)\*\*: (.+)$'

    for line in body.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line)
        if match:
            timestamp = match.group(1)
            speaker = match.group(2)
            text = match.group(3)
            paragraphs.append((timestamp, speaker, text))

    return frontmatter, paragraphs


def merge_paragraphs(paragraphs: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    """
    Merge consecutive paragraphs from the same speaker when the first ends mid-sentence.
    """
    if not paragraphs:
        return paragraphs

    merged = []
    i = 0

    while i < len(paragraphs):
        timestamp, speaker, text = paragraphs[i]

        # Look ahead to see if we should merge with next paragraph(s)
        while (i + 1 < len(paragraphs) and
               paragraphs[i + 1][1] == speaker and  # Same speaker
               not is_sentence_ended(text)):  # Current text ends mid-sentence

            next_timestamp, _, next_text = paragraphs[i + 1]
            # Merge: keep first timestamp, combine text
            text = text + ' ' + next_text
            # Update timestamp to the next one (more recent)
            timestamp = next_timestamp
            i += 1

        merged.append((timestamp, speaker, text))
        i += 1

    return merged


def format_transcript(frontmatter: str, paragraphs: List[Tuple[str, str, str]]) -> str:
    """
    Format transcript back to markdown.
    """
    lines = []
    if frontmatter:
        lines.append(frontmatter.strip())
        lines.append('')

    for timestamp, speaker, text in paragraphs:
        lines.append(f'[{timestamp}] **{speaker}**: {text}')
        lines.append('')

    return '\n'.join(lines)


def fix_paragraph_breaks(input_file: str, output_file: str) -> None:
    """
    Fix paragraph breaks in transcript file.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, paragraphs = parse_transcript(content)
    print(f"Parsed {len(paragraphs)} paragraphs")

    merged = merge_paragraphs(paragraphs)
    print(f"Merged into {len(merged)} paragraphs")

    output = format_transcript(frontmatter, merged)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Transcript fixed and saved to {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_paragraph_breaks.py <input_file> [output_file]")
        print("If output_file is not specified, the input file will be overwritten.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    fix_paragraph_breaks(input_file, output_file)


if __name__ == '__main__':
    main()
