# Auf eine Anzeige bewerben

**Ziel:** von einer konkreten Stellenanzeige zu einer geprüften, versandfertigen Bewerbung, die
in einem eigenen Ordner festgehalten ist.

**Beispiel:** Die Musterfirma GmbH sucht einen *Senior Backend Developer* (Kennzahl 2026-114).
Du bewirbst dich per E-Mail.

## Voraussetzungen

- Plugin installiert und `job-application/konfiguration.md` vorhanden
  ([Erste Schritte](../getting-started.md)).
- Eine Datengrundlage und `profil.md`. Fehlen sie, startet die Eingangstür zuerst
  `job-application-profile-capture`.

## Schritte

### 1. Mit der Anzeige starten

```text
/claude-job-search:job-application-solution
```

Füge auf Nachfrage den Anzeigentext (oder den Link) ein. Der Skill prüft, ob das Profil aktuell
ist, und übergibt die Anzeige an die Analyse.

### 2. Die Analyse lesen

Die Analyse legt den Ordner `musterfirma-senior-backend/` an und hält jede Anforderung mit Beleg
aus deiner Datengrundlage fest:

| Anforderung | Status | Beleg | Offen |
|---|---|---|---|
| 5+ Jahre Java | erfüllt | Station „Beispiel AG, 2019–2025", Stichpunkt 2 | — |
| Kubernetes im Produktivbetrieb | teilweise | ein Projekt, keine Betriebsrolle | produktiver Betrieb |
| Erfahrung in Teamleitung | nicht belegt | kein Eintrag in der Datengrundlage | — |

Außerdem notiert sie den Ton der Anzeige (Sie oder du), die geforderten Unterlagen und die
Gegenpartei (hier: Arbeitgeber direkt, Fachabteilung). Lücken werden nicht überdeckt: *nicht
belegt* bleibt eine Lücke, und der Plan zeigt, wie das Anschreiben ehrlich damit umgeht.

Dieselbe Technologie zu nennen reicht für *erfüllt* nicht. Die Analyse prüft je Anforderung, was sie verlangt (Anwendung
oder Betrieb, eine Komponente oder eine Plattform, Mitarbeit oder Verantwortung, eine Wirkung), gegen die zitierte Stelle
deiner Datengrundlage und schreibt in *Offen*, was die Stelle nicht zeigt. Ist etwas offen, ist die Zeile *teilweise*, und
der Lebenslauf beschreibt die Erfahrung, wie sie ist: „Kubernetes in einem Entwicklungsprojekt eingesetzt“, nicht „die
Plattform betrieben“. Eine andere Formulierung derselben Tätigkeit zählt; ein fehlendes Stichwort ist kein Ablehnungsgrund.
Ob Status und *Offen* zusammenpassen, prüft ein Skript (Regel CV-24); ob die offenen Aspekte richtig erkannt wurden, prüft
der Reviewer. Lies die Spalte *Offen* und korrigiere sie, wenn du mehr weißt, als deine Datengrundlage sagt (und ergänze
das dann in der Datengrundlage).

### 3. Den Plan freigeben

Der Plan nennt die Dokumente und ihr Format, die verwendeten Stationen und Stichpunkte, die
offenen Lücken und die E-Mail als Kanal. Antworte in normalen Worten:

```text
Ja, aber bitte ohne die Station von 2014 im Lebenslauf. Und mit Kurzprofil.
```

Der Skill zeigt den geänderten Plan und wartet auf dein Ja. Erst dann schreibt er die Dokumente.
Der Status wird `geplant`.

### 4. Die Dokumente entstehen der Reihe nach

Lebenslauf, dann Anschreiben (es übernimmt dieselben Stationen, Daten und Zahlen), dann die
E-Mail mit Betreff, kurzem Text, Anlagenliste und ASCII-Dateinamen. Der Status wird `erstellt`.

### 5. Qualitätsprüfung

Die Prüfung meldet Blocker, Warnungen und Hinweise: gleiche Stelle und Kennzahl in allen
Dokumenten, jede Aussage auf die Datengrundlage rückführbar, Rechtschreibung, Seitenzahl,
Anhangsgröße, verbliebene `[ERGÄNZEN]`. Ohne Blocker lautet der Status `geprüft`. Bei Blockern
korrigiert der zuständige Skill das Dokument, danach läuft die Prüfung erneut.

Für eine zweite Meinung nutze den Agenten `job-application-reviewer`. Er liest den gesamten
Satz wie eine Personalerin in der ersten Minute und liefert READY oder NEEDS-WORK; er ändert
nichts.

### 6. Exportieren und versenden

```text
/claude-job-search:job-application-export
```

Wähle PDF (der Standard, auch für Portale). Versende die Mail dann selbst und trage Datum, Kanal
und Anlagen in `vorgang.md` ein; setze den Status `versendet` und ein `wiedervorlage`-Datum.

### 7. Nachfassen

Nach dem Wiedervorlagetermin bittest du um die Mail:

```text
Schreib die Nachfass-Mail für Musterfirma.
```

Der E-Mail-Skill schreibt `email-nachfassen.md` aus den Daten in `vorgang.md`.

## Was in deinem Datenordner bleibt

```text
musterfirma-senior-backend/
├── vorgang.md          Status, Plan, Verlauf
├── stellenanzeige.md   die Anzeige, wörtlich
├── analyse.md          Anforderungsabgleich, Gegenpartei
├── lebenslauf.md
├── anschreiben.md
├── anschreiben-portal.txt nur bei Portal mit Freitextfeld
├── email.md
├── email-nachfassen.md nur auf Wunsch
├── pruefbericht.md     Auswahl und Prüfergebnis
├── notizen.md          nur von dir
└── export/             PDF, nur auf Wunsch
```

## Abwandlungen

- **Portal statt E-Mail:** Sag es im Plan. Es entsteht keine `email.md`; hat das Portal ein
  Freitextfeld für das Anschreiben, schreibt der Anschreiben-Skill zusätzlich
  `anschreiben-portal.txt`.
- **Die Anzeige verlangt ein Motivationsschreiben:** Der Plan nimmt es auf, siehe
  [Initiativbewerbung und Motivationsschreiben](initiative-and-motivation.md).
- **ATS-Portal:** Wähle das Lebenslauf-Format `ats`.
