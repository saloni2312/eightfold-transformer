import json

def parse_json(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    
    records = []
    for item in data:
        record = {
            "source": "ats_json",
            "candidate_id": str(item.get("id", "")).strip(),
            "full_name": item.get("full_name", None),
            "emails": [item["primary_email"]] if item.get("primary_email") else [],
            "phones_raw": [],
            "skills_raw": item.get("skills", []),
            "location_raw": item.get("location", None),
            "years_experience": item.get("years_experience", None),
            "headline": item.get("headline", None),
            "links": {}
        }
        records.append(record)
    
    print(f"✅ JSON parsed: {len(records)} candidates found")
    return records