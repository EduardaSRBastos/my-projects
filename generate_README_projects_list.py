import requests
import re
import os
import string
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")
README_FILE = "README.md"

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# ==========================
# Load README
# ==========================
with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()

# ==========================
# Extract Projects section
# ==========================
projects_pattern = r"(## Projects)([\s\S]*?)(?=\n## |\Z)"
match = re.search(projects_pattern, readme)

if not match:
    print("Projects section not found.")
    exit()

projects_header, projects_body = match.group(1), match.group(2)

# ==========================
# Parse letter sections
# ==========================
letter_sections = defaultdict(list)
current_letter = None
current_block_lines = []

lines = projects_body.split("\n")

for line in lines:
    letter_match = re.match(r"<a id=\"([A-Z#])\"></a>", line)
    if letter_match:
        # flush previous block
        if current_letter and current_block_lines:
            letter_sections[current_letter].append("\n".join(current_block_lines))
            current_block_lines = []

        current_letter = letter_match.group(1)
        continue

    if current_letter:
        if line.startswith("- [**"):
            if current_block_lines:
                letter_sections[current_letter].append("\n".join(current_block_lines))
            current_block_lines = [line]
        else:
            if current_block_lines:
                current_block_lines.append(line)

if current_letter and current_block_lines:
    letter_sections[current_letter].append("\n".join(current_block_lines))

# ==========================
# Collect existing URLs
# ==========================
existing_urls = set(
    re.findall(r"\]\((https://github\.com/[^)]+)\)", projects_body)
)

# ==========================
# Fetch GitHub repos
# ==========================
resp = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=200",
    headers=headers
)
repos = resp.json()

# ==========================
# Build new entries
# ==========================
new_entries = defaultdict(list)

for repo in repos:
    url = repo["html_url"]
    if url in existing_urls:
        continue

    name = repo["name"]
    description = repo.get("description") or ""
    first_letter = name[0].upper()
    if first_letter not in string.ascii_uppercase:
        first_letter = "#"

    title = " ".join(w.capitalize() for w in name.replace("-", " ").split())

    block = f"- [**{title}:**]({url}) {description}\n"

    new_entries[first_letter].append(block)

if not any(new_entries.values()):
    print("No new projects found.")
    exit()

# ==========================
# Merge with RAW blocks preserved
# ==========================
letters = sorted(set(letter_sections.keys()) | set(new_entries.keys()))

new_output = []

# navigation
new_output.append(" - ".join([f"[{L}](#{L})" for L in letters]))
new_output.append("")

for L in letters:
    new_output.append(f"<a id=\"{L}\"></a>")
    new_output.append("")
    new_output.append(f"### {L}")
    new_output.append("")

    # merge raw blocks + new entries
    blocks = letter_sections[L] + new_entries[L]

    # sort by first line only
    blocks = sorted(blocks, key=lambda b: b.split("\n")[0].lower())

    for block in blocks:
        new_output.append(block)

projects_final_text = "\n".join(new_output)

# ==========================
# Replace README section
# ==========================
updated_readme = re.sub(
    projects_pattern,
    f"{projects_header}\n\n{projects_final_text}",
    readme,
    flags=re.DOTALL
)

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(updated_readme)

total_new = sum(len(v) for v in new_entries.values())

print(f"Updated successfully — {total_new} new project{'s' if total_new != 1 else ''} added! Original formatting preserved exactly!")

