"""Shared OpenAI client for all AI features."""
import logging
import openai
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")
        _client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def call_openai(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    """Call OpenAI chat completion. Raises on error."""
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_resume_rewrites(original_text: str) -> list[str]:
    """Generate 3 resume bullet rewrites. Returns list of 3 strings."""
    system_prompt = (
        "You are a professional resume writer. Rewrite the following resume bullet point "
        "to be more specific, action-oriented, and ATS-friendly. "
        "Return exactly 3 alternatives, each on a separate line starting with '1. ', '2. ', '3. '. "
        "Do not add any extra text, numbering beyond 1/2/3, or commentary."
    )
    user_prompt = f"Resume bullet:\n{original_text}"
    result = call_openai(system_prompt, user_prompt, max_tokens=600)

    rewrites = []
    for line in result.splitlines():
        line = line.strip()
        # Strip "1. ", "2. ", "3. " prefix if present
        for prefix in ('1. ', '2. ', '3. '):
            if line.startswith(prefix):
                line = line[len(prefix):]
                break
        if line:
            rewrites.append(line)
        if len(rewrites) >= 3:
            break

    # If we got fewer than 3, pad with what we have (avoid empty strings)
    while len(rewrites) < 3:
        rewrites.append(rewrites[-1] if rewrites else "[Could not generate rewrite]")
    return rewrites[:3]


def generate_cover_letter(
    resume_data: str,
    job_title: str,
    company_name: str,
    hiring_manager_name: str,
    job_description: str,
) -> str:
    """Generate a cover letter from resume data and job info."""
    system_prompt = (
        "You are a professional cover letter writer. Write a complete, personalized cover letter "
        "of 300-500 words. Use a professional tone. Include: your interest in the role, "
        "relevant skills and experience from the resume, and a strong closing. "
        "Do not invent any facts not present in the resume data."
    )
    salutation = f"Dear {hiring_manager_name}," if hiring_manager_name else "Dear Hiring Team,"
    user_prompt = (
        f"Resume:\n{resume_data}\n\n"
        f"Job Title: {job_title}\n"
        f"Company: {company_name}\n"
        f"{salutation}\n\n"
        f"Job Description (if provided):\n{job_description}"
    )
    letter = call_openai(system_prompt, user_prompt, max_tokens=800)
    # Prepend salutation if not already at start
    if not letter.strip().lower().startswith('dear'):
        letter = f"{salutation}\n\n{letter}"
    return letter


def generate_job_match(
    resume_data: str,
    job_description: str,
    sections: list[str],
) -> dict:
    """Analyze job description and rewrite resume sections to match keywords."""
    system_prompt = (
        "You are an expert resume tailor. Analyze the job description and resume. "
        "Rewrite the requested sections to incorporate relevant keywords and phrasing "
        "from the job description while maintaining factual accuracy. "
        "Return a JSON object with keys: 'match_score' (0-100 integer), "
        "'rewritten_sections' (dict of section_name -> rewritten text), "
        "'keywords_found' (list of strings), 'keywords_matched' (list of strings), "
        "'recommendations' (list of strings). "
        "Do not invent skills or experiences not present in the resume."
    )
    user_prompt = (
        f"Resume:\n{resume_data}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Sections to rewrite: {', '.join(sections)}"
    )
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        response_format={"type": "json_object"},
    )
    import json
    result = json.loads(response.choices[0].message.content.strip())
    return result


def analyze_ats_score(
    resume_data: str,
    job_description: str,
) -> dict:
    """Analyze a resume against a job description and return ATS scoring data."""
    system_prompt = (
        "You are an expert ATS (Applicant Tracking System) analyzer. "
        "Analyze the resume against the job description and return a detailed JSON analysis. "
        "Return a JSON object with these exact keys:\n"
        "- 'overall_score': integer 0-100 (weighted average of sub-scores)\n"
        "- 'keyword_score': integer 0-100 (how many job keywords are in the resume)\n"
        "- 'formatting_score': integer 0-100 (how ATS-friendly is the format)\n"
        "- 'readability_score': integer 0-100 (target Flesch-Kincaid grade 8-12)\n"
        "- 'length_score': integer 0-100 (optimal: 1 page=100, 1-2 pages=80, too short=60, too long=40)\n"
        "- 'missing_keywords': list of strings (key skills/requirements from job not in resume)\n"
        "- 'matched_keywords': list of strings (keywords present in both resume and job)\n"
        "- 'recommendations': list of strings (specific actionable fixes)\n"
        "Be honest and strict. ATS systems are unforgiving."
    )
    user_prompt = (
        f"Resume:\n{resume_data}\n\n"
        f"Job Description:\n{job_description}"
    )
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1200,
        response_format={"type": "json_object"},
    )
    result = json.loads(response.choices[0].message.content.strip())
    return result


CHAT_SYSTEM_PROMPT = (
    "You are a helpful career and resume assistant for Placement Copilot. "
    "You help users with: resume writing tips, cover letter advice, job search strategies, "
    "interview preparation, LinkedIn profile optimization, and career guidance. "
    "Be concise, actionable, and encouraging. "
    "Never invent facts about the user — only use information they share with you. "
    "If you don't know something, say so honestly."
)


def chat_with_assistant(
    messages: list[dict],
    max_tokens: int = 500,
) -> str:
    """Send a conversation to OpenAI and return the assistant's reply."""
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "system", "content": CHAT_SYSTEM_PROMPT}] + messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_interview_questions(
    resume_data: str,
    job_title: str,
    job_description: str,
    num_questions: int = 12,
) -> list[dict]:
    """Generate interview questions (behavioral, situational, technical, culture)."""
    import json
    system_prompt = (
        "You are an expert interview coach. Based on the resume and job description, "
        "generate interview questions for a candidate. Return a JSON array of objects "
        "with these exact fields for each question:\n"
        "- 'text': the question string\n"
        "- 'category': one of 'behavioral', 'situational', 'technical', 'culture'\n"
        "- 'answer_framework': a brief framework/guide (2-4 sentences) for answering this type of question\n"
        "Aim for roughly equal distribution across categories. "
        "Return exactly the requested number of questions. "
        "Return only the JSON array — no preamble or explanation."
    )
    user_prompt = (
        f"Job Title: {job_title}\n\n"
        f"Resume:\n{resume_data}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Generate {num_questions} interview questions."
    )
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1500,
        response_format={"type": "json_object"},
    )
    result = json.loads(response.choices[0].message.content.strip())
    # Accept both {"questions": [...]} and direct [...]
    questions = result.get("questions", result) if isinstance(result, dict) else result
    if not isinstance(questions, list):
        questions = []
    return questions


def generate_email_template(
    resume_data: str,
    email_type: str,
    recipient_name: str,
    job_title: str,
    company_name: str,
    custom_notes: str = "",
) -> str:
    """Generate a professional email template."""
    system_prompt = (
        "You are a professional career communications writer. "
        f"Write a complete, professional email of 150-300 words. "
        f"Type: {email_type}. "
        "Use a warm but professional tone. "
        "Return only the email body text — no subject line, no salutation (recipient name is provided), "
        "no sign-off. Start directly with the opening paragraph. "
        "Do not invent any facts not present in the resume data."
    )
    user_prompt = (
        f"Resume:\n{resume_data}\n\n"
        f"Email Type: {email_type}\n"
        f"Recipient: {recipient_name}\n"
        f"Job Title: {job_title}\n"
        f"Company: {company_name}\n"
        f"Custom Notes: {custom_notes or 'None'}"
    )
    body = call_openai(system_prompt, user_prompt, max_tokens=600)
    return body


def optimize_linkedin_profile(
    headline: str,
    summary: str,
    experience_items: str,
    skills: str,
    job_title: str,
    target_industry: str,
) -> dict:
    """Analyze and optimize a LinkedIn profile."""
    import json
    system_prompt = (
        "You are a LinkedIn profile optimization expert. "
        "Review the profile sections and return a JSON object with:\n"
        "- 'headline_score': integer 0-100\n"
        "- 'headline_tips': list of strings (specific actionable tips for the headline)\n"
        "- 'summary_score': integer 0-100\n"
        "- 'summary_tips': list of strings (tips for the About/summary section)\n"
        "- 'experience_score': integer 0-100\n"
        "- 'experience_tips': list of strings (tips for experience entries)\n"
        "- 'skills_suggestions': list of strings (relevant skills to add)\n"
        "- 'overall_score': integer 0-100 (weighted average)\n"
        "- 'top_priority': string (the single most impactful improvement)\n"
        "- 'headline_suggestion': string (a suggested revised headline)\n"
        "- 'summary_suggestion': string (2-3 sentence improved summary opening)\n"
        "Be specific and actionable. Score honestly."
    )
    user_prompt = (
        f"Target Role: {job_title}\n"
        f"Target Industry: {target_industry}\n\n"
        f"Current Headline: {headline}\n\n"
        f"Current Summary:\n{summary}\n\n"
        f"Experience:\n{experience_items}\n\n"
        f"Skills: {skills}"
    )
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1200,
        response_format={"type": "json_object"},
    )
    result = json.loads(response.choices[0].message.content.strip())
    return result