#!/usr/bin/env python3
"""Clean and check the Anzeigen-URL of a posting intake (spec stellenanzeige-url UE-2 rules 3, 5 and 6).

Usage: posting_url.py <url>

Prints a JSON object with `url` (the input), `bereinigt` (the cleaned URL that is requested and stored)
and `grund` (empty when the URL may be requested, otherwise the reason it is refused). The exit code is 0
when the URL may be requested and 3 when it is refused. The check sees only the typed host and path: a public name
that resolves to a private address is caught only by the fetch tool (UE-2 rule 5).
Standard library only.
"""

import ipaddress
import json
import re
import sys
from urllib.parse import unquote, urlsplit, urlunsplit

TRACKING_EXACT = {"fbclid", "gclid", "trk"}
TRACKING_PREFIXES = ("utm_", "mc_")

LINKEDIN_DOMAINS = ("linkedin.com", "linkedin.cn", "lnkd.in")
FILE_EXTENSIONS = (".pdf", ".doc", ".docx", ".odt", ".rtf", ".zip")

REFUSED_SCHEME = "Kein http(s)-Link"
REFUSED_LINKEDIN = "LinkedIn wird nie abgerufen (RC-5.4 Regel 6): Text einfügen oder LinkedIn-Server nutzen"
REFUSED_INTERNAL = "Interne Adresse (RC-5.2 Regel 9)"
REFUSED_FILE = "Dateidownload wird nicht geladen (UE-2 Regel 6): Text einfügen oder lokale Datei nennen"

NUMBER_PART = re.compile(r"0x[0-9a-f]+|[0-9]+", re.I)


def clean(url):
    """Drop tracking parameters; keep the URL as given when nothing identifying would remain.

    The query is filtered as raw text, so the parameters that stay keep their exact bytes.
    """
    parts = urlsplit(url)
    segments = parts.query.split("&") if parts.query else []

    def tracking(segment):
        key = unquote(segment.split("=", 1)[0].replace("+", " ")).lower()
        return key in TRACKING_EXACT or key.startswith(TRACKING_PREFIXES)

    kept = [segment for segment in segments if not tracking(segment)]
    if len(kept) == len(segments):
        return url
    if parts.path in ("", "/") and not kept:
        return url
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "&".join(kept), parts.fragment))


def numeric_address(host):
    """Return the IP address a host spells out (IPv6, or IPv4 in decimal, octal or hex parts), else None."""
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        pass
    parts = host.split(".")
    if not 1 <= len(parts) <= 4 or not all(NUMBER_PART.fullmatch(part) for part in parts):
        return None
    try:
        numbers = [int(part, 0) if part.lower().startswith("0x") else int(part, 8 if part.startswith("0") else 10)
                   for part in parts]
    except ValueError:
        return None
    # inet_aton rule: the last part fills the remaining bytes
    if any(number > 255 for number in numbers[:-1]) or numbers[-1] >= 256 ** (5 - len(numbers)):
        return None
    value = 0
    for number in numbers[:-1]:
        value = value * 256 + number
    value = value * 256 ** (5 - len(numbers)) + numbers[-1]
    return ipaddress.ip_address(value)


def refusal(url):
    """Return the reason the typed URL is refused before any request, or an empty string."""
    try:
        parts = urlsplit(url)
        host = unquote(parts.hostname or "").rstrip(".").lower()
    except ValueError:
        return REFUSED_SCHEME
    if parts.scheme.lower() not in ("http", "https") or not host:
        return REFUSED_SCHEME
    if "%" in host:
        return REFUSED_INTERNAL
    if any(host == domain or host.endswith("." + domain) for domain in LINKEDIN_DOMAINS):
        return REFUSED_LINKEDIN
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        return REFUSED_INTERNAL
    address = numeric_address(host)
    if address is not None and not address.is_global:
        return REFUSED_INTERNAL
    if unquote(parts.path).lower().endswith(FILE_EXTENSIONS):
        return REFUSED_FILE
    return ""


def main(argv):
    if len(argv) != 2:
        print("Usage: posting_url.py <url>", file=sys.stderr)
        return 2
    url = argv[1].strip()
    reason = refusal(url)
    result = {"url": url, "bereinigt": "" if reason else clean(url), "grund": reason}
    print(json.dumps(result, ensure_ascii=False))
    return 3 if reason else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
