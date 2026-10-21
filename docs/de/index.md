# claude-job-search

Claude-Code-Plugin mit Skills und einem Agenten für Bewerbungsunterlagen im
deutschsprachigen Raum: einspaltiger Lebenslauf nach Situation, DIN-5008-Anschreiben,
Bewerbungs-E-Mail, Abgleich der Anforderungen mit der Stellenanzeige und eine
Qualitätsprüfung vor dem Versand.

## Überblick

Du beschreibst eine **Stellenanzeige**. Der Einstieg `job-application-solution` prüft dein
Profil, analysiert die Anzeige, zeigt dir einen Plan und erstellt erst danach die
Unterlagen in der richtigen Reihenfolge. Alle Fakten stammen aus einer lokalen
Profildatei, `job-application/profil.md`. Fehlende Angaben werden markiert, nie erfunden.

## Einstieg

- `/claude-job-search:job-application-solution` mit dem Text der Stellenanzeige für eine komplette Bewerbung.
- `/claude-job-search:job-application-profile-capture`, wenn noch kein Profil existiert.
- `/claude-job-search:job-application-quality-gate` vor dem Versand eines vorhandenen Ordners.

Die Konventionen stehen in der Spezifikation `spec/job-application/konventionen/en.md`
(kanonisch auf Englisch, deutsche Übersetzung ausstehend).

!!! note "Datenschutz"
    Bewerbungsdaten bleiben im git-ignorierten Ordner `job-application/` und werden nie committet.

!!! note "Noch nicht enthalten"
    Zeugnisanalyse, Vorstellungsgesprächs-Vorbereitung sowie PDF- und DOCX-Export stehen auf der Roadmap.
