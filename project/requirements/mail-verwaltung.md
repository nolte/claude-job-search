---
title: Mail-Verwaltung für Bewerbungen (Gmail, Kalender, Vault)
status: elicited; Spec entworfen (spec/job-application/mail-verwaltung/en.md, PR #26)
created: 2026-10-23
---

# Anforderung: Mail-Verwaltung für Bewerbungen

<!--
Erzeugt mit dem Skill `requirements-elicit` nach spec/project/requirements-elicitation/.
`c_d` ist ein Unsicherheits-Proxy, keine kalibrierte Wahrscheinlichkeit.
Eine Anforderung ist `confirmed` nur nach ausdrücklichem Teach-back.
-->

## Bounded context

- **Gebaut wird:** eine Spec `spec/job-application/mail-verwaltung/en.md`, die beschreibt, wie der Skill das Google-Mail-Konto des Nutzers für Bewerbungen verwaltet: sortieren und labeln, optional Kalendereinträge vorschlagen, Informationen in den lokalen Vault übernehmen, Mails bestehenden Vorgängen zuordnen, auf Wunsch Antworten vorschlagen.
- **Für wen:** den Bewerber bzw. die Bewerberin im eigenen Google-Konto.
- **Nicht Teil davon:** Löschen, Archivieren, Spam-Melden, Versenden, Research zu Unternehmen oder Personen, fremde oder mehrere Konten, Ändern bestehender Kalendereinträge, Antwortentwürfe in Gmail.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, Self-Consistency `k = 2`, Fragenbudget = 15 (Spec-Defaults)
- `U_gate = min_d c_d` = **0.7**
- Termination: `question-budget-capped` (14 Fragen plus Gesamt-Teach-back). Zellen unter `τ_high` stehen unten als Restrisiko.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | interpretation | Gesamt-Teach-back bestätigt; Ablauf Schritt 1–7 |
| `non_functional` | yes | 0.7 | specification | Abbruch bei Fehler bestätigt; Datenschutzgrenzen teils `assumed`; keine Leistungsziele erhoben |
| `constraints` | yes | 0.85 | interpretation | Connector (MCP), nur auf Anforderung, Freigabe für Kalender und Vault |
| `domain_objects` | yes | 0.85 | interpretation | Vorgang, Firma, Label-Hierarchie; Begriffe gegen `lokale-struktur` und `kontaktklassifikation` gelesen, Vault-Ziel (Zeile in `## Verlauf`) vom Nutzer bestätigt |
| `actors` | yes | 0.85 | interpretation | Ein Nutzer, ein Konto; Teach-back |
| `acceptance_criteria` | yes | 0.75 | specification | Probe mit erfundenen Mails bestätigt; Mengen und Schwellen offen |
| `edge_cases` | yes | 0.8 | interpretation | Ohne Vorgang, Konflikt, manuelle Umsortierung, unklarer Termin, Connector-Ausfall |
| `scope_boundaries` | yes | 0.9 | interpretation | Nicht-Ziele Punkt für Punkt bestätigt; Antwortvorschläge ausdrücklich ergänzt |

## Requirements

- **R1** — WHEN der Nutzer die Mailverwaltung aufruft, the Skill SHALL `unsort` abarbeiten, und nur dann. Es gibt keinen Schedule und keinen Start bei Sitzungsbeginn.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: "1" (nur auf Anforderung)
- **R2** — WHEN eine Mail in `unsort` liegt, the Skill SHALL ihre Relevanz per grober Analyse (Absender, Betreff, Mailanfang) bestimmen und dabei keinen Research durchführen.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "eine grobe analyse ist ok, aber es soll noch kein research passieren"
- **R3** — WHEN eine Mail als nicht zur Bewerbung gehörig eingestuft ist, the Skill SHALL sie weder inhaltlich analysieren noch in den Vault aufnehmen, und SHALL sie in `unsort` unverändert lassen.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "4" (Datenschutz-Auswahl); Rest der Aussage: Teach-back. Der Verbleib in `unsort` ist `assumed`, siehe Risiken.
- **R4** — WHEN eine Mail als relevant gilt, the Skill SHALL sie analysieren und in die Label-Struktur verschieben, die der Nutzer festgelegt hat.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "wenn emails als relevant identifiziert wurden dürfen sie analysiert werden und werden in passende unterstrukturen verschoben"
- **R5** — The Skill SHALL ohne Nutzerregeln einen Vorschlag für die Label-Struktur anbieten: Eingang `unsort`, darunter `Bewerbung/<Vorgang>/<Mailtyp>` mit den Mailtypen Eingangsbestätigung, Einladung, Absage, Zusage, Rückfrage; im Spec-Review ergänzt: Angebot (Status `angebot`). Das Regelwerk dahinter bestimmt der Nutzer selbst.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: "das jeweilige regelwerk soll der nutzer möglichst selber bestimmen, trotzdem soll es einen vorschlag für eine label und ordnerstruktur geben"; "Vorgang außen, Mailtyp innen"
- **R6** — WHEN eine relevante Mail zugeordnet wird, the Skill SHALL die Merkmale in dieser Rangfolge prüfen: Referenznummer der Stellenanzeige, Firmenname oder Stellentitel, Absender. Der Gmail-Thread SHALL nur als Zusatzsignal dienen.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "ich denke 4,3,2"; "1 als Zusatzsignal"
- **R7** — WHEN eine relevante Mail keinem Vorgang zugeordnet werden kann, OR WHEN zwei Merkmale auf verschiedene Vorgänge zeigen, the Skill SHALL sie nach `Bewerbung/_ohne Vorgang` verschieben und, bei Konflikt, den Konflikt melden. Der Skill SHALL nie selbst einen Vorgang anlegen.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: "3"; "bei Konflikt b"
- **R8** — WHEN der Skill Labels setzt oder Mails verschiebt, the Skill SHALL das ohne Rückfrage tun.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: "2, Kalender und Vault immer mit Freigabe"
- **R9** — WHEN der Skill Informationen in den Vault schreiben will, the Skill SHALL vorher die Freigabe des Nutzers einholen, und SHALL nur Metadaten (Datum, Absender, Mailtyp, Betreff, Gmail-Message-ID, Thread-ID) plus eine kurze Zusammenfassung in eigenen Worten schreiben, keinen Volltext.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "2"; "2, Kalender und Vault immer mit Freigabe"
- **R10** — WHEN eine relevante Mail einen Termin oder eine Frist enthält, the Skill SHALL einen Eintrag im Kalender „Bewerbungen" vorschlagen und ihn erst nach Freigabe anlegen. Bei fehlenden Angaben (z. B. Uhrzeit, Zeitzone) SHALL der Skill nicht raten, sondern nachfragen oder keinen Eintrag anlegen. Nachfasstermine gehören nicht dazu. Fehlt der Kalender, SHALL der Skill ihn nicht selbst anlegen, sondern melden.
  - _dimension_: `functional` · _status_: `confirmed` (Nachfasstermine, Fehlbehandlung des Kalenders: `assumed`) · _source_: "2, eigener Kalender „Bewerbungen""
- **R11** — WHEN der Nutzer eine Mail manuell in ein anderes Label verschoben hat (Entscheidung im Review: nur Mails mit `unsort` gehören dem Skill, alles andere gilt als erledigt), the Skill SHALL sie nie überschreiben, und SHALL aus der Korrektur einen Regelvorschlag ableiten, der nur mit Freigabe gilt.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: "2"
- **R12** — WHERE der Nutzer es verlangt, the Skill SHALL einen Antwortvorschlag als Text in der Sitzung erzeugen, ohne Gmail-Entwurf und ohne Senden. Der Vorschlag SHALL sich auf Fakten aus Datengrundlage und Vorgang stützen und Unbekanntes als `[ERGÄNZEN: …]` markieren.
  - _dimension_: `functional` · _status_: `confirmed` (Faktenbasis und `[ERGÄNZEN]`: `assumed`) · _source_: "ich denke auf wunsch sollten auch passende antwortvorschläge erzeugt werden"; "1"
- **R13** — The Skill SHALL über den Google-Connector (MCP) auf Gmail und Kalender zugreifen und keine eigene OAuth-Anbindung verwalten. Die Spec SHALL festlegen, welche Connector-Funktionen genutzt werden dürfen.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: "1, Connector nutzen"
- **R14** — The Skill SHALL nie Mails löschen, archivieren oder als Spam melden, nie senden, kein Research betreiben, nur ein Konto bedienen und bestehende Kalendereinträge nicht ändern.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Nicht-Ziele-Liste, bestätigt im Gesamt-Teach-back ("ja, passt so")
- **R15** — WHEN der Connector ausfällt oder Rechte fehlen, the Skill SHALL den Lauf abbrechen und den Fehler melden.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: "bei Fehler abbrechen". Ob bereits ausgeführte Änderungen erhalten bleiben (Labeln ist reversibel), ist `assumed`.
- **R16** — The Spec SHALL als Abnahme eine Probe mit erfundenen Mails vorsehen: Jede Mail landet im erwarteten Label, und es wird nichts gelöscht. Echte Mails und Personen sind in Fixtures ausgeschlossen.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: "Probe mit erfundenen Mails"; Plan-Invariante "Fictional examples only"

## Surviving assumptions / open risks

- **Aufgelöst (2026-10-23):** Die Annahme „Anhänge, Gehalt, private Kontaktdaten dürfen in die Zusammenfassung" ist **verworfen**. Der Nutzer hat die engere Fassung bestätigt: keine Gehalts- und Vertragsangaben, keine privaten Kontaktdaten, Anhänge nur als Vermerk. Ebenso bestätigt: Vault-Ziel ist eine Zeile in `## Verlauf` von `vorgang.md`, Statuswechsel nur als Vorschlag mit Freigabe (`mail-verwaltung/en.md` MV-7).
- **`assumed`: Nicht relevante Mails bleiben in `unsort` unverändert** (R3). Das wurde nicht ausdrücklich gefragt.
- **`assumed`: Antwortvorschlag stützt sich auf Fakten und markiert Lücken mit `[ERGÄNZEN]`** (R12).
- **`assumed`: Fehlender Kalender wird gemeldet, nicht angelegt** (R10), und **bei Abbruch bleiben bereits ausgeführte, reversible Label-Änderungen bestehen** (R15).
- **Gegenlesen gegen `lokale-struktur` (LS) und `kontaktklassifikation` (KK) hat Spannungen gezeigt:**
  - LS-6 Regel 4 und 7: Kein Skill setzt S7/S8 (Versand, Nachverfolgung), und ein Skill „infers a reply" nie. Die Mailverwaltung ist faktisch die offene Nachverfolgung (LS-10). Lösungsansatz: Status- und Verlauf-Änderungen nur als Vorschlag mit Freigabe (R9), und LS-6 Regel 7 sowie LS-10 werden in der Spec angepasst.
  - Die `assumed`-Annahme zu Gehalt und privaten Kontaktdaten kollidiert mit KK-4.4, LS-6 Regel 8 und LS-9.6: Kontaktpersonen-Daten werden bei Endstatus entfernt, und Gehalt wird nur geteilt, wenn gefragt. Die Annahme ist damit **nicht tragfähig** und wird in der Spec enger gefasst, sofern der Nutzer nichts anderes entscheidet.
  - Vault-Ziel: Der „Vault" ist die Wurzel (LS-2, LS-8). Naheliegend ist eine Zeile in `## Verlauf` von `vorgang.md` (Datum plus Kurzbeschreibung, LS-6 Regel 1). Ein neues Dateiformat pro Mail wäre eine Änderung von LS-3.
  - `notizen.md` und der Body von `firmen/` bleiben tabu (LS-5.6). Kontaktart-Signale aus Mails nutzen KK-3.1.
- **Begriffe:** Wurzel, Anker, Vorgang, Firma kommen aus `lokale-struktur`. Die Specs liegen auf `develop`, nicht auf `main`. Der Branch ist per Fast-Forward auf `origin/develop` gezogen. `domain_objects` steht nach der bestätigten Vault-Entscheidung bei 0.85.
- **Offen:** Vault-Ordner und Dateiformat pro Mail, und ob das Regelwerk als Datei, per Interview oder beides gepflegt wird. Der Nutzer hat nur den Standardvorschlag und die Hoheit über die Regeln festgelegt.
- **Offen:** Welche Connector-Funktionen für Gmail und Kalender in der Umgebung tatsächlich vorhanden sind (insbesondere Labels ändern). In dieser Sitzung ist nur der Google-Drive-Connector gelistet. Das muss vor der Spec geprüft werden.
- **Offen:** Leistungs- und Mengenziele (z. B. Mails pro Lauf) wurden nicht erhoben.
