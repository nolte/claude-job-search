#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../_lib/wurzel.sh"
build_wurzel erfahren musterfirma-plattform spezialist spezialist erstellt
D=job-application/musterfirma-plattform
sed -i 's/^- Docker-Container im Betrieb mitbetreut$/- [ERGÄNZEN: Aufgaben]/' "$D/lebenslauf.md"
printf '## Prüfung\n\nStand: 2026-10-24 · Ergebnis: BEREIT\nGrundlage: %s · Geprüft: lebenslauf.md\n\n### Blocker\n\n### Warnungen\n\n### Hinweise\n' "$HASH" > "$D/pruefbericht.md"
