import requests
import base64
import os
import re
import json
from collections import defaultdict
from dotenv import load_dotenv

# ==========================
# Configuration
# ==========================
load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")  # Required for private repos
OUTPUT_FILE = "WEBSITE_PROJECTS_LIST.json"

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# ==========================
# Fetch all user repos
# ==========================
repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
response = requests.get(repos_url, headers=headers)
repos = response.json()

if isinstance(repos, dict) and "message" in repos:
    print(f"GitHub API error: {repos['message']}")
    exit()

# Lookup for repo info
repos_lookup = {r['html_url'].lower(): r for r in repos}

# ==========================
# Fetch 'my-projects' README
# ==========================
catalog_url = f"https://api.github.com/repos/{USERNAME}/my-projects/readme"
catalog_response = requests.get(catalog_url, headers=headers)
if catalog_response.status_code != 200:
    print(f"Failed to fetch my-projects README: {catalog_response.status_code}")
    exit()

readme_data = catalog_response.json()
content_encoded = readme_data.get("content", "")
content_decoded = base64.b64decode(content_encoded).decode("utf-8")

# ==========================
# Parse projects from README
# ==========================
project_lines = re.findall(
    r"^-?\s*\[\*\*(.*?)\:\*\*\]\((.*?)\)\s*(.*?)(?:\n|$)",
    content_decoded,
    flags=re.MULTILINE
)

projects_dict = defaultdict(list)
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Precompute all images from README
# Look for ![Preview Image](...) and map it to the project above it
image_lookup = {}
for name, github_url, _ in project_lines:
    # Build a pattern: project line, then capture any image before next project line
    pattern = rf"-?\s*\[\*\*{re.escape(name)}:\*\*\]\({re.escape(github_url)}\).*?(?:\n|$)(.*?)(?=(\[\*\*.*?:\*\*\]\(|$))"
    match = re.search(pattern, content_decoded, re.DOTALL)
    img_url = None
    if match:
        block = match.group(1)
        img_match = re.search(r"!\[Preview Image\]\((.*?)\)", block)
        if img_match:
            img_url = img_match.group(1).strip()
    image_lookup[github_url.lower()] = img_url

for name, github_url, description in project_lines:
    key = github_url.lower()
    repo_info = repos_lookup.get(key, {})

    # Only use image if it exists in the README
    image_url = image_lookup.get(key) 

    # Get technology from GitHub repo languages
    technology = ""
    languages_url = repo_info.get("languages_url")
    if languages_url:
        lang_resp = requests.get(languages_url, headers=headers)
        if lang_resp.status_code == 200:
            languages_data = lang_resp.json()
            if languages_data:
                technology = ", ".join(languages_data.keys())

    # Get website from repo homepage
    website = repo_info.get("homepage", "")

    # Determine alphabetical grouping
    first_letter = name[0].upper()
    if first_letter not in alphabet:
        first_letter = "#"

    # Add project to dictionary
    projects_dict[first_letter].append({
        "name": name,                # Take exactly from README
        "github": github_url,
        "description": description.strip(),
        "image": image_url if image_url else None,  # Only set if it exists
        "technology": technology,
        "website": website if website else None
    })

# ==========================
# Sort projects under each letter alphabetically
# ==========================
for letter in projects_dict:
    projects_dict[letter].sort(key=lambda x: x['name'])

alphabetical_projects = {letter: projects_dict[letter] for letter in sorted(projects_dict.keys())}

# ==========================
# Save JSON
# ==========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(alphabetical_projects, f, indent=4)

print(f"{OUTPUT_FILE} generated successfully!")
