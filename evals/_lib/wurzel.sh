#!/usr/bin/env bash
# Shared scaffold helper: builds a Wurzel in the empty workspace of an eval run from the fictional scenario fixtures
# (tests/fixtures/szenarien). Sourced by the fixture.sh of a case; not a case itself.
#
# The scaffold runs as you with a replaced HOME and a minimal environment: call no tool that lives in your HOME
# (asdf or pyenv shims fail with exit 126). Only coreutils are used here.
#
#   build_wurzel <persona> [<vorgang> <analysis> <cv> [<status>]]
#     persona   erfahren | einsteiger | quereinstieg   (tests/fixtures/szenarien/grundlage/<persona>.md)
#     vorgang   folder name below job-application/ (omit for a Wurzel without a Vorgang)
#     analysis  spezialist | leitung | quereinstieg    (analysen/ and anzeigen/)
#     cv        spezialist | leitung | quereinstieg | einsteiger | none   (cv/<cv>.md)
#     status    value of `status` in vorgang.md (default: erstellt)
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$LIB/../.." && pwd)"
FIX="$REPO/tests/fixtures/szenarien"

build_wurzel() {
  local persona="$1" vorgang="${2:-}" analysis="${3:-}" cv="${4:-none}" status="${5:-erstellt}"
  mkdir -p job-application/grundlage
  cp "$FIX/grundlage/$persona.md" "job-application/grundlage/$persona.md"
  cp "$FIX/grundlage/$persona.md" job-application/profil.md
  cat > job-application/konfiguration.md <<K
---
wurzel: job-application
grundlage: job-application/grundlage/$persona.md
---
K
  # file-mode Grundlage: the grundlage_hash of scripts/grundlage_hash.py is the sha256 of the file (R-9.5)
  HASH="$(sha256sum "job-application/grundlage/$persona.md" | cut -d' ' -f1)"
  export HASH
  [ -n "$vorgang" ] || return 0
  local dir="job-application/$vorgang"
  mkdir -p "$dir"
  cp "$FIX/anzeigen/$analysis.md" "$dir/stellenanzeige.md"
  {
    printf -- '---\nkontaktart: "Direkt: Personalabteilung"\nauftraggeber: unbekannt\nkontakt_konfidenz: gesichert\nexklusiv: unbekannt\n---\n'
    cat "$FIX/analysen/$analysis.md"
    printf '\n## Unternehmen\n\n| Firma | Rolle | Identität | Quelle | Konfidenz | Stand |\n|---|---|---|---|---|---|\n'
    printf '| Musterfirma GmbH | Anstellungsgeber | wahrscheinlich | Anzeige | wahrscheinlich | 2026-10-24 |\n'
  } > "$dir/analyse.md"
  if [ "$cv" != "none" ]; then
    { printf -- '---\ngrundlage_hash: %s\nformat: chronologisch\n---\n\n' "$HASH"; cat "$FIX/cv/$cv.md"; } > "$dir/lebenslauf.md"
  fi
  printf -- '---\nfirma: Musterfirma GmbH\nstelle: Beispielstelle\nref_nr:\nbewerbungsweg: portal\nausrichtung: ausschreibung\nstellenquelle: "Text, eingefügt"\nkontaktart: "Direkt: Personalabteilung"\nstatus: %s\nerfasst: 2026-10-24\ngrundlage_hash: %s\n---\n\n## Plan\n\n## Verlauf\n' "$status" "$HASH" > "$dir/vorgang.md"
}
