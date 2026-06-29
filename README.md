# Eightfold Multi-Source Candidate Data Transformer

## Problem
Eightfold ingests candidate information from many sources at once.
The same person may appear in a recruiter CSV, an ATS JSON export,
and free-text recruiter notes — each with different field names,
formats, and confidence levels. This pipeline turns those messy
inputs into one clean, canonical profile per candidate.

## Pipeline Design
detect → extract → normalize → merge → validate → output
| Stage | What happens |
|-------|-------------|
| detect | Identify source type (CSV / JSON / TXT) |
| extract | Parse fields using source-specific parser |
| normalize | E.164 phones, ISO-3166 countries, canonical skills |
| merge | Group by candidate_id, email-match unstructured sources |
| validate | Null missing fields, never crash on bad input |
| output | Schema-valid JSON, one object per candidate |

## Project Structure
eightfold-transformer/

├── src/

│   ├── parsers/

│   │   ├── csv_parser. py       # Recruiter CSV export

│   │   ├── json_parser.py      # ATS JSON blob

│   │   └── txt_parser.py       # Recruiter notes (unstructured)

│   ├── normalizers.py          # Phone E.164, country ISO-3166, skills

│   ├── merger.py               # Conflict resolution + provenance

│   ├── config_loader.py        # Runtime field projection

│   └── transformer.py          # Main pipeline orchestrator

├── config/

│   └── default_config.json     # Field mapping config

├── samples/

│   ├── recruiter_export.csv    # Structured sample input

│   ├── ats_data.json           # Structured sample input

│   └── recruiter_notes.txt     # Unstructured sample input

├── cli.py                      # Command-line interface

└── README.md
## How to Run

### Install dependencies
```bash
pip3 install pandas pdfplumber phonenumbers pycountry
```

### Basic run (all 3 source types)
```bash
python3 cli.py \
  --csv samples/recruiter_export.csv \
  --json samples/ats_data.json \
  --txt samples/recruiter_notes.txt
```

### Save output to file
```bash
python3 cli.py \
  --csv samples/recruiter_export.csv \
  --json samples/ats_data.json \
  --txt samples/recruiter_notes.txt \
  --output output.json
```

### Run with custom config
```bash
python3 cli.py \
  --csv samples/recruiter_export.csv \
  --config config/default_config.json \
  --output output.json
```

### Run with only one source (pipeline never crashes)
```bash
python3 cli.py --csv samples/recruiter_export.csv
python3 cli.py --json samples/ats_data.json
python3 cli.py --txt samples/recruiter_notes.txt
```

## Output Schema
Each candidate produces one JSON object:
```json
{
  "candidate_id": "C001",
  "full_name": "Rahul Sharma",
  "emails": ["rahul@gmail.com"],
  "phones": ["+919876543210"],
  "location": { "city": "Bangalore", "region": null, "country": "IN" },
  "links": { "linkedin": "...", "github": "...", "portfolio": null, "other": [] },
  "headline": "Senior Software Engineer at Google",
  "years_experience": 5,
  "skills": [{ "name": "Python", "confidence": 0.9, "sources": ["csv"] }],
  "experience": [{ "company": "Google", "title": "Software Engineer", "start": null, "end": null, "summary": null }],
  "education": [],
  "provenance": [{ "field": "emails", "source": "csv", "method": "direct" }],
  "overall_confidence": 0.95
}
```

## Edge Cases Handled

| Edge Case | Behaviour |
|-----------|-----------|
| Missing phone | `null` — never crashes |
| Malformed phone number | Skipped, not included |
| Duplicate emails across sources | Deduplicated |
| Conflicting names | CSV preferred over unstructured notes |
| Unknown country string | Fuzzy-matched, falls back to `null` |
| Unstructured TXT with no ID | Matched to structured record by email |
| Empty or missing field | Returns `null`, omit option via config |
| Garbage / extra source input | Isolated as own profile, not dropped |

## Design Decisions

- **Deterministic**: same inputs always produce same output
- **Robust**: missing or garbage source never crashes the run  
- **Explainable**: every field has a provenance entry showing source and method
- **Configurable**: runtime config controls field projection, renaming, missing-value handling