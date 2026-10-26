#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../_lib/wurzel.sh"
build_wurzel erfahren musterfirma-plattform leitung leitung erstellt
cp "$FIX/briefe/leitung.md" job-application/musterfirma-plattform/anschreiben.md
