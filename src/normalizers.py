import phonenumbers
import pycountry
import re

def normalize_phone(raw_phone, default_country="IN"):
    """Convert any phone format to E.164 e.g. +919876543210"""
    try:
        raw = str(raw_phone).strip()
        # Remove spaces and dashes
        raw = re.sub(r'[\s\-\(\)]', '', raw)
        parsed = phonenumbers.parse(raw, default_country)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
    except Exception:
        pass
    return None


def normalize_country(raw_location):
    """Extract ISO-3166 alpha-2 country code from location string"""
    if not raw_location:
        return None
    try:
        # Try each word/part as a country
        parts = raw_location.replace(",", " ").split()
        # Try full string first, then last word, then each word
        attempts = [raw_location] + [parts[-1]] + parts
        for attempt in attempts:
            try:
                results = pycountry.countries.search_fuzzy(attempt.strip())
                if results:
                    return results[0].alpha_2
            except Exception:
                continue
    except Exception:
        pass
    return None

def normalize_city_region(raw_location):
    """Extract city and region from location string"""
    if not raw_location:
        return {"city": None, "region": None, "country": None}

    # Handle "City Country" (no comma) vs "City, Country"
    if "," in raw_location:
        parts = [p.strip() for p in raw_location.split(",")]
    else:
        parts = [p.strip() for p in raw_location.split(" ")]
        # Last word is likely country, rest is city
        parts = [" ".join(parts[:-1]), parts[-1]]

    city = parts[0] if parts[0] else None
    region = parts[1] if len(parts) > 1 else None
    country = normalize_country(raw_location)

    # Don't put country name into region field
    if region and country:
        try:
            import pycountry
            found = pycountry.countries.search_fuzzy(region)
            if found and found[0].alpha_2 == country:
                region = None
        except Exception:
            pass

    return {"city": city, "region": region, "country": country}

def normalize_skills(skills_list, source="unknown"):
    """Return canonical skill objects"""
    canonical_map = {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "py": "Python",
        "python": "Python",
        "ml": "Machine Learning",
        "machine learning": "Machine Learning",
        "aws": "AWS",
        "docker": "Docker",
        "java": "Java",
        "agile": "Agile",
        "roadmapping": "Roadmapping",
    }
    
    result = []
    seen = set()
    
    for skill in skills_list:
        if not skill:
            continue
        canonical = canonical_map.get(skill.lower(), skill.strip().title())
        if canonical not in seen:
            seen.add(canonical)
            result.append({
                "name": canonical,
                "confidence": 0.9,
                "sources": [source]
            })
    
    return result