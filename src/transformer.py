import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from parsers.csv_parser import parse_csv
from parsers.json_parser import parse_json
from parsers.txt_parser import parse_txt
from normalizers import normalize_phone, normalize_city_region, normalize_skills
from merger import merge_candidates

def transform(sources: dict) -> list:
    """
    Main pipeline:
    1. Parse each source
    2. Normalize fields
    3. Group by candidate_id
    4. Merge groups
    """

    all_records = {}  # { candidate_id: [records] }

    # ── STEP 1: Parse ──────────────────────────────────────────
    raw_records = []

    if "csv" in sources:
        raw_records.extend(parse_csv(sources["csv"]))

    if "json" in sources:
        raw_records.extend(parse_json(sources["json"]))

    if "txt" in sources:
        raw_records.extend(parse_txt(sources["txt"]))

    # ── STEP 2: Normalize each record ──────────────────────────
    for rec in raw_records:
        source = rec.get("source", "unknown")

        # Normalize phones
        rec["phones"] = []
        for raw_ph in rec.get("phones_raw", []):
            normalized = normalize_phone(str(raw_ph))
            if normalized:
                rec["phones"].append(normalized)

        # Normalize location
        rec["location"] = normalize_city_region(rec.get("location_raw"))
        
        # Pass experience through
        if "experience" not in rec:
            rec["experience"] = []
        # Normalize skills
        rec["skills"] = normalize_skills(
            rec.get("skills_raw", []), source=source
        )

    # ── STEP 3: Group by candidate_id ──────────────────────────
    unmatched = []

    for rec in raw_records:
        cid = rec.get("candidate_id")
        if cid and cid != "None":
            all_records.setdefault(cid, []).append(rec)
        else:
            # Try to match unstructured records by email
            matched = False
            for existing_records in all_records.values():
                existing_emails = set()
                for er in existing_records:
                    existing_emails.update(er.get("emails", []))
                if any(e in existing_emails for e in rec.get("emails", [])):
                    existing_records.append(rec)
                    matched = True
                    break
            if not matched:
                unmatched.append(rec)

    # Add unmatched as their own group
    for i, rec in enumerate(unmatched):
        key = f"unmatched_{i}"
        all_records[key] = [rec]

    # ── STEP 4: Merge each group ────────────────────────────────
    results = []
    for cid, records in all_records.items():
        merged = merge_candidates(records)
        if not merged["candidate_id"]:
            merged["candidate_id"] = cid
        results.append(merged)

    print(f"\n✅ Pipeline complete: {len(results)} canonical profiles produced")
    return results