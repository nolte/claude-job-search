---
title: Pflege-Interview für die Datengrundlage
status: implemented
created: 2026-10-21
---

# Anforderung: Pflege-Interview für die Datengrundlage

## Ausgangslage

Die Datengrundlage (Spec R-9, Anforderung `eigene-datengrundlage.md`) ist die einzige Quelle
der Wahrheit für alle Bewerbungsunterlagen. Der Nutzer pflegt sie über die Zeit: neue Stationen,
Zertifikate, korrigierte Daten. Eine bestehende Notiz hat oft Lücken und Unstimmigkeiten, die
erst beim Lesen auffallen. Das Gegenstück zur Zieldatei muss deshalb ein geführtes Interview
sein, das den Stand prüft und den Nutzer gezielt fragt.

Bisher gibt es dafür keinen Ablauf. `job-application-profile-capture` legt eine Grundlage neu an,
kann aber ein bestehendes Dokument nicht vervollständigen und prüft keine Kernpunkte.

## Ziel

Der Nutzer pflegt eine bestehende Datengrundlage in einem geführten Dialog. Der Dialog
erkennt fehlende Kernpunkte und Unstimmigkeiten, fragt nur dazu nach und schreibt die
Antworten nach Bestätigung in die Datei. Am Ende ist die Datei vollständig oder die offenen
Punkte sind ausdrücklich markiert.

## Begriffe

| Begriff | Bedeutung |
|---|---|
| **Datengrundlage** | Markdown-Datei mit allen Stationen, Abschlüssen und Nachweisen (Spec R-9). |
| **Kernpunkt** | Angabe, die für eine Zielausgabe nötig ist, siehe Checkliste unten. |
| **Befund** | Ergebnis der Prüfung: fehlender Kernpunkt oder Unstimmigkeit. |
| **Pflegelauf** | Ein Durchlauf des Interviews von der Prüfung bis zum Abschlussbericht. |
| **Offen-Marker** | `[ERGÄNZEN: …]` für fehlende Angaben, `[KLÄREN: …]` für Widersprüche (Spec R-1). |

## Eingabe

- **Pfad zur Datengrundlage.** Standard: `job-application/grundlage/lebenslauf-chronologisch.md`.
  Der Nutzer kann einen anderen Pfad angeben, etwa eine bestehende Notiz. Die Entscheidung
  dazu steht unter „Offene Entscheidungen“.
- **Optional:** neue Rohdaten (Lebenslauf-PDF, Zeugnisse, Notizen), die zuerst eingearbeitet
  werden (Spec R-9.4).
- **Optional:** Schwerpunkt des Laufs, etwa „nur Stationen“ oder „nur Zertifikate“.

## Kernpunkt-Checkliste

Die Checkliste ist die Prüfgrundlage des Pflegelaufs. Pflicht bedeutet: für Zielausgaben nötig.
Optional bedeutet: nur auf Wunsch des Nutzers ergänzen (Spec R-2, R-8.2).

| Bereich | Kernpunkt | Status |
|---|---|---|
| Kontakt | Name, Anschrift, Telefon, E-Mail | Pflicht |
| Kontakt | LinkedIn-Profil | optional |
| Persönlich | Geburtsdatum, Familienstand, Staatsangehörigkeit | optional, nur auf Wunsch |
| Persönlich | Foto | optional, länderabhängig (R-8.2) |
| Station | Zeitraum im Format `MM/JJJJ – MM/JJJJ` oder `MM/JJJJ – heute` | Pflicht |
| Station | Position exakt wie im Zeugnis | Pflicht |
| Station | Arbeitgeber mit Rechtsform und Ort | Pflicht |
| Station | Aufgaben als Stichpunkte | Pflicht, mindestens eine Zeile |
| Station | Ergebnisse, belegt durch Zahl oder qualitativ | empfohlen für relevante Stationen |
| Station | Zeugnis-Nachweis: Datei, Datum, Aussteller, Wortlaut der Schlussbeurteilung | Pflicht, wenn ein Zeugnis existiert |
| Ausbildung | Abschluss, Ort, Zeitraum | Pflicht |
| Schule | Abschluss, Schule, Jahr | Pflicht |
| Weiterbildung | Titel, Anbieter, Jahr | empfohlen |
| Sprachen | Sprache mit GER-Niveau (z. B. B2) | Pflicht |
| IT-Kenntnisse | Werkzeuge mit Niveau oder Nutzungsdauer | empfohlen |
| Zielrichtung | Gesuchte Rollen, Standort, Eintrittstermin | optional |

## Prüfregeln

Die Prüfung läuft vollständig vor dem Interview. Sie erzeugt eine Befundliste mit drei Stufen.

| Stufe | Befund | Beispiel |
|---|---|---|
| **Blocker** | Pflichtkernpunkt fehlt oder ist widersprüchlich | Kontaktdaten leer; zwei Zeiträume für dieselbe Station |
| **Warnung** | Format oder Plausibilität weicht von R-2/R-2.1 ab | Jahresangabe statt `MM/JJJJ`; Lücke über zwei Monate ohne Erklärung; mehr als fünf Stichpunkte bei einer Station; Zeitraum mit Ende vor Beginn |
| **Hinweis** | Inhalt kann verbessert werden | Station ohne Ergebnis; Zahl ohne Beleg; Überschneidung zwischen Ausbildung und Schule, die möglich aber zu klären ist |

Regeln im Einzelnen:

1. **Format:** Zeiträume, Datumsangaben und Sprachniveaus in der vorgegebenen Form.
2. **Plausibilität:** Ende nach Beginn; keine Doppelung derselben Station; Überschneidungen
   bei Vollzeitstationen werden gemeldet, nicht korrigiert.
3. **Lücken:** Zeiträume ohne Beschäftigung über zwei Monate brauchen eine neutrale Angabe
   (Spec R-2.1.3).
4. **Stichpunkte:** drei bis fünf für die aktuellsten relevanten Stationen, ein bis zwei für ältere
   (Spec R-2.1.2).
5. **Zahlen:** jede Zahl in einem Stichpunkt muss im Nutzerkontext oder in einem Zeugnis belegt sein.
   Unbelegte Zahlen werden als Blocker gemeldet (Spec R-1).
6. **Zeugnisse:** jede Station mit Zeugnis trägt den Nachweis. Titel und Zeitraum werden
   gegen das Zeugnis geprüft.

## Ablauf des Interviews

1. **Bestandsaufnahme.** Der Skill liest die Datei, prüft die Kernpunkte und zeigt den
   Befundbericht: Anzahl Blocker, Warnungen und Hinweise, gegliedert nach Abschnitt.
2. **Fragen.** Der Skill stellt die Fragen zu den Befunden, Blocker zuerst. Höchstens drei
   Fragen pro Runde. Jede Frage nennt den betroffenen Abschnitt und den Befund in einem Satz.
3. **Antwort.** Der Nutzer antwortet, überspringt eine Frage oder erklärt sie als irrelevant.
   Überspringen erzeugt den Offen-Marker. Eine Frage wird nicht erneut gestellt, außer der
   Nutzer wünscht es.
4. **Anwenden.** Nach jeder Antwort wird die Änderung in die Datei geschrieben. Der Nutzer
   bekommt die geänderte Stelle zu sehen, bevor sie gespeichert wird. Bei einem Abbruch bleibt
   der Zwischenstand erhalten.
5. **Bestätigung.** Jede neue oder geänderte Station wird vom Nutzer bestätigt
   (`Bestätigt: ja`, Spec R-9.4).
6. **Abschluss.** Der Skill setzt `stand` auf das heutige Datum, berechnet den Hash
   (`sha256sum`) und legt den Abschlussbericht vor: erledigte Punkte, offene Punkte, verbleibende
   Blocker.

## Funktionale Anforderungen

**FA-P1 Vollständigkeitsbericht.** Vor jeder Frage liegt der Befundbericht nach Stufen vor.

- *Akzeptanz:* Eine Datei mit fünf fehlenden Pflichtpunkten erzeugt fünf Blocker-Einträge
  mit Abschnitt und Befund.

**FA-P2 Fragen nur zu Befunden.** Der Skill stellt keine allgemeinen Fragen zu Bereichen ohne Befund.

- *Akzeptanz:* Eine vollständige Datei erzeugt keine Frage außer dem Abschlussbericht.

**FA-P3 Gruppierung.** Höchstens drei Fragen pro Runde, Blocker vor Warnungen, Warnungen vor Hinweisen.

- *Akzeptanz:* Bei zwölf Befunden erscheinen die Fragen in vier Runden mit der Reihenfolge der Stufen.

**FA-P4 Keine Fakten ohne Bestätigung.** Der Skill schreibt nur Werte, die der Nutzer nennt oder
die aus einem Rohdokument stammen und bestätigt sind (Spec R-1).

- *Akzeptanz:* Eine Antwort wie „weiß ich nicht“ erzeugt `[ERGÄNZEN: …]`, keinen erfundenen Wert.

**FA-P5 Unverändertes bleibt unverändert.** Nur die angefragten Stellen werden geändert. Der
Rest der Datei, einschließlich Frontmatter und Struktur, bleibt erhalten.

- *Akzeptanz:* Ein Diff nach einem Lauf zeigt nur die beantworteten Stellen.

**FA-P6 Änderungsprotokoll.** Die Datei erhält einen Abschnitt „Pflegeverlauf“ mit Datum und
Kurzbeschreibung jeder Änderung.

- *Akzeptanz:* Nach drei Änderungen enthält der Abschnitt drei Einträge mit Datum.

**FA-P7 Wiederholbarkeit.** Ein zweiter Lauf ohne Änderungen zeigt nur noch die offenen
Punkte, keine bereits erledigten.

- *Akzeptanz:* Ein Lauf nach vollständiger Pflege meldet „keine Befunde“ und berechnet nur den Hash neu.

**FA-P8 Hash und Stand.** Am Ende aktualisiert der Skill `stand` und den Hash, damit
bestehende Zielausgaben als veraltet erkannt werden (Spec R-9.5).

- *Akzeptanz:* Nach einer Änderung weicht der gespeicherte Hash in den Profil- und Zielausgaben
  vom neuen Hash ab und wird von `job-application-quality-gate` gemeldet.

**FA-P9 Optionale Felder.** Geburtsdatum, Familienstand, Foto und Staatsangehörigkeit werden nur
gefragt, wenn der Nutzer sie in einer Sitzung ausdrücklich einschließt.

- *Akzeptanz:* Ohne Schwerpunkt „persönlich“ erscheinen diese Felder nicht in den Fragen.

## Nicht-funktionale Anforderungen

**NFA-P1 Abbruch ohne Verlust.** Jede bestätigte Antwort wird sofort gespeichert. Ein Abbruch
verliert höchstens die laufende Frage.

**NFA-P2 Datenschutz.** Die Datei liegt lokal und wird nicht committet (Spec R-6). Der Befundbericht
im Chat zeigt Abschnittsnamen und Befunde, nicht die vollständigen Werte sensibler Felder.

**NFA-P3 Sprache.** Fragen und Befunde sind deutsch. Original-Zitate bleiben unverändert.

**NFA-P4 Kein Netzwerkzugriff.** Der Pflegelauf nutzt nur die Datei und die Antworten des Nutzers.

## Abnahmekriterien

1. Auf eine unvollständige Beispielnotiz angewendet, liefert der Lauf einen Befundbericht
   mit allen Blockern (FA-P1), fragt nur dazu nach (FA-P2) und höchstens drei Fragen pro Runde (FA-P3).
2. Eine Antwort wird nach Bestätigung in die Datei geschrieben. Der Diff zeigt nur die
   beantwortete Stelle (FA-P5). Der Pflegeverlauf enthält einen Eintrag (FA-P6).
3. Ein zweiter Lauf auf dieselbe Datei meldet nur die verbleibenden Befunde (FA-P7).
4. Nach Abschluss stimmen `stand` und Hash überein, und `job-application-quality-gate` erkennt eine
   spätere Änderung der Datei (FA-P8).
5. Ohne Schwerpunkt „persönlich“ erscheinen keine optionalen persönlichen Felder (FA-P9).

## Auswirkungen auf bestehende Bausteine

| Baustein | Änderung |
|---|---|
| Spec `spec/job-application/konventionen/en.md`, R-9 | Neuer Abschnitt „Pflegelauf“ mit Checkliste, Prüfstufen und Pflegeverlauf |
| `job-application-profile-capture` | Bei bestehender Datei Verweis auf den Pflegelauf statt Neuanlage |
| `job-application-quality-gate` | Hash-Abgleich mit der Datengrundlage (bereits in Spec R-7 und R-9.5) |
| Neuer Skill (siehe Entscheidung E-P1) | Führt den Pflegelauf aus |

## Nicht-Ziele

- Import aus Online-Profilen (z. B. LinkedIn-API).
- Automatisches Korrigieren von Unstimmigkeiten ohne Rückfrage.
- Schreiben in Notizsysteme außerhalb des angegebenen Pfades.
- Bewertung der Qualität der Berufserfahrung. Der Lauf prüft Vollständigkeit und Form,
  nicht die inhaltliche Stärke.

## Entscheidungen

Entschieden am 2026-10-21 durch den Nutzer, jeweils in Übereinstimmung mit der Empfehlung.

**E-P1 Eigener Skill oder Modus?** Entschieden: eigener Skill `job-application-cv-maintain`.
Der Pflegelauf hat eine andere Ablauflogik als die Erstanlage (Prüfung, Befundbericht, Fragen in
Runden) und sollte nicht in `job-application-profile-capture` vermischt werden. `job-application-profile-capture`
verweist bei bestehender Datei auf den neuen Skill.

**E-P2 Quelle der Wahrheit.** Entschieden: referenzieren statt kopieren. Der Pfad ist konfigurierbar, Standard ist
`job-application/grundlage/lebenslauf-chronologisch.md`. Eine bestehende Notiz wird über den Pfad
referenziert und nicht kopiert. Dann gibt es nur eine Quelle, und der Hash bezieht sich auf die
Datei unter diesem Pfad. Der Nutzer muss die Notiz bei Pfadwechsel selbst pflegen.

**E-P3 Prüfung des Pfades außerhalb des Repositories.** Entschieden: Der Skill akzeptiert jeden
lokalen Pfad, verweigert aber Pfade innerhalb des Plugin-Repositories, um eine versehentliche
Committierung zu verhindern.

## Quellen

Die Checkliste und die Prüfregeln stützen sich auf die Spec (R-1, R-2, R-2.1, R-6, R-8.2, R-9).
Externe Quellen wurden für dieses Dokument nicht neu erhoben. Die Grundlage der Lebenslauf-Regeln
steht in `project/requirements/lebenslauf-formate.md`.
