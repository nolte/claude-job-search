# Template of `lebenslauf.md`

Loaded by `job-application-cv-create` when the file is written (step 9). Spec: `spec/job-application/lebenslauf/en.md`
LB-3 (sections and order), LB-9 (closing line), LB-11.12 (frontmatter); `spec/job-application/lebenslauf-versionen/en.md`
LV-2, LV-3; `spec/job-application/konventionen/en.md` R-2.1.

```markdown
---
grundlage_hash: <current hash of the Grundlage>
format: chronologisch | einseitig | kombiniert | ats
situation: <situation chosen for the format, LB-11.12>
auspraegung: <folder name of the variant>
version: <integer, starting at 1>
version_datum: <set only when the Version is frozen, LV-3>
---

# Lebenslauf

## Persönliche Daten
Name · Anschrift · Telefon · E-Mail · LinkedIn (optional) · GitHub/Portfolio (optional)

## Kurzprofil
<optional, at most three sentences of facts; required in kombiniert>

## Berufserfahrung

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Event-Pipeline auf Basis von Python und Kafka betreut; Latenz von 800 ms auf 120 ms gesenkt
- Code-Reviews als Pflichtschritt für ein Team von 5 Entwicklern eingeführt

### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg
- [ERGÄNZEN: Aufgaben]

## Ausbildung und Studium
- 09/2015 – 08/2018: Fachinformatiker Anwendungsentwicklung, Musterfirma GmbH, Berlin

## Schulbildung
- 2015: Abitur, Beispiel-Gymnasium, Hamburg

## Sprachkenntnisse (GER-Niveau)
- Deutsch: Muttersprache
- Englisch: C1

## IT- und Fachkenntnisse
- Programmiersprachen: Python, Go

## Weiterbildung und Zertifikate
- 2022: Zertifikat Beispiel, Beispiel-Akademie, Berlin

Berlin, 23.10.2026
```

Sections follow LB-3 in this order; the optional ones `Praktika`, `Relevante Projekte`, `Ehrenamt` and `Interessen` are
added where they apply. A section without content is omitted (LB-3). The required ones (`Persönliche Daten`,
`Berufserfahrung` unless entry level, `Ausbildung und Studium`, `Schulbildung`, `Sprachkenntnisse`) are required only
where the Grundlage holds content for them; if it holds nothing, the section is omitted without a placeholder and not
reported as a Blocker. Section headings are the standard headings (R-8.3, CG-11.2a). No tables, no columns, no text boxes,
no sub-bullets (CV-17). The closing line is `Ort, TT.MM.JJJJ` with the city of the address and the date of generation
(LB-9.2, LB-9.4); an unknown city is `[ERGÄNZEN: Ort]`.
