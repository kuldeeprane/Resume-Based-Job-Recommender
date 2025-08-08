import re

def format_job_description(text: str) -> str:
    """
    Parses a raw job description string and formats it with Markdown headers and colons.
    """
    if not isinstance(text, str):
        return "No description available."

    # List of keywords to identify as section headers
    section_keywords = [
        "job description", "key responsibilities", "qualifications and skills", 
        "education", "industry type", "department", "employment type", "role category"
    ]
    
    pattern = re.compile(r'(' + '|'.join(section_keywords) + r')', re.IGNORECASE)
    parts = pattern.split(text)

    formatted_text = ""
    if parts and parts[0].strip():
        formatted_text += "**Overview:**\n" + parts[0].strip() + "\n\n"

    for i in range(1, len(parts), 2):
        keyword = parts[i].strip().title()
        raw_content = parts[i+1] # Get the raw content

        #  --- THE FIX IS HERE --- 
        # This line removes any combination of colons and spaces from the start of the content.
        cleaned_content = re.sub(r'^\s*[:\s]+\s*', '', raw_content)

        # Now we can safely add our own, clean colon.
        formatted_text += f"**{keyword}:**\n"
        formatted_text += cleaned_content.strip() + "\n\n"

    return formatted_text.strip() if formatted_text.strip() else text