import json
from dataclasses import dataclass
from typing import Tuple

import ollama


# @ dataclass is just makes it so the __init__ function is created automatically with some other nice things
# A Section is some general part of the paper like the Title, Abstract, Introduction, Result, Discussion etc.
@dataclass(frozen=True)
class Section:
    name: str
    text: str
    span: Tuple[int, int]  # (start_index, end_index) in the original text
    is_found: bool

    def word_count(self) -> int:
        return len(self.text.split()) if self.is_found else 0

    def character_count(self) -> int:
        return len(self.text)


# a segment is like a sentence or a whole line if the line has no sentence ending.
@dataclass(frozen=True)
class Segment:
    index: int
    text: str
    start: int # position of the first character in the raw text
    end: int # position right after the last character in the raw text
    line_number: int # which line of the raw text the segment is on


# Characters that can end a segment when they are followed by a space or the end of the line.
SEGMENT_ENDINGS = ".!?:"

ABBREVIATIONS = {"al.", "e.g.", "i.e.", "dr.", "fig.", "figs.", "eq.", "vs.", "ref.", "no.", "approx."}

def split_into_segments(raw_text: str) -> list[Segment]:
    """Split the text into numbered segments, one per sentence (and never across a line break)."""
    segments = []
    line_start = 0  # position in raw_text where the current line begins

    for line_number, line in enumerate(raw_text.split("\n")):
        piece_start = 0  # position in the line where the current piece begins

        # For each char in the line
        for i, char in enumerate(line):
            is_last_char = i == len(line) - 1

            # If it isn't a dot or some other symbol that ends a segment we continue
            if char not in SEGMENT_ENDINGS:
                continue

            # If next char isn't a space we don't accept a segment ender like . because likely it is something like 45.3 or e.g
            if not is_last_char and not line[i + 1].isspace():
                continue

            # Something like 'al. ' would still be treated as a segment ender when it isn't one so we make an exception for certain common expressions
            last_word = line[piece_start:i + 1].split()[-1].lower()
            if last_word in ABBREVIATIONS:
                continue

            _add_segment(segments, line, piece_start, i + 1, line_start, line_number)
            piece_start = i + 1

        _add_segment(segments, line, piece_start, len(line), line_start, line_number)
        line_start += len(line) + 1

    return segments


def _add_segment(segments: list[Segment], line: str, start: int, end: int, line_start: int, line_number: int):
    """Add line[start:end] as a segment, without the surrounding whitespace. Empty pieces are skipped."""
    piece = line[start:end]
    text = piece.strip()
    if not text:
        return
    leading_spaces = len(piece) - len(piece.lstrip())
    absolute_start = line_start + start + leading_spaces
    segments.append(Segment(
        index=len(segments),
        text=text,
        start=absolute_start,
        end=absolute_start + len(text),
        line_number=line_number,
    ))


def numbered_text(segments: list[Segment]) -> str:
    """
    Write the segments as "[index] text", keeping the line layout of the original text,
    so the LLM can still see headings, paragraphs and blank lines.
    """
    output = ""
    previous_line = None

    # For each segment. Think of for each sentence
    for segment in segments:

        # If this isn't the first segment
        if previous_line is not None:

            # another segment/sentence on the same line. The two sentences are just separated by a space
            if segment.line_number == previous_line:
                output += " "
            elif segment.line_number == previous_line + 1:
                output += "\n"
            else:
                output += "\n\n"  # one or more blank lines in the original
        output += f"[{segment.index}] {segment.text}"
        previous_line = segment.line_number
    return output


SECTION_FINDER_INSTRUCTIONS = """
You split scientific papers into sections. The paper is given to you as numbered segments: every segment
starts with its number in square brackets, like [12]. Line breaks and blank lines are the same as in the paper.

For each requested section, give the number of its first segment ("start") and its last segment ("end"), inclusive.
Rules:
- Sections do not need to have a heading. Recognise them from their content and position.
- A section can be inside another section (for example a significance statement inside the introduction).
  Then give the range of the inner section only for that section, the outer section may include it.
- If a section is not in the paper, set "found" to false and "start" and "end" to -1.

Respond ONLY with JSON.
"""

# ollama forces llm response to be of this format. Explained in:
# https://docs.ollama.com/capabilities/structured-outputs
def _response_schema(section_names: list[str]) -> dict:
    """JSON schema that forces the LLM to answer with {"<section name>": {"found", "start", "end"}, ...}"""
    one_section = {
        "type": "object",
        "properties": {
            "found": {"type": "boolean"},
            "start": {"type": "integer"},
            "end": {"type": "integer"},
        },
        "required": ["found", "start", "end"],
    }
    return {
        "type": "object",
        "properties": {name: one_section for name in section_names},
        "required": section_names,
    }

def _is_heading(segment: Segment, section_name: str) -> bool:
    starts_with_hashtag = segment.text.startswith("#") and len(segment.text.split()) <= 6
    return starts_with_hashtag

# qwen3:4b
def locate_sections(raw_text: str, section_names: list[str], model: str = "qwen3:4b") -> dict[str, Section]:
    """Ask the llm where each section is, and cut the sections out of the raw text."""
    segments = split_into_segments(raw_text)
    sections = {name: Section(name=name, text="", span=(0, 0), is_found=False) for name in section_names}
    if not segments:
        return sections

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SECTION_FINDER_INSTRUCTIONS},
                {"role": "user", "content": f"Sections to find: {', '.join(section_names)}\n\n{numbered_text(segments)}"},
            ],
            format=_response_schema(section_names),
            options={"temperature": 0},  # we want the same answer every time
            think=False,  # thinking models like qwen3 are very slow without this, and it doesn't help here
        )
        llm_data = json.loads(response["message"]["content"])
    except Exception as e:
        print(f"Error communicating with Ollama or parsing JSON: {e}")
        return sections

    for name in section_names:
        answer = llm_data.get(name)
        if not isinstance(answer, dict) or not answer.get("found"):
            continue
        start, end = answer.get("start"), answer.get("end")
        # The LLM can make mistakes, so only accept numbers that point at real segments
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        if not (0 <= start <= end < len(segments)):
            continue
        # Sometimes the heading like "# Abstract" or "Abstract:" is included. We can manually remove some of these segments from the section manually
        while start < end and _is_heading(segments[start], name):
            start += 1

        span = (segments[start].start, segments[end].end)
        sections[name] = Section(name=name, text=raw_text[span[0]:span[1]], span=span, is_found=True)

    return sections
