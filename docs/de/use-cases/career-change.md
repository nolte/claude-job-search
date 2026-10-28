# Berufswechsel und Stellensuche

**Ziel:** herausfinden, was du willst, passende Anzeigen finden und dich in einem Fach bewerben,
in dem dein Lebenslauf nicht geradlinig verläuft.

**Beispiel:** Nach acht Jahren in der Logistikplanung willst du in die Datenanalyse wechseln.

## Schritte

### 1. Festhalten, was du willst

```text
/job-application:job-application-traumjob-interview
```

Ein Interview in sieben Phasen zu Wünschen, Prioritäten, Ausschlüssen und Hypothesen. Nichts
wird geschrieben, bevor du die Zusammenfassung bestätigst. Ergebnis ist `wunschprofil.md`
einschließlich deiner **Vetos** (zum Beispiel: kein Bereitschaftsdienst, keine Zeitarbeit).

### 2. Jobbörsen durchsuchen (optional)

```text
/job-application:job-application-job-search
```

Der Skill leitet aus Wunschprofil und `profil.md` einen **Suchbrief** ab, zeigt ihn mit der Quelle
jedes Suchbegriffs und sucht erst nach deinem Ja. Er braucht den optionalen
[JobSpy](../jobspy.md)-Server, der eigene Risiken mitbringt; lies zuerst diese Seite. Du erhältst
eine Auswahlliste, in der Vetos sichtbar sind, Dubletten zusammengeführt werden und
Vermittler-Anzeigen markiert sind. Die Liste liegt in `suche/<Datum>-<slug>.md`. Du wählst eine
Anzeige; der Skill übergibt sie an `job-application-solution`.

Ohne JobSpy überspringst du den Schritt und fügst eine selbst gefundene Anzeige ein.

### 3. Die Passung prüfen, bevor du investierst

```text
/job-application:job-application-fit-check
```

Füge eine Anzeige ein oder nenne ein Unternehmen. Das Ergebnis in `passung.md` lautet *Veto*,
*Klärungsbedarf* oder *Passt überwiegend*. Vetos stehen zuerst, und jeder Wert nennt seine Quelle.
Du kannst den Check vorab einzeln laufen lassen. Mit bestätigtem Wunschprofil führt ihn auch
`job-application-solution` in der Analyse aus, und ein Veto stoppt das Plan-Gate, bis du
entschieden hast. So schreibst du keine Unterlagen für eine Stelle, die du nicht annehmen
würdest.

### 4. Mit Quereinstiegsprofil bewerben

Starte `job-application-solution` für die gewählte Anzeige. Bei einem Wechsel schlägt der Plan
typischerweise vor:

- Lebenslauf-Format `kombiniert`: ein Kurzprofil von höchstens drei Sätzen, danach die
  chronologischen Stationen. Ältere relevante Belege können in einem kurzen Block *Relevante*
  stehen, nur in diesem Format.
- Anschreiben-Variante `quereinstieg`: Sie ordnet die Anforderungen der Anzeige Belegen aus deinen
  Logistikjahren zu (etwa Prognosen in Excel und SQL) und benennt offen, wo Erfahrung noch
  fehlt. Sie fragt dich nach dem Grund des Wechsels in einem Satz, in deinen Worten; sonst
  enthält der Brief `[ERGÄNZEN: Grund des Wechsels]`. Die Wünsche aus dem Interview erscheinen
  nicht im Brief.

## Was bleibt

`wunschprofil.md`, `suche/…`, je geprüfter Anzeige `passung.md` und der Vorgangsordner jeder
begonnenen Bewerbung.

## Gut zu wissen

- Du kannst das Interview später wiederholen; das Wunschprofil wird erst nach deiner Bestätigung
  ersetzt.
- Die Passungsprüfung ist eine Entscheidungshilfe, keine Bevormundung: *Klärungsbedarf* heißt
  Fragen fürs Gespräch, kein Nein.
