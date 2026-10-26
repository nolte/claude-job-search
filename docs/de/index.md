# claude-job-search

Claude-Code-Plugin mit Skills und einem Agenten für Bewerbungsunterlagen im
deutschsprachigen Raum: Wunschprofil und Passung, einspaltiger Lebenslauf nach Situation,
DIN-5008-Anschreiben, Motivationsschreiben, Bewerbungs-E-Mail, Abgleich der Anforderungen
mit der Stellenanzeige, eine Qualitätsprüfung vor dem Versand, Export als PDF, DOCX, HTML
oder Markdown und ein Ordner je Bewerbung, der ihren Status festhält.

## Überblick

Du beschreibst eine **Stellenanzeige**. Der Einstieg `job-application-solution` prüft dein
Profil, analysiert die Anzeige, zeigt dir einen Plan und erstellt erst danach die
Unterlagen in der richtigen Reihenfolge. Alle Fakten stammen aus deiner lokalen
Datengrundlage. Das Profil, `profil.md`, wird daraus mit Quellenverweis abgeleitet. Fehlende
Angaben werden markiert, nie erfunden.

Jede Bewerbung bekommt einen eigenen Ordner, den Vorgang. Darin liegen die Anzeige, die
Analyse, die Unterlagen, der Prüfbericht und `vorgang.md` mit Status und Verlauf der
Bewerbung. Den Ablauf zeigt dir [Erste Schritte](getting-started.md), die Begriffe erklärt das
[Glossar](glossary.md).

## Einstieg

- Neu hier? Lies [Erste Schritte](getting-started.md): installieren, konfigurieren, Daten erfassen, erste Bewerbung.
- Du willst das Plugin in einer Situation wie deiner sehen? Die [Anwendungsfälle](use-cases/index.md): Anzeige, Recruiter, Berufswechsel, Initiativbewerbung, Daten aktuell halten.
- `/claude-job-search:job-application-profile-capture`, wenn noch keine Datengrundlage existiert.
- Du willst erst wissen, was du suchst? Führe einmal `/claude-job-search:job-application-traumjob-interview` aus und danach `/claude-job-search:job-application-fit-check` für jede Stelle oder Firma.
- Hast du noch keine Anzeige? Führe `/claude-job-search:job-application-job-search` aus, um Jobbörsen mit einem Brief zu durchsuchen, den du zuerst freigibst; dafür brauchst du den optionalen Server [JobSpy](jobspy.md), mit eigenen Risiken.
- `/claude-job-search:job-application-solution` mit dem Text der Stellenanzeige für eine komplette Bewerbung.
- `/claude-job-search:job-application-quality-gate` vor dem Versand eines vorhandenen Bewerbungsordners.
- Mehrere Bewerbungen und Suchen gleichzeitig? Der [Workflow](workflow.md) behält über Sitzungen hinweg die Reihenfolge der Schritte, was auf deine Freigabe wartet und was fehlgeschlagen ist.
- Bewirbst du dich über einen Personalvermittler oder Headhunter? Lies zuerst [Gegenpartei](counterparts.md).
- Du willst wissen, welche optionalen MCP-Server es gibt und welche Regeln für alle gelten? Siehe [Optionale MCP-Server](mcp-servers.md); keiner ist nötig.
- Claude soll LinkedIn-Anzeigen, Firmenseiten und Profile direkt lesen? Siehe [LinkedIn-Zugriff](linkedin.md), ein optionaler MCP-Server mit eigenen Risiken.
- Claude soll eine Firma gegen das Handelsregister prüfen? Siehe [Handelsregister-Zugriff](handelsregister.md), ein optionaler MCP-Server mit eigenen Risiken.

!!! note "Datenschutz"
    Bewerbungsdaten bleiben lokal, in dem Ordner, den du konfigurierst (standardmäßig
    `job-application/`). Der Ordner ist standardmäßig git-ignoriert; ihn in einem privaten,
    nicht veröffentlichten Repository zu führen ist erlaubt und deine Entscheidung. Kein Skill
    versendet etwas.

!!! note "Noch nicht enthalten"
    Versand, Rückmeldungen und Gespräche trägst du selbst in `vorgang.md` und `notizen.md` ein
    (oder in Obsidian); ein Tracking-Skill steht auf der Roadmap, ebenso die Vorbereitung auf
    das Vorstellungsgespräch und die Zeugnisanalyse. Der Export erzeugt überall DOCX, HTML und
    Markdown; PDF braucht LuaLaTeX oder den Export-Container, siehe [Export](export.md).

!!! info "Für Entwickler"
    Die Konventionen dahinter stehen in den Spezifikationen unter `spec/job-application/`,
    beginnend mit `spec/job-application/konventionen/en.md` und
    `spec/job-application/lokale-struktur/en.md` (kanonisch auf Englisch, deutsche Übersetzung
    ausstehend). Der Index ist `spec/README.md`.
