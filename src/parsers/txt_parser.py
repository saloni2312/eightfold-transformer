import re

def parse_txt(filepath):
    with open(filepath, "r") as f:
        text = f.read()
    
    # Split into blocks per candidate (separated by blank lines)
    blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
    
    records = []
    for block in blocks:
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[a-zA-Z]+', block)
        phones = re.findall(r'\+?\d[\d\s\-]{8,}\d', block)
        github = re.findall(r'github\.com/[\w\-]+', block)
        
        # Extract name from first line
        first_line = block.split("\n")[0]
        name = first_line.split("-")[0].strip() if "-" in first_line else first_line.strip()
        
        record = {
            "source": "recruiter_notes",
            "candidate_id": None,
            "full_name": name if name else None,
            "emails": emails,
            "phones_raw": phones,
            "skills_raw": [],
            "location_raw": None,
            "links": {
                "github": github[0] if github else None
            },
            "raw_text": block
        }
        records.append(record)
    
    print(f"✅ TXT parsed: {len(records)} candidate blocks found")
    return records