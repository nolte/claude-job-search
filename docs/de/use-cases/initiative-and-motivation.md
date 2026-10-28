# Initiativbewerbung und Motivationsschreiben

**Ziel:** dich ohne Anzeige bewerben oder den Text schreiben, den ein Programm verlangt: deine
Gründe und Ziele.

## Initiativbewerbung

**Beispiel:** Du möchtest bei der Beispiel AG arbeiten, die keine passende Stelle ausgeschrieben
hat.

```text
/job-application:job-application-cover-letter-create
```

Wähle die Variante `initiativ`. Ohne Anzeige gibt es weder eine Anforderungsliste noch eine
Kennzahl. Der Betreff lautet „Initiativbewerbung als <Rolle>" oder „Initiativbewerbung im
Bereich <Bereich>", der Einstieg nennt den Bereich und deinen Grund für die Wahl, und die Belegabsätze nennen zwei oder drei
nachgewiesene Stärken. Der Brief sagt auch, was das Unternehmen bekommt, nicht nur, was du
willst. Fakten über das Unternehmen brauchen eine Quelle. Den Lebenslauf erzeugst du wie üblich
mit `job-application-cv-create`, die Qualitätsprüfung prüft den Satz.

Direkt aufgerufen, schreibt der Skill `anschreiben.md` in den Ordner `<wurzel>/<slug>/`. Die
Anzeigenanalyse (`analyse.md`) ist für diese Variante optional. Status und Verlauf in
`vorgang.md` werden nur fortgeschrieben, wenn der Ordner bereits eine `vorgang.md` enthält;
lege sonst zuerst den Vorgang an, damit die Bewerbung wie jede andere nachverfolgt wird.

## Motivationsschreiben für Stelle, Studium oder Stipendium

**Beispiel:** Ein Stipendium der erfundenen Beispiel-Stiftung verlangt ein Motivationsschreiben.

```text
/job-application:job-application-motivation-letter-create
```

Die Varianten sind `stelle` (Standard), `studium`, `stipendium`, `quereinstieg` und
`berufseinstieg`. Der Text besteht aus **deinen** Gründen und Zielen in deinen Worten plus zwei
oder drei Belegen aus der Datengrundlage. Der Skill fragt dich nach den Gründen und erfindet sie
nie:

```text
Warum dieses Stipendium? Was wollen Sie in drei Jahren erreicht haben?
```

Antworte in groben Sätzen; der Skill formt sie und vermerkt die Herkunft jedes Teils in einer
Notiz. Ergebnis ist `motivationsschreiben.md`. Hat ein Portal ein Freitextfeld, ist zusätzlich
eine Klartextfassung `motivationsschreiben-portal.txt` möglich.

## Anschreiben oder Motivationsschreiben?

| Text | Schwerpunkt | Einsatz |
|---|---|---|
| Anschreiben | Anforderungen der Anzeige und Belege aus deinem Werdegang | die übliche Bewerbung |
| Motivationsschreiben | warum du das willst und wohin du dich entwickelst | Anzeige oder Programm verlangt es; Stipendium; Studium |

Beide können Teil einer Bewerbung sein, wenn die Anzeige beides verlangt.

## Was bleibt

`anschreiben.md` oder `motivationsschreiben.md`, das Prüfergebnis in `pruefbericht.md` und die
Einträge in `vorgang.md`.
