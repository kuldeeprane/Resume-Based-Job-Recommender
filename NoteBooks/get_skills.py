import pandas as pd
import ast # Abstract Syntax Tree module for safely evaluating string literals

def get_unique_skills_from_csv(file_path: str, column_name: str) -> list:
    """
    Reads a CSV file and extracts all unique skills from a specified column.

    Args:
        file_path (str): The path to the CSV file.
        column_name (str): The name of the column containing skill lists.

    Returns:
        list: A sorted list of unique skills found in the column.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    
    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in the CSV file.")
        return []

    # A set is used to automatically store only unique skills
    all_skills = set()

    # Iterate through each entry in the specified column
    for skill_list_str in df[column_name].dropna(): # .dropna() skips empty cells
        try:
            # Safely parse the string "['skill1', 'skill2']" into a Python list
            skills = ast.literal_eval(skill_list_str)
            
            if isinstance(skills, list):
                # Add all skills from the list to our set
                # .strip() and .lower() normalizes the skills
                all_skills.update([skill.strip().lower() for skill in skills])
        except (ValueError, SyntaxError):
            # This will catch cells that are not in a valid list format
            print(f"Warning: Could not parse row value: {skill_list_str}")
            continue

    # Convert the final set to a sorted list for a clean output
    return sorted(list(all_skills))

import json

def save_list_to_json(data_list: list, file_path: str):
    """Saves a list to a JSON file."""
    print(f"Saving list to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=4)
    print(f"✅ Successfully saved {len(data_list)} items to {file_path}")

# --- Example on how to use the function ---
if __name__ == "__main__":
    csv_file = 'NoteBooks/cleaned_job_data2.csv'  # <-- Make sure to use the correct path to your CSV
    skills_column = 'Required Skills' # <-- The name of your column

    unique_skills = get_unique_skills_from_csv(csv_file, skills_column)
    
    if unique_skills:
        print(f"✅ Found {len(unique_skills)} unique skills in total.")
        # print(unique_skills)
        save_list_to_json(unique_skills, "NoteBooks/skills.json")