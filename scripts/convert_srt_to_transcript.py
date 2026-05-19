#!/usr/bin/env python3
"""
Convert SRT transcript to paragraph format with speaker labels.

Usage:
    python convert_srt_to_transcript.py <input_file> [output_file]

If output_file is not specified, the input file will be overwritten.
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class SRTEntry:
    number: int
    start_time: str
    end_time: str
    text: str


def format_timestamp(timestamp: str) -> str:
    """
    Convert SRT timestamp (HH:MM:SS,mmm) to HH:MM:SS format.
    """
    # Remove milliseconds part (comma and 3 digits)
    return re.sub(r',\d{3}$', '', timestamp)


def parse_srt(content: str) -> List[SRTEntry]:
    """Parse SRT content into entries."""
    entries = []

    # Split by double newlines (SRT entries are separated by blank lines)
    blocks = re.split(r'\n\n+', content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue

        # First line is entry number
        try:
            number = int(lines[0].strip())
        except ValueError:
            continue

        # Second line is timestamp
        timestamp_match = re.match(
            r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})',
            lines[1]
        )
        if not timestamp_match:
            continue

        start_time = format_timestamp(timestamp_match.group(1))
        end_time = format_timestamp(timestamp_match.group(2))

        # Remaining lines are text
        text = ' '.join(lines[2:]).strip()

        entries.append(SRTEntry(number, start_time, end_time, text))

    return entries


def identify_speaker(text: str, entry_num: int, context: dict) -> Optional[str]:
    """
    Identify speaker based on text content, entry number, and context.
    Returns speaker name or None if unclear.
    """
    text_lower = text.lower()

    # Introduction - definitely host Александр
    if any(x in text_lower for x in [
        'привет, с вами подкаст',
        'подкаст базовый блок',
        'выпуск номер',
        'в гостях у нас сегодня василий'
    ]):
        return 'Александр Селезнев'

    # Sponsor section - host Александр
    if any(x in text_lower for x in [
        'нас поддерживает',
        'zerion',
        'fluence',
        'gosh',
        '1inch',
        'поблагодарить наших спонсоров'
    ]):
        return 'Александр Селезнев'

    # Guest introduction
    if 'в гостях у нас' in text_lower or 'ко-фаундер проекта lido' in text_lower:
        return 'Александр Селезнев'

    # Closing - host Александр
    if any(x in text_lower for x in [
        'спасибо тебе большое',
        'заканчиваем',
        'всем пока',
        'огромное спасибо нашим слушателям'
    ]):
        return 'Александр Селезнев'

    # Questions that start with interrogative words + ты/вы - likely host
    if text.endswith('?') and len(text) < 250:
        if any(x in text_lower for x in [
            'как ты', 'что ты', 'почему ты',
            'как вы', 'что вы', 'почему',
            'расскажи', 'скажи пожалуйста'
        ]):
            # Check if it's about Lido, staking, DeFi topics - host asking guest
            if any(x in text_lower for x in [
                'lido', 'стейкинг', 'солана',
                'defi', 'governance', 'коммьюнити',
                'протокол', 'вася'
            ]):
                # But if it says "мы" or describes internal decisions, it's guest
                if ('я думаю' not in text_lower and
                    'мы сделали' not in text_lower and
                    'у нас' not in text_lower[:30]):
                    return ('Иван Иваницкий'
                            if 'такой' in text_lower or 'техническ' in text_lower
                            else 'Александр Селезнев')

    # First person statements about Lido internals - guest
    if any(x in text_lower for x in [
        'мы сделали', 'мы запустили', 'мы думали',
        'мы создали', 'наша позиция', 'я считаю',
        'по моему мнению'
    ]):
        if any(x in text_lower for x in [
            'lido', 'стейкинг', 'протокол',
            'коммьюнити', 'модули', 'нод-оператор'
        ]):
            return 'Василий Шаповалов'

    # First person "я" statements with technical depth - guest
    if (text_lower.startswith('я ') and
        any(x in text_lower for x in [
            'lido', 'стейкинг', ' cosmos',
            'токен', 'governance', 'механизм'
        ])):
        if len(text) > 100:  # Longer responses are likely guest
            return 'Василий Шаповалов'

    # Agreement/confirmation responses - could be either, use context
    short_responses = ['да.', 'да, да.', 'точно.', 'правда.',
                       'конечно.', 'согласен.', 'да-да.', 'хорошо.']
    if text_lower in short_responses:
        return context.get('previous_speaker', 'Александр Селезнев')

    # Technical deep dive statements - guest
    if any(x in text_lower for x in [
        'механизм', 'протокол', 'контракт',
        'смарт-контракт', 'валидация', 'делегация', 'транзакция'
    ]):
        if 'я ' in text_lower or 'мы ' in text_lower:
            return 'Василий Шаповалов'

    # "Привет-привет" response - guest answering
    if 'привет-привет' in text_lower:
        return 'Василий Шаповалов'

    # Statements about market share, numbers, statistics about Lido - guest
    if any(x in text_lower for x in [
        'market share', 'миллиард', 'процент',
        'доля рынка', 'токенов', 'эмиссия'
    ]):
        if any(x in text_lower for x in ['у нас', 'мы ', 'lido ', 'стейкинга ']):
            return 'Василий Шаповалов'

    return None


def consolidate_entries(entries: List[SRTEntry]) -> List[Tuple[str, str, str]]:
    """
    Consolidate SRT entries into paragraphs with speaker labels.
    Returns list of (timestamp, speaker, text) tuples.
    """
    paragraphs = []
    current_speaker = None
    current_text = []
    current_start = None

    context = {'previous_speaker': None}

    for i, entry in enumerate(entries):
        # Identify speaker for this entry
        speaker = identify_speaker(entry.text, entry.number, context)

        # If speaker unclear, try to infer from context
        if speaker is None:
            # Check if it looks like a continuation
            if current_speaker:
                # If short response, likely same speaker
                if len(entry.text) < 50:
                    speaker = current_speaker
                else:
                    # Longer text - might be speaker change
                    # Use heuristics based on content
                    text_lower = entry.text.lower()

                    # If talking about Lido with "мы" or "я" - likely guest
                    if (any(x in text_lower for x in [
                        'мы сделали', 'я думаю', 'по моему',
                        'наша компания', 'я считаю'
                    ]) and 'lido' in text_lower):
                        speaker = 'Василий Шаповалов'
                    # If asking question - likely host
                    elif entry.text.endswith('?'):
                        speaker = ('Иван Иваницкий'
                                   if context.get('previous_speaker') == 'Александр Селезнев'
                                   else 'Александр Селезнев')
                    else:
                        speaker = current_speaker
            else:
                speaker = 'Александр Селезнев'  # Default to host

        # If speaker changed or text is getting long, start new paragraph
        text_ended = (entry.text.endswith(('.', '!', '?', '...', '—')) or
                      len(entry.text) > 100)

        if (speaker != current_speaker or
            (text_ended and len(' '.join(current_text)) > 200) or
            len(' '.join(current_text)) > 400):

            if current_text and current_speaker:
                paragraphs.append(
                    (current_start, current_speaker, ' '.join(current_text))
                )

            current_speaker = speaker
            current_start = entry.start_time
            current_text = [entry.text]
        else:
            current_text.append(entry.text)

        context['previous_speaker'] = speaker

    # Add final paragraph
    if current_text and current_speaker:
        paragraphs.append((current_start, current_speaker, ' '.join(current_text)))

    return paragraphs


def format_paragraphs(paragraphs: List[Tuple[str, str, str]], frontmatter: str) -> str:
    """Format paragraphs into final transcript format."""
    result_lines = []

    # Clean up frontmatter - remove trailing --- if present
    frontmatter = frontmatter.strip()
    if frontmatter.endswith('---'):
        frontmatter = frontmatter[:-3].strip()

    result_lines.append(frontmatter)
    result_lines.append('status: edited')
    result_lines.append('---')
    result_lines.append('')

    for timestamp, speaker, text in paragraphs:
        # Clean up text
        text = text.strip()
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove separator lines
        text = re.sub(r'-{3,}', '', text)

        if text:
            result_lines.append(f'[{timestamp}] **{speaker}**: {text}')
            result_lines.append('')

    return '\n'.join(result_lines)


def convert_transcript(input_file: str, output_file: str) -> None:
    """
    Convert an SRT transcript file to paragraph format.

    Args:
        input_file: Path to input SRT/transcript file
        output_file: Path to output file
    """
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter_match = re.match(r'^(---\n.*?\n---)', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        transcript_content = content[frontmatter_match.end():]
    else:
        frontmatter = '---\nepisode_number:\nrecording_date:\npublication_date:\nguest:\n'
        transcript_content = content

    # Remove separator lines
    transcript_content = re.sub(r'^-+$', '', transcript_content, flags=re.MULTILINE)
    transcript_content = transcript_content.strip()

    # Parse SRT
    entries = parse_srt(transcript_content)
    print(f"Parsed {len(entries)} SRT entries")

    # Consolidate into paragraphs
    paragraphs = consolidate_entries(entries)
    print(f"Consolidated into {len(paragraphs)} paragraphs")

    # Format output
    output = format_paragraphs(paragraphs, frontmatter)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Transcript converted and saved to {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_srt_to_transcript.py <input_file> [output_file]")
        print("If output_file is not specified, the input file will be overwritten.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    convert_transcript(input_file, output_file)


if __name__ == '__main__':
    main()
