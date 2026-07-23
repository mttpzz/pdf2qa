import os
import csv
import json
import textwrap
import anthropic
import pdfplumber
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_MODEL: str | None = os.getenv('ANTHROPIC_MODEL')
ANTHROPIC_API_KEY: str | None = os.getenv('ANTHROPIC_API_KEY')

PDF_PATH = "dataset.pdf"
NUM_QUESTIONS = 5000
OUTPUT_PATH = "dataset.csv"

MAX_TOKENS = 8192
CHUNK_SIZE = 10_000


def extract_text(pdf_path: str) -> str:
    """Extract all text from PDF file, preserving paragraph structure."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"[ERROR] File not found: {pdf_path}")

    print(f"[INFO] Reading PDF: {pdf_path}")
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"[INFO] Total pages: {total}")
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                parts.append(text)
            if i % 20 == 0 or i == total:
                print(f"[INFO]  → processed page {i}/{total}", end="\r")
    print()

    full_text = "\n\n".join(parts)
    print(f"[INFO] Characters extracted: {len(full_text):,}")
    return full_text


def split_into_chunks(text: str, chunk_size: int) -> list[str]:
    """Split text into chunks, breaking at paragraph boundaries to preserve context."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            split = text.rfind("\n\n", start, end)
            if split != -1:
                end = split
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]


def generate_qa_for_chunk(client: anthropic.Anthropic, chunk: str, n_questions: int, chunk_index: int, total_chunks: int) -> list[dict[str, str]]:
    """Generate Q&A pairs for a text chunk using Claude API. Returns list of {question, answer} dicts."""
    prompt = textwrap.dedent(f"""
        Below is an excerpt from a document (section {chunk_index} of {total_chunks}).
        Generate exactly {n_questions} question-answer pairs based ONLY on the content of this excerpt.

        Rules:
        - Questions must be clear, specific, and relevant to the text.
        - Answers must be complete but concise (max 3-4 sentences).
        - Do not invent information not present in the text.
        - Respond ONLY with valid JSON array, no markdown, no extra text.

        Expected JSON format (array of objects):
        [
          {{"question": "...", "answer": "..."}},
          ...
        ]

        === START OF EXCERPT ===
        {chunk}
        === END OF EXCERPT ===

        Now generate the {n_questions} question-answer pairs as JSON:
    """).strip()

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        raise ValueError("Response is not a JSON list.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\n[WARN] Chunk {chunk_index}: response not parseable ({e}). Chunk skipped.")
        print(f"       Raw response (first 300 chars): {raw[:300]}")
        return []


def distribute_questions(total: int, n_chunks: int) -> list[int]:
    """Evenly distribute target question count across chunks."""
    base: int = total // n_chunks
    remainder: int = total % n_chunks
    dist: list[int] = [base] * n_chunks
    for i in range(remainder):
        dist[i] += 1
    return dist


def write_csv(rows: list[dict[str, str]], output_path: str) -> None:
    """Write Q&A pairs to CSV file with question and answer columns."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] CSV saved to: {output_path}  ({len(rows)} rows)")


def main() -> None:
    """Extract text from PDF, generate Q&A pairs, and save to CSV."""
    text: str = extract_text(PDF_PATH)
    if not text.strip():
        raise ValueError("[ERROR] No text extractable from PDF (might be scanned).")

    chunks = split_into_chunks(text, CHUNK_SIZE)
    n_chunks = len(chunks)
    print(f"[INFO] Chunks generated: {n_chunks}")

    if NUM_QUESTIONS < n_chunks:
        chunks = chunks[:NUM_QUESTIONS]
        n_chunks = NUM_QUESTIONS
        print(f"[INFO] Reduced to {n_chunks} chunks (questions < original chunks).")

    distribution = distribute_questions(NUM_QUESTIONS, n_chunks)
    print(f"[INFO] Question distribution per chunk: {distribution}")

    api_key = ANTHROPIC_API_KEY
    if not api_key:
        raise ValueError("[ERROR] Environment variable ANTHROPIC_API_KEY not set.")

    client = anthropic.Anthropic(api_key=api_key)
    all_rows: list[dict] = []

    for i, (chunk, n_q) in enumerate(zip(chunks, distribution), 1):
        print(f"[INFO] Chunk {i}/{n_chunks}: generating {n_q} questions...")
        qa_pairs = generate_qa_for_chunk(client, chunk, n_q, i, n_chunks)

        for pair in qa_pairs:
            q = pair.get("question") or pair.get("domanda") or ""
            a = pair.get("answer") or pair.get("risposta") or ""
            if q and a:
                all_rows.append({"question": q, "answer": a})

    print(f"\n[INFO] Q&A pairs generated: {len(all_rows)} / {NUM_QUESTIONS} requested")

    if not all_rows:
        raise RuntimeError("[ERROR] No Q&A pairs generated. Check the PDF and API key.")

    write_csv(all_rows, OUTPUT_PATH)


if __name__ == "__main__":
    main()
