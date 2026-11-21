"""
Text cleaning and normalization module for agricultural documents.

Performs robust text cleaning on raw extracted PDF text:
- Strips repetitive headers, footers, and standalone page numbers.
- Resolves broken line-end hyphenations without corrupting hyphenated terms.
- Normalizes whitespace while preserving semantic paragraph boundaries.
- Preserves Telugu Unicode diacritics and scientific notations (dosages, chemicals, Latin names).
"""

import re
import unicodedata
from typing import List, Optional


class TextCleaner:
    """Cleans and standardizes extracted text from agricultural publications."""

    # Common PDF artifact patterns
    HEADER_FOOTER_PATTERNS = [
        r"^AESA\s+BASED\s+IPM\s+Package.*$",
        r"^AESA\s+based\s+IPM\s+[–-].*$",
        r"^INTEGRATED\s+PEST\s+MANAGEMENT\s+PACKAGE\s+FOR.*$",
        r"^Standard\s+Operating\s+Procedure\s+For\s+Agromet\s+Advisory\s+Services.*$",
        r"^Publication\s+No:\s*MoES/IMD/.*$",
        r"^Directorate\s+of\s+Plant\s+Protection,?\s+Quarantine\s+&?\s+Storage.*$",
        r"^National\s+Institute\s+of\s+Plant\s+Health\s+Management.*$",
        r"^\s*Page\s+\d+\s+of\s+\d+\s*$",
        r"^\s*[-–—]\s*\d+\s*[-–—]\s*$",
        r"^\s*\d+\s*$",  # Standalone page number
        r"^\s*[ivxlcdm]+\s*$",  # Standalone roman numeral
    ]

    def __init__(self, custom_headers: Optional[List[str]] = None):
        """
        Initialize TextCleaner.

        Args:
            custom_headers: Optional regex patterns for document-specific headers/footers.
        """
        patterns = self.HEADER_FOOTER_PATTERNS.copy()
        if custom_headers:
            patterns.extend(custom_headers)
        self.header_footer_regex = [re.compile(p, re.IGNORECASE) for p in patterns]

    def clean_page_text(self, text: str, preserve_telugu: bool = True) -> str:
        """
        Clean raw text extracted from a single PDF page.

        Args:
            text: Raw extracted text from fitz.
            preserve_telugu: If True, preserves Telugu Unicode codepoints (U+0C00 - U+0C7F).

        Returns:
            Cleaned and normalized text.
        """
        if not text:
            return ""

        # 1. Unicode normalization (NFC ensures consistent composite glyphs)
        text = unicodedata.normalize("NFC", text)

        # 2. Split lines and strip known header/footer artifacts
        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                cleaned_lines.append("")
                continue

            # Check if line matches any header/footer pattern
            if any(regex.match(stripped) for regex in self.header_footer_regex):
                continue

            # Remove excessive dots/underscores (e.g. from table of contents)
            if re.match(r"^[\.\_\-\s]{5,}$", stripped):
                continue

            cleaned_lines.append(stripped)

        # Recombine into text
        cleaned_text = "\n".join(cleaned_lines)

        # 3. Resolve broken line-end hyphens: e.g. "culti-\nvation" -> "cultivation"
        # Match word ending with hyphen, newline, and word beginning (English only)
        cleaned_text = re.sub(r"([A-Za-z]{2,})-\n([A-Za-z]{2,})", r"\1\2", cleaned_text)

        # 4. Resolve single line breaks within sentences while preserving paragraphs
        cleaned_text = self._join_broken_sentences(cleaned_text)

        # 5. Normalize multiple spaces while preserving paragraph breaks
        cleaned_text = self._normalize_whitespace(cleaned_text)

        return cleaned_text.strip()

    def _join_broken_sentences(self, text: str) -> str:
        """
        Join lines that are part of the same sentence, keeping double newlines as paragraphs.
        """
        paragraphs = text.split("\n\n")
        joined_paragraphs = []

        for para in paragraphs:
            lines = [l.strip() for l in para.split("\n") if l.strip()]
            if not lines:
                continue

            joined_para = ""
            for i, line in enumerate(lines):
                if i == 0:
                    joined_para = line
                else:
                    # If current line starts with bullet, number, or dash, keep on new line
                    if re.match(r"^([•\-\*–—]|\d+[\.\)])\s+", line):
                        joined_para += "\n" + line
                    # If previous line ends with a period, colon, or question mark, keep break
                    elif joined_para and joined_para[-1] in ".?!:":
                        joined_para += " " + line
                    else:
                        # Otherwise merge with a single space
                        joined_para += " " + line

            joined_paragraphs.append(joined_para)

        return "\n\n".join(joined_paragraphs)

    def _normalize_whitespace(self, text: str) -> str:
        """
        Replace redundant tabs and horizontal spaces with a single space.
        Limit consecutive vertical whitespace to two newlines.
        """
        # Replace non-breaking spaces and tabs
        text = text.replace("\u00a0", " ").replace("\t", " ")

        # Collapse horizontal whitespace
        text = re.sub(r"[ ]{2,}", " ", text)

        # Collapse excessive newlines (max 2 consecutive)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text
