# Job Hunt Agent - MVP

Automated job search agent using browser-use to scrape Indeed for Laravel developer positions.

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API Key

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run

```bash
python main.py
```

The agent will:
1. Navigate to Indeed.com
2. Search for "Laravel developer" jobs in "Egypt"
3. Extract 5 job postings (title, company, location, summary)
4. Save results to `job_postings.csv`
5. Take screenshots of each job posting

## Output

- **CSV File**: `job_postings.csv` with columns:
  - Job Title
  - Company Name
  - Location
  - Summary
  - Screenshot Path

## Configuration

Edit the `task` variable in `main.py` to customize:
- Job search query
- Location
- Number of jobs to fetch
- Output format

## Troubleshooting

- **Browser not found**: Run `playwright install chromium`
- **API errors**: Check your OPENAI_API_KEY in `.env`
- **Rate limiting**: Add delays between requests in the task prompt
