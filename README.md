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

### Customization

Edit constants at the top of `pdf2qa.py` to control behavior:

```python
PDF_PATH = "dataset.pdf"        # Input PDF file
NUM_QUESTIONS = 5000            # Target Q&A pairs to generate
OUTPUT_PATH = "dataset.csv"     # Output CSV file
CHUNK_SIZE = 10_000             # Text chars per chunk (smaller = more focused, slower)
MAX_TOKENS = 8192               # Max Claude response length
```

**Note on CHUNK_SIZE:** Smaller chunks (5000) = more focused Q&A, more API calls. Larger chunks (20000) = broader context, fewer calls.

### Pricing

**This tool incurs Claude API costs.** Each PDF chunk generates an API call. Typical cost estimate:
- 50-page PDF with 100 questions: ~$0.50–$2.00 (depends on chunk overlap)
- Monitor usage at [Anthropic Console](https://console.anthropic.com/account/usage)

Use `CHUNK_SIZE` and `NUM_QUESTIONS` to control costs.

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

### Multi-Language Support

Claude may generate Q&A in languages other than English. The script automatically handles:
- English: `question`, `answer` fields
- Italian: `domanda`, `risposta` fields
- Other languages: Column names preserved as-is

Example (Italian response):
```json
[
  {"domanda": "Qual è il tema principale?", "risposta": "Il documento tratta..."},
  {"question": "What is the main topic?", "answer": "The document discusses..."}
]
```

Both are correctly exported to the output CSV with their original field names normalized to `question`/`answer`.

## Performance & Time Estimates

Processing time depends on PDF size and API latency:
- **10-page PDF, 100 questions:** ~1–2 minutes
- **50-page PDF, 500 questions:** ~5–10 minutes
- **100+ pages:** 15+ minutes (chunks are processed sequentially)

Each chunk = one API call. Reduce `NUM_QUESTIONS` or increase `CHUNK_SIZE` to speed up processing.

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: dataset.pdf` | PDF file missing | Run `python onepdf.py` or place PDF in current directory |
| `ANTHROPIC_API_KEY not set` | Missing `.env` file | Create `.env` and add `ANTHROPIC_API_KEY=...` |
| `response not parseable` | Claude returned invalid JSON | Normal for some chunks; quality Q&A still saved. Increase `MAX_TOKENS` if frequent. |
| `No text extractable from PDF` | PDF is image-only (scanned) | Use OCR tool first (e.g., Tesseract, Pytesseract) |
| `Empty dataset.csv` | All chunks failed to parse | Check PDF quality and API key; try reducing `CHUNK_SIZE` |
| API timeout / rate limits | Too many simultaneous requests | Add delay between chunks or use cheaper model (`claude-3-haiku-*`) |

## Notes

- Questions generated based solely on PDF content — no external information invented
- Answers limited to 3-4 sentences for conciseness
- Skipped chunks logged as warnings; partial dataset still exported
- Processing time scales linearly with questions requested
- Verify generated dataset quality before fine-tuning — sample a few Q&A pairs manually

## Requirements

- Python 3.8+
- Anthropic API key (paid account)
- Dependencies listed in `requirements.txt`

## License

This project is provided as-is. Use and modify freely.
