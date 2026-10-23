# Glossar

Die Begriffe sind dieselben wie in den Skills, den Dateinamen und den Spezifikationen. So passt
das, was du im Chat liest, zu dem, was du auf der Platte findest.

**Datengrundlage (Grundlage)**
: Deine persönlichen Fakten in Markdown: Stationen, Ausbildung, Kenntnisse, Sprachen,
  Zeugnisse, jeweils mit Quelle. Die einzige Quelle der Wahrheit. Eine Datei oder ein
  Verzeichnis mit Notizen; nichts anderes darf einen Fakt erfinden.

**Profil (Ableitung)**
: `profil.md`, aus der Datengrundlage abgeleitet, mit Quellenverweis je Eintrag. Die
  Generatoren lesen es. Es wird neu abgeleitet, nie von Hand bearbeitet.

**Wunschprofil**
: Deine Wünsche, Prioritäten und Vetos für die nächste Stelle, vom Interview in
  `wunschprofil.md` festgehalten. Eine Präferenz, kein Fakt; es gelangt nie in ein Dokument.

**Wurzel**
: Der Wurzelordner aller Bewerbungsdaten, standardmäßig `job-application/`. Skills schreiben
  nirgendwo sonst.

**Anker (konfiguration.md)**
: `job-application/konfiguration.md`, die einzige Datei an fester Stelle. Sie nennt die Wurzel
  und die Datengrundlage; jeder andere Pfad wird über sie aufgelöst.

**Vorgang**
: Eine Bewerbung auf eine Stelle, von der Erfassung bis zum Abschluss, in einem eigenen Ordner
  unter der Wurzel. Enthält die Anzeige, die Analyse, die Unterlagen, den Prüfbericht und
  `vorgang.md`.

**Ausprägung**
: Eine Lebenslauf-Variante mit eigenem Schwerpunkt, die du über mehrere Bewerbungen
  wiederverwendest, etwa `lebenslauf-basis/`. Ein Ordner neben den Vorgängen mit
  `lebenslauf.md`, `pruefbericht.md`, `versionen/` und `export/`.

**Version**
: Eine eingefrorene Kopie eines Lebenslaufs in `versionen/`, die nie wieder bearbeitet wird.
  Exporte entstehen aus einer Version, damit die versendete PDF Byte für Byte nachgebaut werden
  kann.

**Stammdaten**
: Fakten, die über Bewerbungen hinweg gelten: deine in der Datengrundlage, die einer Firma in
  `firmen/<firma>.md`. Einmal erfasst, in jedem Vorgang wiederverwendet.

**Metadaten**
: Strukturierte Fakten zu einem Vorgang oder einer Firma im Frontmatter (`status`, Daten,
  Referenznummer). Skills lesen und schreiben sie.

**Notizen**
: Dein freier Text zu einem Vorgang (`notizen.md`) oder einer Firma. Skills lesen ihn und
  ändern ihn nie.

**Hash / stale**
: Jede abgeleitete Datei merkt sich einen Hash der Datengrundlage, aus der sie stammt. Ändert
  sich die Datengrundlage, passt der Hash nicht mehr und die Datei ist *stale* (veraltet): Sie
  wird neu abgeleitet, nicht geflickt.

**Plan-Gate**
: Der Moment, in dem der Einstieg den Plan für eine Bewerbung zeigt und auf deine Freigabe
  wartet. Kein Dokument entsteht, bevor du Ja sagst.

**Quality Gate**
: Die Prüfung vor dem Versand: Blocker, Warnungen und Hinweise. Eine Bewerbung mit Blockern ist
  nicht bereit; ihr Status ist `in Arbeit`, sonst `geprüft`.

**Kontaktart**
: Die Art der Gegenpartei, mit der du es zu tun hast: Arbeitgeber direkt (Personalabteilung,
  Fachbereich, Geschäftsführung), Personalberatung oder Headhunter, Personalvermittlung oder
  Zeitarbeit, Empfehlung, Jobportal oder unklar. Sie entscheidet, was du wann offenlegst, siehe
  [Gegenpartei](counterparts.md).
