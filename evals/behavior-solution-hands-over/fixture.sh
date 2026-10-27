#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../_lib/wurzel.sh"
build_wurzel erfahren musterfirma-beispielstelle spezialist spezialist versendet
# the sent application carries its dispatch data (KK-5), so the Vorgang is not flagged as incomplete
sed -i 's/^status: versendet$/status: versendet\nversendet_am: 2026-10-26\nweg: portal/' job-application/musterfirma-beispielstelle/vorgang.md
