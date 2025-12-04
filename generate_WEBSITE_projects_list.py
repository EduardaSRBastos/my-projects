import requests
import base64
import os
import re
import json
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FILE = "WEBSITE_PROJECTS_LIST.json"

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# ---- GitHub JSON fetch ----
def fetch_json(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

# ---- load existing JSON (if any) to preserve metadata) ----
existing_by_url = {}
if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
        for letter, items in existing.items():
            for item in items:
                key = item.get("github", "")
                if key:
                    existing_by_url[key.lower()] = item
    except Exception:
        existing_by_url = {}

# ---- fetch all repos (for optional metadata refresh) ----
repos = []
repos_data = fetch_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=200")
if isinstance(repos_data, list):
    repos = repos_data
repos_lookup = {r["html_url"].lower(): r for r in repos} if repos else {}

# ---- fetch README of my-projects ----
readme_api = f"https://api.github.com/repos/{USERNAME}/my-projects/readme?ref=develop"
readme_resp = fetch_json(readme_api)
if not readme_resp:
    print(f"Failed to fetch README from {readme_api}. Exiting.")
    raise SystemExit(1)

content_encoded = readme_resp.get("content", "")
if not content_encoded:
    print("README content missing. Exiting.")
    raise SystemExit(1)

content_decoded = base64.b64decode(content_encoded).decode("utf-8")

# ---- extract Projects section (same pattern as README generator) ----
projects_pattern = r"(## Projects)([\s\S]*?)(?=\n## |\Z)"
m = re.search(projects_pattern, content_decoded)
if not m:
    print("Projects section not found in README. Exiting.")
    raise SystemExit(1)

projects_body = m.group(2)

# ---- parse blocks by letter, preserving exact block lines ----
letter_sections = defaultdict(list)
current_letter = None
current_block_lines = []

lines = projects_body.split("\n")
for line in lines:
    anchor = re.match(r'<a id="([A-Z#])"></a>', line)
    if anchor:
        # flush previous block list
        if current_letter and current_block_lines:
            letter_sections[current_letter].append("\n".join(current_block_lines))
            current_block_lines = []
        current_letter = anchor.group(1)
        continue

    if current_letter:
        if line.startswith("- [**"):
            # start of a new project block
            if current_block_lines:
                letter_sections[current_letter].append("\n".join(current_block_lines))
            current_block_lines = [line]
        else:
            if current_block_lines:
                current_block_lines.append(line)

# flush last
if current_letter and current_block_lines:
    letter_sections[current_letter].append("\n".join(current_block_lines))

project_tuples = []  # list of (letter, name, url, description, image)
for letter in letter_sections.keys():
    blocks = letter_sections[letter]
    for block in blocks:
        block_lines = block.split("\n")
        proj_line = block_lines[0]
        rest_lines = block_lines[1:]

        # match project line: - [**Name:**](URL) optional_description
        mproj = re.match(r"^-?\s*\[\*\*(.+?)\:\*\*\]\((https?://github\.com/[^)]+)\)\s*(.*)", proj_line)
        if not mproj:
            mproj = re.match(r"^-?\s*\[\*\*(.+?)\:\*\*\]\(([^)]+)\)\s*(.*)", proj_line)
            if not mproj:
                continue

        name = mproj.group(1).strip()
        url = mproj.group(2).strip()
        description = (mproj.group(3) or "").strip()

        # find first Preview Image in following lines
        image = None
        for ln in rest_lines:
            img_m = re.search(r"!\[Preview Image\]\((.*?)\)", ln)
            if img_m:
                image = img_m.group(1).strip()
                break

        project_tuples.append((letter, name, url, description, image))

# ---- Build projects_dict preserving README order, merging existing metadata ----
projects_dict = defaultdict(list)
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

for letter, name, url, description, image in project_tuples:
    key = url.lower()

    # start with README-provided fields
    entry = {
        "name": name,
        "github": url,
        "description": description,
        "image": image if image else None,
        "technology": None,
        "website": None
    }

    existing = existing_by_url.get(key)
    if existing:
        if existing.get("technology"):
            entry["technology"] = existing.get("technology")
        if existing.get("website"):
            entry["website"] = existing.get("website")

    repo_info = repos_lookup.get(key)
    if repo_info:
        homepage = repo_info.get("homepage") or ""
        if homepage:
            entry["website"] = homepage

        lang_url = repo_info.get("languages_url")
        if lang_url:
            lang_data = fetch_json(lang_url)
            if isinstance(lang_data, dict) and lang_data:
                entry["technology"] = ", ".join(sorted(lang_data.keys()))

    first_letter = letter if letter in alphabet else "#"
    projects_dict[first_letter].append(entry)

for letter in projects_dict:
    projects_dict[letter].sort(key=lambda x: x["name"].lower())

alphabetical_projects = {letter: projects_dict[letter] for letter in sorted(projects_dict.keys())}

# ---- write output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(alphabetical_projects, f, indent=4, ensure_ascii=False)

print(f"{OUTPUT_FILE} generated successfully. Projects parsed: {sum(len(v) for v in projects_dict.values())}")
