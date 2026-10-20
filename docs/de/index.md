# claude-job-search

Claude-Code-Plugin mit Skills und einem Agenten für Bewerbungsunterlagen im
deutschsprachigen Raum: tabellarischer Lebenslauf, DIN-5008-Anschreiben,
Bewerbungs-E-Mail, Abgleich der Anforderungen mit der Stellenanzeige und eine
Qualitätsprüfung vor dem Versand.

## Überblick

Du beschreibst eine **Stellenanzeige**. Der Einstieg `bewerbung-solution` prüft dein
Profil, analysiert die Anzeige, zeigt dir einen Plan und erstellt erst danach die
Unterlagen in der richtigen Reihenfolge. Alle Fakten stammen aus einer lokalen
Profildatei, `bewerbung/profil.md`. Fehlende Angaben werden markiert, nie erfunden.

## Einstieg

- `/claude-job-search:bewerbung-solution` mit dem Text der Stellenanzeige für eine komplette Bewerbung.
- `/claude-job-search:bewerbung-profil-erfassen`, wenn noch kein Profil existiert.
- `/claude-job-search:bewerbung-pruefen` vor dem Versand eines vorhandenen Ordners.

Die Konventionen stehen in der Spezifikation `spec/bewerbung/konventionen/en.md`
(kanonisch auf Englisch, deutsche Übersetzung ausstehend).

!!! note "Datenschutz"
    Bewerbungsdaten bleiben im git-ignorierten Ordner `bewerbung/` und werden nie committet.

!!! note "Noch nicht enthalten"
    Zeugnisanalyse, Vorstellungsgesprächs-Vorbereitung sowie PDF- und DOCX-Export stehen auf der Roadmap.
