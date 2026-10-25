"""Patterns for personal data that must not stand in a fixture of this public repository.

Fixtures use reserved domains (`example.test`, `example.com`), the telephone prefix 00000 and invented names. A
pattern here fires on a real-looking e-mail address, a telephone number in national or international form, an IBAN
and a profile URL of a career network. Names and street addresses cannot be recognised by a pattern; they stay a
matter of review (CLAUDE.md, "Fictional examples only")."""

import re

PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@(?!(?:[A-Za-z0-9-]+\.)*(?:example\.(?:test|com|org|net)|[A-Za-z0-9-]+\.(?:test|invalid|example))(?![A-Za-z0-9.-]))[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "international telephone number": r"(?<![0-9A-Za-z])(?:\+|00)(?!0{3,})\d{1,3}[ /.-]?\(?\d{1,5}\)?[ /.-]?\d{3,}",
    "national telephone number": r"(?<![0-9A-Za-z/.-])\(?0(?!0{4}\b)\d{2,5}\)?[ /.-]?\d{4,}(?![0-9A-Za-z])",
    "IBAN": r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}\b|\bDE\d{20}\b",
    "profile URL": r"(?:linkedin|xing)\.com/(?:in|profile|profiles)/(?!muster|beispiel)",
}


def findings(text):
    """[(kind, matched text)] for every pattern hit in `text`."""
    text = re.sub(r"\b[0-9a-fA-F]{32,}\b", " ", text)  # a hash is no number
    return [(kind, match.group(0)) for kind, pattern in PATTERNS.items() for match in re.finditer(pattern, text)]
