import pandas as pd

def parse_csv(filepath):
    df = pd.read_csv(filepath)
    records = []
    
    for _, row in df.iterrows():
        skills_raw = []
        if pd.notna(row.get("skills", "")):
            skills_raw = [s.strip() for s in str(row["skills"]).split(",")]
        
        record = {
            "source": "csv",
            "candidate_id": str(row.get("candidate_id", "")).strip(),
            "full_name": str(row.get("name", "")).strip() if pd.notna(row.get("name")) else None,
            "emails": [str(row["email"]).strip()] if pd.notna(row.get("email")) else [],
            "phones_raw": [str(row["phone"]).strip()] if pd.notna(row.get("phone")) else [],
            "location_raw": str(row.get("location", "")).strip() if pd.notna(row.get("location")) else None,
            "links": {
                "linkedin": str(row["linkedin"]).strip() if pd.notna(row.get("linkedin")) else None
            },
            "experience": [{
    "company": str(row["company"]).strip() if pd.notna(row.get("company")) else None,
    "title": str(row["title"]).strip() if pd.notna(row.get("title")) else None,
    "start": None,
    "end": None,
    "summary": None
}] if pd.notna(row.get("company")) else [],
            "skills_raw": skills_raw
        }
        records.append(record)
    
    print(f"✅ CSV parsed: {len(records)} candidates found")
    return records