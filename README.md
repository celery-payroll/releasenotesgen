# Release Notes Generator

A tool to automatically generate human-friendly release notes from a GitHub repository's issues and changelog.

## Overview

releasenotesgen reads your CHANGELOG.md file, extracts issue references for a specified release, and uses OpenAI's API to generate detailed release notes in a consistent format.

## Prerequisites

- Python 3.6+
- GitHub Personal Access Token
- OpenAI API Key

## Installation

### 1. Install required packages

```bash
pip3 install requests openai pyyaml
```

### 2. Clone the repository

```bash
git clone https://github.com/celery-payroll/releasenotesgen.git
cd releasenotesgen
```

### 3. Make it executable from anywhere (optional)

```bash
ln -s "$(pwd)/releasenotesgen.py" /usr/local/bin/releasenotesgen
```

## Setup

### 1. Copy the configuration template

```bash
cp releasenotesgen.yml /path/to/your/project/
```

### 2. Configure environment variables

```bash
export GITHUB_TOKEN="your_github_token"
export OPENAI_API_KEY="your_openai_api_key"
```

## Configuration

Edit `releasenotesgen.yml` in your project directory:

```yaml
repo_owner: celery-payroll    # GitHub repository owner/organization
repo_name: web-app            # GitHub repository name
model: gpt-4o                 # OpenAI model (optional, default: gpt-4o)
```

## Requirements

- Your project must have a `CHANGELOG.md` file with a specific format:
  ```markdown
  ## 1.2.3
  *(2023-06-15)*
  
  #### Features
  * New authentication system ([#123](https://github.com/owner/repo/issues/123))
  
  #### Changes
  * Updated UI components ([#124](https://github.com/owner/repo/issues/124))
  
  #### Bugfixes
  * Fixed login issue ([#125](https://github.com/owner/repo/issues/125))
  ```

## Usage

Run the tool from your project directory:

```bash
releasenotesgen <release-number>
```

Example:
```bash
releasenotesgen 1.2.3
```

### Options

- `--dry-run`: Preview the generated release notes without writing to RELEASE_NOTES.md
  ```bash
  releasenotesgen 1.2.3 --dry-run
  ```

## Output

The tool will generate a `RELEASE_NOTES.md` file with detailed explanations for each issue, formatted consistently for your target audience.
