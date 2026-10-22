# Gegenpartei: mit wem du es zu tun hast

Nicht jede Stellenanzeige kommt vom Arbeitgeber. Das Plugin ordnet die Gegenpartei jeder
Bewerbung ein, wenn es die Anzeige analysiert, hält das Ergebnis in `analyse.md` fest und passt
an, was es schreibt und was es dich vorher fragt. Diese Seite erklärt die Arten, die Fragen und
warum das Plugin in manchen Fällen keine vollständigen Unterlagen erzeugt.

## Die Arten

| Gegenpartei | Wer das ist | Was sie von dir will | Worauf du achtest |
|---|---|---|---|
| **Arbeitgeber direkt: Personalabteilung** | HR, Recruiting | Vollständige Unterlagen passend zur Anzeige, ein sauberer Prozess | Langsamer Prozess, Standardantworten |
| **Arbeitgeber direkt: Fachbereich** | Hiring Manager, Teamleitung | Fachliche Tiefe und Belege für die gelösten Probleme, schnell | Übertriebene Tiefe |
| **Arbeitgeber direkt: Geschäftsführung** | Geschäftsführung, Inhaber, oft in kleinen Firmen | Passung zur Richtung der Firma, Verantwortungsumfang, Verlässlichkeit | Unklare Rollengrenzen |
| **Personalberatung / Headhunter** | Ein Recruiter mit Mandat eines Arbeitgebers | Ein schnell präsentierbares Profil, deine Verfügbarkeit, Flexibilität bei den Konditionen | Dein Profil geht womöglich an mehrere Kunden; der Arbeitgeber bleibt verdeckt; Druck beim Gehalt |
| **Personalvermittlung / Zeitarbeit** | Eine Agentur, die dich anstellt oder bei einem Kunden einsetzt | Verfügbarkeit, ein Standardprofil, schnelle Vermittlung | Die Konditionen (Agentur oder Kunde) unterscheiden sich von dem, was die Anzeige nahelegt |
| **Empfehlung** | Eine Mitarbeiterin oder ein Mitarbeiter, der dich empfiehlt | Eine Empfehlung, die ihm nicht schadet | Du schuldest dem Empfehlenden einen sauberen Prozess |
| **Jobportal** | Eine automatische Nachricht oder ein Plattform-Recruiter | Ein schneller Treffer, ein Klick | Die Anzeige kann veraltet oder doppelt sein |
| **Unklar** | Alle, die in keine Zeile oben passen | Herauszufinden | Handeln auf falscher Annahme |

Das Plugin liest Signale in Anzeige und Nachricht: ein verdeckter Arbeitgeber („unser Kunde“,
„vertraulich“), eine Absenderdomain, die nicht zum Arbeitgeber passt, Hinweise auf eine
Provision oder auf Arbeitnehmerüberlassung, eine automatische Plattformnachricht, eine
Empfehlung mit Namen. Zwei unabhängige Signale sind nötig, bevor eine Art als wahrscheinlich
gilt; ohne Signal hält es *unklar* fest und fragt dich.

## Die Fragen, die das Plugin dir stellt

Ist die Gegenpartei ein Headhunter oder eine Agentur, bittet dich der Planschritt, ein paar
Dinge zu klären, bevor ein Dokument entsteht, und hält die Antworten mit Datum fest:

- **Ist der Arbeitgeber bekannt?** Ein Recruiter darf dein Profil einem Kunden vorlegen. Du
  musst wissen, an welchen Arbeitgeber jedes Profil geht. Nach dem Auftraggeber zu fragen ist
  ein normaler Schritt, kein Vorwurf; auch eine Weigerung wird festgehalten und senkt die
  Sicherheit der Einordnung.
- **Hat der Recruiter ein exklusives Mandat?** Ein exklusives Mandat blockiert eine direkte
  Bewerbung beim selben Arbeitgeber über einen anderen Weg.
- **Doppelbewerbung?** Das Plugin sucht in deiner Wurzel nach anderen Bewerbungen beim selben
  Arbeitgeber. Würdest du denselben Arbeitgeber zweimal erreichen, über einen Recruiter und
  direkt, sagt es dir das, bevor etwas hinausgeht.
- **Was darf weitergegeben werden?** Kontaktdaten (Telefon, Anschrift), Gehalt und
  Kündigungsfrist gehen nur mit deiner Zustimmung für diesen Arbeitgeber an einen Recruiter, und
  der Recruiter bekommt dieselben Fakten wie der Arbeitgeber, nicht mehr.
- **Wer zahlt wem?** Du zahlst keine Vermittlungsprovision für die Stelle eines Arbeitgebers.
  Erwähnt eine Nachricht eine Provision, markiert das Plugin das, und es entsteht kein Dokument,
  bevor du die Bedingungen geprüft hast.

## Warum keine vollständigen Unterlagen vor der Offenlegung

Ein vollständiger Lebenslauf und ein Anschreiben sind für einen Arbeitgeber geschrieben: Die
Stationen sind für diese Anzeige ausgewählt, der Brief nennt die Firma, und die
Qualitätsprüfung prüft das Set gegen die Anzeige. Solange der Arbeitgeber unbekannt ist, geht
nichts davon wahrheitsgemäß, und ein vollständiger Lebenslauf in den Händen eines Recruiters
kann ohne dein Wissen weitergereicht werden.

Für einen Headhunter oder eine Agentur, deren Kunde noch nicht genannt ist, erzeugt das Plugin
deshalb ein **Kurzprofil** und deine Verfügbarkeit, und die E-Mail stellt die beiden Fragen von
oben. Das vollständige Set folgt, sobald der Arbeitgeber bekannt und festgehalten ist. Bei einem
Arbeitgeber, der dich direkt anschreibt, wird nichts zurückgehalten.

## Was das für dich heißt

- Rechne damit, dass der Plan die Gegenpartei nennt und bei Recruitern auf deine Antworten
  wartet.
- Halte die Antworten des Recruiters im Bewerbungsordner fest (`analyse.md` speichert sie, deine
  eigenen Notizen gehören in `notizen.md`), damit ein späterer direkter Kontakt mit demselben
  Arbeitgeber keine Doppelbewerbung wird.
- Ton und Einstieg des Anschreibens folgen der Gegenpartei: förmlich bei Personalabteilung und
  Geschäftsführung, sachlich beim Fachbereich, kurz auf einer Plattform.
- Das Plugin entscheidet, wie du kommunizierst, sobald du dich zur Bewerbung entschieden hast. Ob
  du dich bewirbst, entscheidet es nicht.

!!! info "Für Entwickler"
    Die Regeln hinter dieser Seite: `spec/job-application/kontaktklassifikation/en.md` (Arten und
    Motivationen, Signale und Einordnung, Offenlegung und Vertraulichkeit, Kommunikation je
    Gegenpartei) und `spec/job-application/unternehmensanalyse/en.md` (die Firmen hinter einer
    Bewerbung und wie sie festgehalten werden).
