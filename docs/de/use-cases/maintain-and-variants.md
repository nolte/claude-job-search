# Daten und Lebensläufe aktuell halten

**Ziel:** die Datengrundlage korrekt halten, während dein Werdegang weitergeht, und
Lebensläufe mit eigenem Schwerpunkt über mehrere Bewerbungen wiederverwenden.

**Beispiel:** Du hast bei der Beispiel AG die Rolle gewechselt, eine Zertifizierung abgeschlossen
und bewirbst dich nun sowohl auf Fach- als auch auf Führungsstellen.

## Die Datengrundlage pflegen

```text
/claude-job-search:job-application-cv-maintain
```

Der Skill prüft die erforderlichen Kernpunkte und Unstimmigkeiten in deiner Datengrundlage
(Lücken zwischen Stationen, fehlende Daten, widersprüchliche Angaben) und fragt **nur nach den
Befunden**. Jede bestätigte Antwort wird in die Datei geschrieben; jede Änderung steht im
Pflegeverlauf. Zum Schluss meldet er den Hash der Grundlage. Skills, die darauf aufbauen,
vergleichen diesen Hash und melden, wenn `profil.md` veraltet ist.

Neues Rohmaterial (ein frisches Zertifikat, ein aktueller LinkedIn-Export) legst du in
`rohdaten/` ab; danach bringt `job-application-profile-capture` es ein und leitet `profil.md`
neu ab.

## Lebenslauf-Ausprägungen

Eine **Ausprägung** ist ein Lebenslauf mit eigenem Schwerpunkt, den du wiederverwendest. Bitte
den Lebenslauf-Skill darum:

```text
Lege eine Variante "teamleitung" an: Schwerpunkt Führung und Projektverantwortung.
```

Jede Ausprägung hat einen Ordner (zum Beispiel `lebenslauf-teamleitung/`) mit `lebenslauf.md`,
`pruefbericht.md`, den eingefrorenen Versionen in `versionen/` und deren Exporten in `export/`.
Ein Vorgang, der einen geänderten Lebenslauf braucht, erhält eine eigene Ausprägung, abgeleitet
aus einer bestehenden Version; er ändert nie eine andere Ausprägung. Kein Skill ändert eine
eingefrorene Version oder löscht sie ohne deine Aufforderung.

## Eine Version vor dem Versand einfrieren

Am Ende fragt der Lebenslauf-Skill, ob dieser Stand der zu versendende ist. Bestätigst du, kopiert
er das Dokument nach `versionen/v<NNN>_<Datum>.md`. Eine eingefrorene Version wird nie bearbeitet.
Die nächste Änderung erhöht die Versionsnummer, sodass du jederzeit zeigen kannst, was ein
Empfänger genau erhalten hat. Exporte lassen sich aus ihrem Manifest neu bauen
(`task export -- --reproduce <Datei>.manifest.json`) und mit dem Original vergleichen.

## Was bleibt

Die aktualisierte Datengrundlage mit Pflegeverlauf, `profil.md` und je Ausprägung Arbeitsstand,
eingefrorene Versionen und Exporte.

## Rhythmus

Ein kurzer `cv-maintain`-Lauf nach jeder wesentlichen Änderung und vor einer größeren Serie von
Bewerbungen hält die späteren Schritte schnell: Die Anzeigenanalyse findet kein veraltetes Profil,
und die Qualitätsprüfung hat weniger Befunde.
