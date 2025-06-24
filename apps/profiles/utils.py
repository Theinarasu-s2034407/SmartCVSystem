import boto3
import fitz  # PyMuPDF
import io
import re
import logging
import datetime

SKILL_KEYWORDS = [
    # Frontend
    'javascript', 'typescript', 'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt.js',
    'html', 'html 5', 'css', 'scss', 'sass', 'bootstrap', 'tailwind', 'material-ui', 'redux',
    # Backend
    'python', 'django', 'flask', 'fastapi', 'node', 'node.js', 'express', 'java', 'spring', 'spring boot',
    'php', 'laravel', 'symfony', 'ruby', 'rails', 'go', 'golang', 'c#', '.net', 'asp.net', 'kotlin',
    'graphql', 'rest', 'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'docker', 'git', 'aws', 'firebase',
    # Mobile
    'android', 'kotlin', 'java', 'swift', 'ios', 'react native', 'flutter', 'dart', 'xamarin', 'cordova', 'ionic'
]

DATE_PATTERNS = [
    r'(\d{2}/\d{4})\s*[-–]\s*(\d{2}/\d{4}|present)',
    r'([A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*([A-Za-z]{3,9}\s+\d{4}|present)',
    r'(\d{2}-\d{4})\s*[-–]\s*(\d{2}-\d{4}|present)',
    r'(\d{4})\s*[-–]\s*(\d{4}|present)',
    r'([A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*(\d{4}|present)',
    r'(\d{4})\s*[-–]\s*([A-Za-z]{3,9}\s+\d{4}|present)',
    r'([A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*(\d{2}/\d{4}|present)',
    r'(\d{2}/\d{4})\s*[-–]\s*([A-Za-z]{3,9}\s+\d{4}|present)',
    r'(\d{2}-\d{4})\s*[-–]\s*([A-Za-z]{3,9}\s+\d{4}|present)',
    r'([A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*(\d{2}-\d{4}|present)',
]

EDUCATION_LEVELS = [
    ("bachelor", "Bachelor's"),
    ("master", "Master's"),
    ("diploma", "Diploma"),
    ("phd", "PhD"),
    ("doctor of philosophy", "PhD"),
    ("high school", "High School"),
]

EXPERIENCE_PATTERNS = [
    (r"([6-9]|[1-9][0-9]+)\s*(\+)?\s*(years|yrs)", "Senior"),
    (r"(3|4)\s*(years|yrs)", "Mid"),
    (r"(0|1|2)\s*(years|yrs)", "Junior"),
    (r"\bintern(ship)?\b", "Junior")
]

def parse_date(date_str):
    date_str = date_str.strip().replace('-', '/')
    if date_str.lower() == 'present':
        return datetime.datetime.now()
    for fmt in ("%m/%Y", "%b %Y", "%B %Y", "%m-%Y", "%Y"):
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def merge_periods(periods):
    periods.sort()
    merged = []
    for period in periods:
        if not merged:
            merged.append(period)
        else:
            last_start, last_end = merged[-1]
            curr_start, curr_end = period
            if curr_start <= last_end + datetime.timedelta(days=31):
                merged[-1] = (last_start, max(last_end, curr_end))
            else:
                merged.append(period)
    return merged

def extract_resume_info_from_s3(bucket_name, key, aws_access_key=None, aws_secret_key=None, region='us-east-1'):
    fallback_resume_data = {
        "skills": "",
        "education_level": "Unknown",
        "experience_level": "unknown"
    }
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        s3_object = s3.get_object(Bucket=bucket_name, Key=key)
        file_stream = io.BytesIO(s3_object['Body'].read())
    except Exception as e:
        logging.error(f"[S3 Read Error] {e}")
        return fallback_resume_data

    try:
        doc = fitz.open(stream=file_stream, filetype="pdf")
        full_text = "\n".join(page.get_text() for page in doc)
        full_text_lower = full_text.lower()
    except Exception as e:
        logging.error(f"[PDF Parse Error] {e}")
        return fallback_resume_data

    resume_data = {
        "skills": "",
        "education_level": "Unknown",
        "experience_level": "unknown"
    }

    # --- Skill Extraction ---
    found_skills = {kw.capitalize() for kw in SKILL_KEYWORDS if re.search(rf'\b{re.escape(kw)}\b', full_text_lower)}
    resume_data["skills"] = ", ".join(sorted(found_skills))

    # --- Education Extraction ---
    for keyword, label in EDUCATION_LEVELS:
        if keyword in full_text_lower:
            resume_data["education_level"] = label
            break

    # --- Experience Extraction ---
    matches = []
    for pattern in DATE_PATTERNS:
        matches += re.findall(pattern, full_text, re.IGNORECASE)

    periods = []
    for match in matches:
        start_str, end_str = match
        start = parse_date(start_str)
        end = parse_date(end_str)
        if start and end and end >= start:
            periods.append((start, end))

    merged = merge_periods(periods)
    total_months = sum(
        (end.year - start.year) * 12 + (end.month - start.month)
        for start, end in merged if (end.year - start.year) * 12 + (end.month - start.month) > 0
    )
    total_years = total_months / 12

    if total_years >= 6:
        resume_data["experience_level"] = "Senior"
    elif total_years >= 3:
        resume_data["experience_level"] = "Mid"
    elif total_years > 0:
        resume_data["experience_level"] = "Junior"
    else:
        for pattern, level in EXPERIENCE_PATTERNS:
            if re.search(pattern, full_text_lower):
                resume_data["experience_level"] = level
                break

    return resume_data