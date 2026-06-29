def merge_candidates(records):
    """
    Merge multiple source records for same candidate.
    Strategy: first non-null wins, lists are merged uniquely.
    """
    merged = {
        "candidate_id": None,
        "full_name": None,
        "emails": [],
        "phones": [],
        "location": {"city": None, "region": None, "country": None},
        "links": {"linkedin": None, "github": None, "portfolio": None, "other": []},
        "headline": None,
        "years_experience": None,
        "skills": [],
        "experience": [],
        "education": [],
        "provenance": [],
        "overall_confidence": 0.0
    }

    confidence_scores = []

    for record in records:
        source = record.get("source", "unknown")

        # candidate_id
        if not merged["candidate_id"] and record.get("candidate_id"):
            merged["candidate_id"] = record["candidate_id"]
            merged["provenance"].append({
                "field": "candidate_id", "source": source, "method": "direct"
            })

        # full_name
        if not merged["full_name"] and record.get("full_name"):
            merged["full_name"] = record["full_name"]
            merged["provenance"].append({
                "field": "full_name", "source": source, "method": "direct"
            })
            confidence_scores.append(1.0)

        # emails
        for email in record.get("emails", []):
            if email and email not in merged["emails"]:
                merged["emails"].append(email)
                merged["provenance"].append({
                    "field": "emails", "source": source, "method": "direct"
                })

        # phones
        for phone in record.get("phones", []):
            if phone and phone not in merged["phones"]:
                merged["phones"].append(phone)
                merged["provenance"].append({
                    "field": "phones", "source": source, "method": "normalized"
                })

        # location
        loc = record.get("location", {})
        if isinstance(loc, dict):
            for key in ["city", "region", "country"]:
                if not merged["location"][key] and loc.get(key):
                    merged["location"][key] = loc[key]

        # links
        rec_links = record.get("links", {})
        for key in ["linkedin", "github", "portfolio"]:
            if not merged["links"][key] and rec_links.get(key):
                merged["links"][key] = rec_links[key]

        # headline
        if not merged["headline"] and record.get("headline"):
            merged["headline"] = record["headline"]
            confidence_scores.append(0.9)

        # years_experience
        if merged["years_experience"] is None and record.get("years_experience") is not None:
            merged["years_experience"] = record["years_experience"]

        # skills - merge by name
        existing_names = {s["name"] for s in merged["skills"]}
        for skill in record.get("skills", []):
            if skill["name"] not in existing_names:
                merged["skills"].append(skill)
                existing_names.add(skill["name"])

        # experience
        for exp in record.get("experience", []):
            if exp not in merged["experience"]:
                merged["experience"].append(exp)

    # overall confidence
    if confidence_scores:
        merged["overall_confidence"] = round(
            sum(confidence_scores) / len(confidence_scores), 2
        )
    else:
        merged["overall_confidence"] = 0.5

    return merged