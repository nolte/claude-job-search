# Anwendungsfälle

Diese Seiten zeigen das Plugin in den Situationen, in denen Bewerbende tatsächlich stehen. Jede
Seite beginnt bei einem Ziel, nennt die Voraussetzungen, führt mit den Befehlen und dem, was du
siehst, durch die Schritte und endet mit den Dateien, die in deinem Datenordner bleiben. Alle
Namen in den Beispielen sind frei erfunden (Musterfirma GmbH, Beispiel AG).

[Erste Schritte](../getting-started.md) erklärt Installation und Konfiguration einmal; die
Anwendungsfälle setzen voraus, dass beides erledigt ist und deine Datengrundlage existiert.

## Welche Seite passt zu dir

| Deine Situation | Seite | Beteiligte Skills |
|---|---|---|
| Du hast eine Stellenanzeige und willst eine vollständige, geprüfte Bewerbung | [Auf eine Anzeige bewerben](posting-application.md) | `job-application-solution`, `-posting-analysis`, `-cv-create`, `-cover-letter-create`, `-email-create`, `-quality-gate`, `-export` |
| Ein Recruiter oder eine Agentur meldet sich, oder der Arbeitgeber bleibt verdeckt | [Über Recruiter oder Agentur](recruiter.md) | `job-application-solution`, `-posting-analysis` (Gegenpartei), `-cover-letter-create` (Variante `vermittler`) |
| Du weißt nicht, worauf du dich bewerben sollst, oder wechselst das Fach | [Berufswechsel und Stellensuche](career-change.md) | `job-application-traumjob-interview`, `-job-search`, `-fit-check`, `-cv-create` (Format `kombiniert`) |
| Es gibt keine Anzeige, oder ein Programm fragt nach deinen Gründen | [Initiativbewerbung und Motivationsschreiben](initiative-and-motivation.md) | `job-application-cover-letter-create` (Variante `initiativ`), `-motivation-letter-create` |
| Dein Werdegang ist weitergegangen und die Basisdaten müssen folgen | [Daten und Lebensläufe aktuell halten](maintain-and-variants.md) | `job-application-cv-maintain`, `-profile-capture`, `-cv-create` (Ausprägungen, eingefrorene Versionen) |

## Regeln, die in jedem Szenario gelten

- **Erst der Plan, dann die Dokumente.** Kein Dokument entsteht, bevor du den Plan freigibst.
- **Keine erfundenen Fakten.** Jede Aussage stammt aus deiner Datengrundlage; was fehlt, bleibt
  als `[ERGÄNZEN: …]` sichtbar, bis du es klärst.
- **Du versendest.** Das Plugin bereitet vor und prüft. Versand, Antworten und das Ergebnis trägst
  du selbst in `vorgang.md` ein.
- **Optionale Server bleiben optional.** Jedes Szenario funktioniert mit eingefügtem Text.
  LinkedIn, Handelsregister, Websuche und JobSpy erhöhen nur den Komfort, siehe
  [Optionale MCP-Server](../mcp-servers.md).
