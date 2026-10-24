#!/usr/bin/env python3
"""Clean and check the Anzeigen-URL of a posting intake (spec stellenanzeige-url UE-2 rules 3 and 5).

Usage: posting_url.py <url>

Prints a JSON object with `url` (the input), `bereinigt` (the cleaned URL that is requested and stored)
and `grund` (empty when the URL may be requested, otherwise the reason it is refused). The exit code is 0
when the URL may be requested and 3 when it is refused. The check sees only the typed host: a public name
that resolves to a private address is caught only by the fetch tool (UE-2 rule 5).
Standard library only.
"""

import ipaddress
import json
import socket
import sys
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

TRACKING_EXACT = {"fbclid", "gclid", "trk"}
TRACKING_PREFIXES = ("utm_", "mc_")

REFUSED_SCHEME = "Kein http(s)-Link"
REFUSED_LINKEDIN = "LinkedIn wird nie abgerufen (RC-5.4 Regel 6): Text einfügen oder LinkedIn-Server nutzen"
REFUSED_INTERNAL = "Interne Adresse (RC-5.2 Regel 9)"


def clean(url):
    """Drop tracking parameters; keep the URL as given when nothing identifying would remain."""
    parts = urlsplit(url)
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    kept = [
        (key, value)
        for key, value in pairs
        if key.lower() not in TRACKING_EXACT and not key.lower().startswith(TRACKING_PREFIXES)
    ]
    if len(kept) == len(pairs):
        return url
    if parts.path in ("", "/") and not kept:
        return url
    query = urlencode(kept, quote_via=quote)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def numeric_address(host):
    """Return the IP address a host spells out, in any form inet_aton accepts, else None."""
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        pass
    try:
        return ipaddress.ip_address(socket.inet_aton(host))
    except (OSError, ValueError):
        return None


def refusal(url):
    """Return the reason the typed URL is refused before any request, or an empty string."""
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").rstrip(".").lower()
    except ValueError:
        return REFUSED_SCHEME
    if parts.scheme.lower() not in ("http", "https") or not host:
        return REFUSED_SCHEME
    if host == "linkedin.com" or host.endswith(".linkedin.com"):
        return REFUSED_LINKEDIN
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        return REFUSED_INTERNAL
    address = numeric_address(host)
    if address is not None and not address.is_global:
        return REFUSED_INTERNAL
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
