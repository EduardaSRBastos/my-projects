import requests
import base64
from collections import defaultdict
import string
import re
import os
from dotenv import load_dotenv

# ==========================
# Configuration
# ==========================
load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN") # Optional: Add your GitHub Personal Access Token here for higher rate limits
OUTPUT_FILE = "README_PROJECTS_LIST.md"

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# ==========================
# Fetch public repos
# ==========================
repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
response = requests.get(repos_url, headers=headers)

try:
    repos = response.json()
except ValueError:
    print("Error: Failed to parse JSON from GitHub API.")
    exit()

if isinstance(repos, dict) and "message" in repos:
    print(f"GitHub API returned an error: {repos['message']}")
    exit()

if not isinstance(repos, list):
    print(f"Unexpected response from GitHub API: {repos}")
    exit()

# ==========================
# Organize repos alphabetically
# ==========================
alphabet = string.ascii_uppercase
projects_dict = defaultdict(list)

for repo in repos:
    name = repo.get("name")
    html_url = repo.get("html_url")
    repo_about = repo.get("description")  # GitHub About description
    if not name or not html_url:
        continue

    first_letter = name[0].upper()
    if first_letter not in alphabet:
        first_letter = "#"  # for non-alphabetical names

    # Default values
    description = ""
    image_url = ""

    # Try fetching README for description
    readme_url = f"https://api.github.com/repos/{USERNAME}/{name}/readme"
    readme_response = requests.get(readme_url, headers=headers)

    if readme_response.status_code == 200:
        readme_data = readme_response.json()
        content_encoded = readme_data.get("content", "")
        if content_encoded:
            try:
                content_decoded = base64.b64decode(content_encoded).decode("utf-8")
                # Extract description inside <p><i>...</i></p>
                desc_match = re.search(r"<p><i>(.*?)</i></p>", content_decoded, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()

                # For image, check if README has <kbd> image </kbd>
                img_match = re.search(r"<kbd>\s*!\[.*?\]\((.*?)\)\s*</kbd>", content_decoded, re.DOTALL)
                if img_match:
                    image_url = f"https://raw.githubusercontent.com/{USERNAME}/{name}/refs/heads/main/assets/images/preview.png"

            except Exception as e:
                print(f"Warning: Could not decode README for {name}: {e}")

    # Fallback to GitHub About description if README description is missing
    if not description and repo_about:
        description = repo_about.strip()

    # Include all projects
    projects_dict[first_letter].append({
        "name": name,
        "description": description,
        "url": html_url,
        "image": image_url
    })

# ==========================
# Generate Markdown
# ==========================
output = "Collection of personal projects\n\n"

# Alphabet line with links
letters_present = [letter for letter in alphabet if projects_dict[letter]]
if projects_dict["#"]:
    letters_present.append("#")  # include non-alphabetical names at the end

output += " - ".join([f"[{letter}](#{letter})" for letter in letters_present]) + "\n\n"

# List projects under each letter
for letter in letters_present:
    output += f"<a id=\"{letter}\"></a>\n\n"  # Anchor for the letter
    output += f"### {letter}\n\n"  # Section header
    for project in projects_dict[letter]:
        # Format project name: uppercase first letters
        project_name_formatted = " ".join([w.capitalize() for w in project['name'].replace("-", " ").split()])
        # Project name as link
        output += f"[**{project_name_formatted}:**]({project['url']})"
        # Add description on the same line if exists
        if project['description']:
            output += f" {project['description']}"
        output += "\n\n"
        # Image below
        if project['image']:
            output += f"![Preview Image]({project['image']})\n\n"

# ==========================
# Save to file
# ==========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(output)

print(f"{OUTPUT_FILE} generated successfully!")