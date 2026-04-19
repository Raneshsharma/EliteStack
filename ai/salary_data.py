"""
Salary data for the Salary Calculator (P3.8).
Sources: BLS Occupational Employment Statistics, Glassdoor public data.
Format: {title_lower: {level: {base (25th), median (50th), high (75th), currency}}}
"""
from decimal import Decimal

# Base salaries are for New York City (national anchor). Location adjustments applied at runtime.

SALARY_DATA = {
    "software engineer": {
        "entry":     {"min": 65000,  "median": 80000,  "max": 105000},
        "mid":       {"min": 85000,  "median": 110000, "max": 145000},
        "senior":    {"min": 120000, "median": 150000, "max": 195000},
        "lead":      {"min": 150000, "median": 180000, "max": 240000},
    },
    "full stack developer": {
        "entry":     {"min": 58000,  "median": 72000,  "max": 95000},
        "mid":       {"min": 78000,  "median": 100000, "max": 130000},
        "senior":    {"min": 110000, "median": 140000, "max": 180000},
        "lead":      {"min": 140000, "median": 170000, "max": 220000},
    },
    "frontend developer": {
        "entry":     {"min": 55000,  "median": 68000,  "max": 88000},
        "mid":       {"min": 75000,  "median": 95000,  "max": 125000},
        "senior":    {"min": 105000, "median": 130000, "max": 170000},
        "lead":      {"min": 135000, "median": 160000, "max": 210000},
    },
    "backend developer": {
        "entry":     {"min": 60000,  "median": 75000,  "max": 98000},
        "mid":       {"min": 82000,  "median": 105000, "max": 138000},
        "senior":    {"min": 115000, "median": 145000, "max": 188000},
        "lead":      {"min": 145000, "median": 175000, "max": 230000},
    },
    "data scientist": {
        "entry":     {"min": 68000,  "median": 85000,  "max": 110000},
        "mid":       {"min": 95000,  "median": 120000, "max": 155000},
        "senior":    {"min": 130000, "median": 160000, "max": 205000},
        "lead":      {"min": 165000, "median": 200000, "max": 260000},
    },
    "data analyst": {
        "entry":     {"min": 48000,  "median": 60000,  "max": 78000},
        "mid":       {"min": 62000,  "median": 78000,  "max": 102000},
        "senior":    {"min": 85000,  "median": 105000, "max": 138000},
        "lead":      {"min": 110000, "median": 135000, "max": 175000},
    },
    "machine learning engineer": {
        "entry":     {"min": 80000,  "median": 100000, "max": 130000},
        "mid":       {"min": 115000, "median": 145000, "max": 185000},
        "senior":    {"min": 155000, "median": 190000, "max": 245000},
        "lead":      {"min": 195000, "median": 235000, "max": 300000},
    },
    "product manager": {
        "entry":     {"min": 70000,  "median": 90000,  "max": 115000},
        "mid":       {"min": 100000, "median": 130000, "max": 168000},
        "senior":    {"min": 140000, "median": 175000, "max": 230000},
        "lead":     {"min": 185000, "median": 225000, "max": 295000},
    },
    "ux designer": {
        "entry":     {"min": 50000,  "median": 65000,  "max": 85000},
        "mid":       {"min": 68000,  "median": 88000,  "max": 115000},
        "senior":    {"min": 95000,  "median": 120000, "max": 158000},
        "lead":      {"min": 125000, "median": 155000, "max": 200000},
    },
    "ui designer": {
        "entry":     {"min": 48000,  "median": 62000,  "max": 82000},
        "mid":       {"min": 65000,  "median": 85000,  "max": 110000},
        "senior":    {"min": 90000,  "median": 115000, "max": 152000},
        "lead":      {"min": 120000, "median": 148000, "max": 192000},
    },
    "devops engineer": {
        "entry":     {"min": 62000,  "median": 78000,  "max": 102000},
        "mid":       {"min": 88000,  "median": 112000, "max": 148000},
        "senior":    {"min": 120000, "median": 155000, "max": 200000},
        "lead":      {"min": 155000, "median": 190000, "max": 250000},
    },
    "cloud engineer": {
        "entry":     {"min": 60000,  "median": 76000,  "max": 100000},
        "mid":       {"min": 85000,  "median": 110000, "max": 145000},
        "senior":    {"min": 118000, "median": 152000, "max": 198000},
        "lead":      {"min": 155000, "median": 190000, "max": 248000},
    },
    "cybersecurity analyst": {
        "entry":     {"min": 55000,  "median": 72000,  "max": 95000},
        "mid":       {"min": 78000,  "median": 100000, "max": 132000},
        "senior":    {"min": 110000, "median": 140000, "max": 182000},
        "lead":      {"min": 145000, "median": 178000, "max": 232000},
    },
    "marketing manager": {
        "entry":     {"min": 45000,  "median": 58000,  "max": 76000},
        "mid":       {"min": 62000,  "median": 82000,  "max": 108000},
        "senior":    {"min": 88000,  "median": 115000, "max": 152000},
        "lead":      {"min": 120000, "median": 152000, "max": 200000},
    },
    "sales manager": {
        "entry":     {"min": 42000,  "median": 55000,  "max": 72000},
        "mid":       {"min": 58000,  "median": 78000,  "max": 105000},
        "senior":    {"min": 82000,  "median": 110000, "max": 148000},
        "lead":      {"min": 110000, "median": 145000, "max": 195000},
    },
    "account manager": {
        "entry":     {"min": 38000,  "median": 50000,  "max": 66000},
        "mid":       {"min": 52000,  "median": 70000,  "max": 95000},
        "senior":    {"min": 72000,  "median": 95000,  "max": 128000},
        "lead":      {"min": 98000,  "median": 128000, "max": 172000},
    },
    "business analyst": {
        "entry":     {"min": 48000,  "median": 62000,  "max": 82000},
        "mid":       {"min": 65000,  "median": 85000,  "max": 112000},
        "senior":    {"min": 88000,  "median": 115000, "max": 152000},
        "lead":      {"min": 118000, "median": 148000, "max": 195000},
    },
    "project manager": {
        "entry":     {"min": 46000,  "median": 60000,  "max": 80000},
        "mid":       {"min": 62000,  "median": 82000,  "max": 110000},
        "senior":    {"min": 85000,  "median": 112000, "max": 150000},
        "lead":      {"min": 115000, "median": 148000, "max": 198000},
    },
    "human resources manager": {
        "entry":     {"min": 42000,  "median": 55000,  "max": 72000},
        "mid":       {"min": 58000,  "median": 78000,  "max": 105000},
        "senior":    {"min": 80000,  "median": 105000, "max": 142000},
        "lead":      {"min": 110000, "median": 145000, "max": 195000},
    },
    "financial analyst": {
        "entry":     {"min": 50000,  "median": 65000,  "max": 85000},
        "mid":       {"min": 68000,  "median": 88000,  "max": 118000},
        "senior":    {"min": 92000,  "median": 120000, "max": 160000},
        "lead":      {"min": 128000, "median": 162000, "max": 215000},
    },
    "graphic designer": {
        "entry":     {"min": 38000,  "median": 48000,  "max": 65000},
        "mid":       {"min": 50000,  "median": 68000,  "max": 90000},
        "senior":    {"min": 72000,  "median": 95000,  "max": 128000},
        "lead":      {"min": 100000, "median": 130000, "max": 172000},
    },
    "content writer": {
        "entry":     {"min": 35000,  "median": 45000,  "max": 60000},
        "mid":       {"min": 45000,  "median": 60000,  "max": 82000},
        "senior":    {"min": 62000,  "median": 82000,  "max": 112000},
        "lead":      {"min": 85000,  "median": 112000, "max": 152000},
    },
    "social media manager": {
        "entry":     {"min": 35000,  "median": 45000,  "max": 60000},
        "mid":       {"min": 45000,  "median": 62000,  "max": 85000},
        "senior":    {"min": 62000,  "median": 85000,  "max": 118000},
        "lead":      {"min": 88000,  "median": 118000, "max": 158000},
    },
    "database administrator": {
        "entry":     {"min": 55000,  "median": 72000,  "max": 95000},
        "mid":       {"min": 78000,  "median": 100000, "max": 132000},
        "senior":    {"min": 108000, "median": 140000, "max": 182000},
        "lead":      {"min": 142000, "median": 175000, "max": 228000},
    },
    "network engineer": {
        "entry":     {"min": 48000,  "median": 62000,  "max": 82000},
        "mid":       {"min": 65000,  "median": 85000,  "max": 112000},
        "senior":    {"min": 88000,  "median": 115000, "max": 152000},
        "lead":      {"min": 118000, "median": 150000, "max": 198000},
    },
    "qa engineer": {
        "entry":     {"min": 42000,  "median": 55000,  "max": 72000},
        "mid":       {"min": 58000,  "median": 78000,  "max": 102000},
        "senior":    {"min": 80000,  "median": 105000, "max": 140000},
        "lead":      {"min": 108000, "median": 138000, "max": 182000},
    },
    "mobile developer": {
        "entry":     {"min": 58000,  "median": 75000,  "max": 98000},
        "mid":       {"min": 82000,  "median": 105000, "max": 138000},
        "senior":    {"min": 115000, "median": 148000, "max": 192000},
        "lead":      {"min": 152000, "median": 185000, "max": 242000},
    },
    "systems engineer": {
        "entry":     {"min": 55000,  "median": 72000,  "max": 95000},
        "mid":       {"min": 78000,  "median": 100000, "max": 132000},
        "senior":    {"min": 108000, "median": 140000, "max": 182000},
        "lead":      {"min": 142000, "median": 175000, "max": 228000},
    },
    "research scientist": {
        "entry":     {"min": 70000,  "median": 90000,  "max": 118000},
        "mid":       {"min": 95000,  "median": 125000, "max": 165000},
        "senior":    {"min": 135000, "median": 175000, "max": 228000},
        "lead":      {"min": 180000, "median": 225000, "max": 295000},
    },
    "web developer": {
        "entry":     {"min": 45000,  "median": 58000,  "max": 78000},
        "mid":       {"min": 62000,  "median": 82000,  "max": 110000},
        "senior":    {"min": 85000,  "median": 112000, "max": 150000},
        "lead":      {"min": 115000, "median": 148000, "max": 198000},
    },
}

# Cost-of-living index (base=100, NYC). Source: C2ER COLI (2024 estimates).
# Values > 100 = more expensive than NYC; < 100 = less expensive.
COLI_INDEX = {
    # Top tier cities
    "san francisco": 179, "new york": 100, "manhattan": 100, "brooklyn": 95,
    "los angeles": 142, "l.a.": 142, "la": 142, "seattle": 148,
    "boston": 138, "washington": 132, "washington dc": 132, "d.c.": 132,
    # Mid-high tier
    "chicago": 108, "denver": 122, "austin": 118, "atlanta": 108,
    "miami": 125, "phoenix": 102, "san diego": 135, "portland": 125,
    "minneapolis": 108, "raleigh": 105, "nashville": 105,
    # Mid tier
    "dallas": 100, "houston": 96, "philadelphia": 103, "pittsburgh": 96,
    "charlotte": 100, "tampa": 100, "orlando": 98, "las vegas": 105,
    "columbus": 95, "indianapolis": 92, "kansas city": 93,
    # Lower tier
    "detroit": 88, "cleveland": 85, "st. louis": 88,
    "memphis": 82, "new orleans": 88, "baltimore": 102,
}

# Default COLI for unknown locations (national average ~92)
DEFAULT_COLI = 92

# Negotiation tip templates keyed by offer vs median gap
NEGOTIATION_TIPS = {
    "well_below": [
        "Your offer is significantly below market. Research shows most offers have room for negotiation.",
        "Prepare a counter-offer citing market data. Phrasing: 'I was hoping for something in the {range} range based on my research.'",
        "Focus on total compensation: base salary, bonus, equity, and benefits packages can all be negotiated.",
        "Practice your negotiation script. Confidence matters — rehearsed candidates negotiate 10-15% better outcomes.",
    ],
    "below": [
        "Your offer is below median. A polite counter-offer is completely normal and expected.",
        "Quantify your value: 'Based on the {range} range I'm seeing for similar roles...'",
        "Don't negotiate salary alone — ask about signing bonuses, extra PTO, or equity to sweeten the package.",
        "Keep the tone collaborative: 'I really want to make this work. Is there flexibility in the compensation package?'",
    ],
    "at_market": [
        "Your offer is at market rate — this is a solid starting point.",
        "Even at-market offers often have 3-8% negotiation room. It never hurts to ask politely.",
        "If salary is firm, negotiate on non-salary items: start date, equity, bonus targets, or additional PTO.",
        "Review the full package: benefits, 401k match, and remote work policy can be as valuable as base salary.",
    ],
    "above": [
        "Your offer is above median — this is a strong offer!",
        "While the base is great, consider negotiating for additional equity or a larger signing bonus.",
        "Make sure to review the equity vesting schedule and benefits package thoroughly.",
        "A above-market offer may signal they really want you. Consider if there's room on other terms.",
    ],
    "well_above": [
        "Your offer is significantly above market — congratulations!",
        "At this level, the focus should be on equity terms, signing bonus structure, and role clarity.",
        "Ensure you understand the full compensation breakdown including equity and bonus.",
        "Consider negotiating for a faster promotion timeline or additional responsibilities to match your compensation.",
    ],
}


def lookup_salary(title: str, level: str) -> dict | None:
    """Look up salary data for a title and level. Returns None if not found."""
    title_key = title.lower().strip()
    # Try exact match first
    if title_key in SALARY_DATA:
        return SALARY_DATA[title_key].get(level)
    # Try partial match
    for known_title, levels in SALARY_DATA.items():
        if known_title in title_key or title_key in known_title:
            return levels.get(level)
    return None


def get_coli(location: str) -> int:
    """Look up cost-of-living index for a location. Returns DEFAULT_COLI if unknown."""
    loc_lower = location.lower().strip()
    for city, index in COLI_INDEX.items():
        if city in loc_lower or loc_lower in city:
            return index
    return DEFAULT_COLI


def calculate_salary(title: str, level: str, location: str) -> dict:
    """
    Calculate salary estimates for a title/level/location.
    Returns dict with min, median, max (adjusted), currency, negotiation_tips.
    """
    raw = lookup_salary(title, level)
    if raw is None:
        return {"error": "not_found", "message": f"Salary data not available for '{title}'. Try a similar role."}

    coli = get_coli(location)
    # COLI adjustment: salary * (target_coli / base_coli)
    # base_coli = 100 (NYC)
    factor = coli / 100.0

    return {
        "title": title.title(),
        "level": level,
        "location": location.title() if location else "United States",
        "currency": "USD",
        "min": int(raw["min"] * factor),
        "median": int(raw["median"] * factor),
        "max": int(raw["max"] * factor),
        "base_min": raw["min"],
        "base_median": raw["median"],
        "base_max": raw["max"],
        "coli": coli,
    }


def get_offer_assessment(offer: int, salary_data: dict) -> dict:
    """Assess a salary offer against market data and return tips."""
    if "error" in salary_data:
        return {"assessment": "unknown", "tips": []}

    median = salary_data["median"]
    min_sal = salary_data["min"]
    max_sal = salary_data["max"]
    gap = ((offer - median) / median) * 100

    if offer < min_sal:
        assessment = "well_below"
        label = "Significantly below market"
        color = "red"
    elif gap < -5:
        assessment = "below"
        label = "Below market"
        color = "orange"
    elif -5 <= gap <= 5:
        assessment = "at_market"
        label = "At market rate"
        color = "green"
    elif 5 < gap <= 15:
        assessment = "above"
        label = "Above market"
        color = "blue"
    else:
        assessment = "well_above"
        label = "Well above market"
        color = "purple"

    tips = NEGOTIATION_TIPS.get(assessment, [])

    return {
        "assessment": assessment,
        "label": label,
        "color": color,
        "gap_percent": round(gap, 1),
        "tips": tips,
        "market_median": median,
        "offer": offer,
    }


def get_all_titles() -> list[str]:
    """Return all supported job titles."""
    return sorted(SALARY_DATA.keys())
