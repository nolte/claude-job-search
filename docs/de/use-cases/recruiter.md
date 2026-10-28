# Über Recruiter oder Agentur

**Ziel:** einem Headhunter oder einer Agentur antworten, ohne deine Daten an einen unbekannten
Arbeitgeber zu geben und ohne dich doppelt beim selben Unternehmen zu bewerben.

**Beispiel:** Ein Recruiter schreibt: *„Unser Kunde, ein führender Softwareanbieter, sucht eine
Teamleitung Entwicklung. Bitte senden Sie uns Ihre vollständigen Unterlagen."* Ein Arbeitgeber
wird nicht genannt.

## Schritte

### 1. Die Nachricht an die Eingangstür geben

```text
/job-application:job-application-solution
```

Füge die Nachricht ein. Die Anzeigenanalyse liest die Signale („unser Kunde", eine Absender-
Domain, die zu keinem Arbeitgeber passt, ein Hinweis auf eine Vergütung) und hält die
Gegenpartei in `analyse.md` fest. Einen Typ vermerkt sie nur dann als *wahrscheinlich*, wenn
zwei unabhängige Signale vorliegen; ohne Signal steht dort *unklar*, und sie fragt dich.
Hintergrund: [Gegenpartei](../counterparts.md).

### 2. Die Fragen im Planschritt beantworten

Vor jedem Dokument fragt der Plan:

- Ist der Arbeitgeber bekannt? Du entscheidest, ob du ohne diesen Namen weitermachst.
- Hat der Recruiter ein exklusives Mandat?
- Hast du dich bereits bei diesem Arbeitgeber beworben? Das Plugin durchsucht die übrigen Ordner
  in deinem Datenordner und warnt vor einer Doppelbewerbung.
- Welche Kontaktdaten, Gehaltsangaben und Kündigungsfristen dürfen weitergegeben werden? Nur mit
  deiner Zustimmung für diesen Arbeitgeber.
- Ist eine Gebühr erwähnt? Dann entsteht kein Dokument, bevor du die Bedingungen geprüft hast.

Der Plan zeigt Gegenpartei, Verlässlichkeit und noch fehlende Offenlegung und führt den offenen
Punkt, bis du entschieden hast. Nach deiner Freigabe steht der Plan im Abschnitt `## Plan` von
`vorgang.md`.

### 3. Kein voller Satz vor der Offenlegung

Solange der Arbeitgeber unbekannt ist, geht kein Dokument an den Recruiter: Stationen lassen sich
für eine namenlose Stelle nicht wahrheitsgemäß auswählen, und ein vollständiger Lebenslauf kann
ohne dein Wissen weitergereicht werden. Hinausgehen darf ein Kurzprofil mit deiner Verfügbarkeit.
Der E-Mail-Skill formuliert eine solche Antwort an einen Vermittler, dessen Auftraggeber nicht
genannt ist: Er nennt keinen Arbeitgeber und fragt nach Auftraggeber und Mandat. Das Kurzprofil
ist Teil dieser Antwort; eine eigene Datei entsteht dafür nicht.

### 4. Der Arbeitgeber wird genannt

Trage den Namen in den Vorgang ein (sag der Eingangstür: *„Der Kunde ist die Beispiel AG."*).
Das Plugin prüft erneut auf frühere Bewerbungen bei der Beispiel AG und läuft dann wie eine
normale Bewerbung weiter ([Auf eine Anzeige bewerben](posting-application.md)). Das Anschreiben
nutzt die Variante `vermittler`; der Recruiter erhält dieselben Fakten wie der Arbeitgeber, nicht
mehr.

Ist ein Handelsregister-Server verbunden, lässt sich mit deiner Zustimmung die Identität der
Firma prüfen ([Handelsregister-Zugriff](../handelsregister.md)). Ohne ihn bleibt der Punkt
*nicht ermittelt*.

## Was bleibt

`analyse.md` mit Einordnung der Gegenpartei und ihrer Verlässlichkeit, der freigegebene Plan und
der Verlauf in `vorgang.md` sowie die Antwortmail als `email.md`. Ob du ohne den Namen des
Arbeitgebers weitermachst, entscheidest du; der Plan führt den Punkt offen, bis du entschieden
hast.

## Wenn der Arbeitgeber dich direkt anschreibt

Dann wird nichts zurückgehalten: Das Plugin ordnet die Gegenpartei ein (Personalabteilung,
Fachabteilung oder Geschäftsführung) und erzeugt den vollständigen Satz.
