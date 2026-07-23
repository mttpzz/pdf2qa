# PDF to Q&A

Automatically generate question-answer datasets from PDF documents using Claude AI. Useful for creating training data, study materials, or fine-tuning datasets.

## Features

- **Extract text from PDFs** — handles multi-page documents with intelligent paragraph-aware chunking
- **Generate Q&A pairs** — uses Claude API to create contextually relevant questions and answers
- **Distributed question generation** — evenly distributes questions across PDF chunks for balanced coverage
- **Merge multiple PDFs** — combine several PDF files into a single document before processing
- **CSV export** — outputs a clean dataset with question and answer columns

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mttpzz/pdf2qa.git
cd pdf2qa
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

## Configuration

Create a `.env` file with the following variables:

```
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

Get your API key from [Anthropic Console](https://console.anthropic.com).

## Usage

### Generate Q&A from a PDF

```bash
python pdf2qa.py <pdf-file> <num-questions>
```

Example:
```bash
python pdf2qa.py document.pdf 100
```

This will:
1. Extract all text from `document.pdf`
2. Split text into intelligent chunks
3. Generate 100 question-answer pairs using Claude
4. Save results to `dataset.csv` with columns: `question`, `answer`

**Note:** If `dataset.csv` already exists, it will be overwritten.

### Merge multiple PDFs

```bash
python onepdf.py
```

This script:
1. Finds all PDF files in the `pdf/` directory
2. Merges them in alphabetical order
3. Saves the combined result as `dataset.pdf`

You can customize the sort order and output path by editing the variables at the top of `onepdf.py`:
- `FOLDER` — directory to scan for PDFs
- `OUTPUT` — output file path
- `SORT_BY` — sort by "name" (alphabetic) or "mtime" (modification date)

## Output

`dataset.csv` contains two columns:

| question | answer |
|----------|--------|
| What is the main topic of this document? | The document discusses... |
| How does the system work? | The system operates by... |

## Notes

- Questions are generated based solely on PDF content — no external information is invented
- Answers are limited to 3-4 sentences for conciseness
- If a chunk fails to parse, it's skipped with a warning
- Processing time depends on PDF size and Claude API response time
- Verify the generated dataset quality before using for fine-tuning

## Requirements

- Python 3.8+
- Anthropic API key (paid account)
- Dependencies listed in `requirements.txt`

## License

This project is provided as-is. Use and modify freely.
