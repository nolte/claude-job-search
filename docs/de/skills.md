# Skills und Agenten

Die Spalte *Stufe* nennt den Schritt des Bewerbungsprozesses (S0 bis S10, siehe
[Erste Schritte](getting-started.md#7-status-pflegen-und-ubersicht)), in dem der Skill läuft.

| Name | Stufe | Zweck |
|---|---|---|
| `job-application-solution` | Einstieg (S1–S5) | Einstieg: Profil, Analyse, Freigabe des Plans, Unterlagen, Qualitätsprüfung. Schreibt den freigegebenen Plan in `vorgang.md` |
| `job-application-profile-capture` | Erfassung (S0) | Erstellt die Datengrundlage aus deinen Rohdaten und leitet daraus `profil.md` ab |
| `job-application-cv-maintain` | Erfassung (S0) | Geführtes Pflegeinterview für eine bestehende Datengrundlage: prüft Kernpunkte, fragt nach Befunden |
| `job-application-traumjob-interview` | Erfassung (S0) | Siebenphasiges Interview, das das bestätigte Wunschprofil speichert |
| `job-application-fit-check` | Analyse (S2) | Prüft eine Stelle oder ein Unternehmen gegen das Wunschprofil; Vetos zuerst, jeder Wert belegt |
| `job-application-posting-analysis` | Erfassung und Analyse (S1–S2) | Legt den Vorgang an (`stellenanzeige.md`, `vorgang.md`, `notizen.md`, Firmendatei in `firmen/`), extrahiert die Anforderungen und gleicht sie belegt mit der Datengrundlage ab; ordnet den Ansprechpartner ein und erfasst die Firmenrollen; führt immer Recherchestufe 0 zur Anzeige aus, die Stufen 1 und 2 auf Wunsch (`## Recherche`), LinkedIn nur über den MCP-Server mit deiner Zustimmung; Websuche und Seitenabruf bevorzugt über den open-webSearch-Server, wenn verbunden, sonst über die eingebauten Tools (siehe [Websuche](websearch.md)) |
| `job-application-cv-create` | Erstellung (S4) | Einspaltiger deutscher Lebenslauf im Format der Situation |
| `job-application-cover-letter-create` | Erstellung (S4) | Einseitiges Anschreiben im DIN-Format, vier Varianten |
| `job-application-motivation-letter-create` | Erstellung (S4) | Motivationsschreiben aus den von dir genannten Beweggründen und belegten Nachweisen, mit Herkunftsnachweis |
| `job-application-email-create` | Erstellung (S4) | Begleit-E-Mail mit Betreff, Anhangsliste und Dateinamen, nur bei Bewerbung per E-Mail |
| `job-application-quality-gate` | Prüfung (S5) | Qualitätsprüfung: Blocker, Warnungen, Hinweise. Setzt den Status auf `geprüft` (keine Blocker) oder `in Arbeit` |
| `job-application-export` | Export (S6) | Exportiert ein fertiges Dokument als DOCX, HTML oder Markdown; PDF über LaTeX (braucht LuaLaTeX oder den Container) via `task export` |
| `job-application-reviewer` (Agent) | Prüfung (S5) | Schreibgeschützte Gesamtprüfung aus Sicht einer Personalerin |

## Was die Skills festhalten

Jeder Skill, der an einer Bewerbung arbeitet, schreibt in den Ordner dieser Bewerbung und
sonst nirgendwohin. Der Status in `vorgang.md` sagt dir, wie weit eine Bewerbung ist:

| Schritt | Wer schreibt | Dateien | Status danach |
|---|---|---|---|
| Anzeige erfasst | `job-application-posting-analysis` | `stellenanzeige.md`, `vorgang.md`, `notizen.md` (leer), `firmen/<firma>.md` beim ersten Kontakt | `erfasst` |
| Analysiert | `job-application-posting-analysis` | `analyse.md` | `analysiert` |
| Plan freigegeben | `job-application-solution` | Abschnitt *Plan* in `vorgang.md` | `geplant` |
| Unterlagen erstellt | `job-application-cv-create`, `-cover-letter-create`, `-motivation-letter-create`, `-email-create` | `lebenslauf.md`, `anschreiben.md`, `motivationsschreiben.md`, `email.md`, `pruefbericht.md` (Abschnitt *Auswahl*) | `erstellt` |
| Geprüft | `job-application-quality-gate` | `pruefbericht.md` (Abschnitt *Prüfung*) | `geprüft` oder `in Arbeit` |
| Exportiert | `job-application-export` | `export/` | unverändert |

## Was du selbst pflegst

Der Versand und alles danach sind deine Angaben, nicht die des Plugins. Du trägst sie in
`vorgang.md` ein (Versanddatum, Weg, Anhänge, jede Rückmeldung, jedes Gespräch, das Ergebnis)
und hältst deine freien Notizen in `notizen.md` fest. Obsidian ist dafür ein bequemer Ort; das
Plugin braucht es nicht. [Erste Schritte](getting-started.md#7-status-pflegen-und-ubersicht)
zeigt die Statuswerte und eine Übersicht über alle Bewerbungen.

## Aufrufreihenfolge

Die Skills laufen für jede Stellenanzeige in fester Reihenfolge. Die einmaligen Schritte, also
Interview und Datengrundlage, kommen vorher. `job-application-solution` steuert den Lauf und
wartet auf deine Freigabe, bevor ein Dokument entsteht. Das Diagramm zeigt, welcher Skill
welche Datei an den nächsten übergibt. Gestrichelte Pfeile sind optional.

<!-- diagram-source: user-described—order of the job-application skills per posting, from intake to quality gate and export -->
```mermaid
flowchart LR
    subgraph intake ["Erfassung (einmalig oder bei geänderten Daten)"]
        interview[job-application-traumjob-interview]
        capture[job-application-profile-capture]
        maintain[job-application-cv-maintain]
    end
    subgraph run ["Je Stellenanzeige"]
        solution[job-application-solution]
        analysis[job-application-posting-analysis]
        fit[job-application-fit-check]
        plan{Plan freigegeben?}
        cv[job-application-cv-create]
        letter[job-application-cover-letter-create]
        motivation[job-application-motivation-letter-create]
        mail[job-application-email-create]
        gate[job-application-quality-gate]
    end
    export[job-application-export]
    reviewer[Agent job-application-reviewer]

    solution -->|keine Grundlage| capture
    maintain -->|Grundlage aktualisiert| capture
    capture -->|Profil| analysis
    solution --> analysis
    interview -.->|Wunschprofil| fit
    analysis -.->|Analyse| fit
    fit -.->|Veto stoppt die Prüfung| plan
    analysis --> plan
    plan -->|ja| cv
    cv -->|Lebenslauf| letter
    letter -.->|wenn verlangt| motivation
    motivation -.-> gate
    letter -->|nur bei E-Mail| mail
    letter --> gate
    mail --> gate
    gate -->|Blocker: zuständiger Skill behebt| cv
    gate -->|bereit| export
    gate -.->|optionale zweite Lesung| reviewer
```
