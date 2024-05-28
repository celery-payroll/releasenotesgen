import re
import requests
from openai import OpenAI
from datetime import datetime
import sys
import os
import argparse

# Set your GitHub and OpenAI API keys
GITHUB_TOKEN = ''
OPENAI_API_KEY = ''
REPO_OWNER = ''
REPO_NAME = ''

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def read_changelog(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)

def extract_issues(changelog, release):
    issues = {'features': [], 'changes': [], 'bugfixes': []}
    pattern = rf'## {re.escape(release)}\n\*\((\d{{4}}-\d{{2}}-\d{{2}})\)\*([\s\S]+?)(?=\n## |\Z)'
    match = re.search(pattern, changelog)
    if not match:
        print(f"Error: Release {release} not found in CHANGELOG.md")
        sys.exit(1)
    release_date = match.group(1)
    release_content = match.group(2)

    # Adjusted regex to capture the correct content without removing "* "
    sections = re.findall(r'(#### (Features|Changes|Bugfixes)\n[\s\S]+?)(?=\n#### |\Z)', release_content)
    for section, category in sections:
        items = re.findall(r'\* (.+?) \(\[#(\d+)\]\(https://github.com/' + REPO_OWNER + '/' + REPO_NAME + r'/issues/(\d+)\)\)', section)
        issues[category.lower()].extend(items)
    return issues, release_date

def get_issue_details(issue_number):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch details for issue #{issue_number}")
        sys.exit(1)

def summarize_issue(title, body):
    prompt = f"Summarize the following GitHub issue:\n\nTitle: {title}\n\nBody: {body}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a very experienced product manager and your specialty is the creation of Changelog summaries. You use the body of GitHub issue, that has been written in English, to summarize the issue into a maximum of 3 sentences. You write the summary from the point of view of a developer that has resolved the issue."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def build_release_notes(release, release_date, summaries):
    content = f"## {release}\n*({release_date})*\n"
    for category, issues in summaries.items():
        if issues:
            content += f"\n#### {category.capitalize()}\n"
            for summary, issue_number, link in issues:
                content += f"* {summary} ([#{issue_number}]({link}))\n"
    return content

def write_release_notes(file_path, new_content):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                existing_content = file.read()
            if existing_content.strip():
                # Find the position to insert new content after "# Release Notes"
                parts = existing_content.split('\n', 1)
                if len(parts) > 1 and parts[0].strip() == "# Release Notes":
                    new_content = f"{parts[0]}\n\n{new_content}\n---\n\n{parts[1]}"
                else:
                    new_content = f"# Release Notes\n\n{new_content}\n---\n\n{existing_content}"
            else:
                new_content = f"# Release Notes\n\n{new_content}"
        else:
            new_content = f"# Release Notes\n\n{new_content}"

        with open(file_path, 'w') as file:
            file.write(new_content)
    except IOError as e:
        print(f"Error: Unable to write to file {file_path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate release notes for a specific release.")
    parser.add_argument('release', type=str, help='The release number to generate notes for')
    args = parser.parse_args()

    release = args.release

    changelog_path = os.path.join(os.path.dirname(__file__), 'CHANGELOG.md')
    changelog = read_changelog(changelog_path)
    issues, release_date = extract_issues(changelog, release)

    summaries = {'features': [], 'changes': [], 'bugfixes': []}
    processed_issues = set()

    for category, issue_entries in issues.items():
        for entry in issue_entries:
            description, issue_number, link_number = entry
            if issue_number not in processed_issues:
                issue = get_issue_details(issue_number)
                summary = summarize_issue(issue['title'], issue['body'])
                link = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/{link_number}"
                summaries[category].append((summary, issue_number, link))
                processed_issues.add(issue_number)

    # Only write to RELEASE_NOTES.md if there are summaries
    if any(summaries.values()):
        new_release_notes = build_release_notes(release, release_date, summaries)
        write_release_notes('RELEASE_NOTES.md', new_release_notes)
    else:
        print(f"No issues found for release {release}.")

if __name__ == '__main__':
    main()
