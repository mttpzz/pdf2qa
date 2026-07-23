import sys
import time
from pathlib import Path
from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError
from tqdm import tqdm

FOLDER = Path("pdf").resolve()
OUTPUT = Path("dataset.pdf")
SORT_BY = "name"  # "name" = alphabetic | "mtime" = modification date


def main():
    pdf_files = sorted(
        [p for p in FOLDER.glob("*.pdf") if p.resolve() != OUTPUT.resolve()],
        key=lambda p: p.name.lower() if SORT_BY == "name" else p.stat().st_mtime,
    )

    if not pdf_files:
        print(f"❌  No PDF files found in: {FOLDER}")
        sys.exit(1)

    print(f"📁  FOLDER  : {FOLDER}")
    print(f"📝  OUTPUT  : {OUTPUT}")
    print(f"🔢  Sort by : {SORT_BY}")
    print(f"\n📂  Found {len(pdf_files)} PDF files to merge.\n")

    writer = PdfWriter()
    ok = []
    errors = []
    total_pages = 0

    for pdf_path in tqdm(pdf_files, desc="Merging"):
        try:
            reader = PdfReader(str(pdf_path), strict=False)
            n = len(reader.pages)
            writer.append(reader)
            total_pages += n
            ok.append((pdf_path.name, n))
        except PdfReadError as e:
            errors.append((pdf_path.name, f"Corrupted PDF: {e}"))
            print(f"\n  ⚠️  Skipped '{pdf_path.name}': {e}", file=sys.stderr)
        except Exception as e:
            errors.append((pdf_path.name, str(e)))
            print(f"\n  ⚠️  Error on '{pdf_path.name}': {e}", file=sys.stderr)

    print(f"\n💾  Writing '{OUTPUT}' ({total_pages} total pages)…")
    t0 = time.time()
    with open(OUTPUT, "wb") as f:
        writer.write(f)
    elapsed = time.time() - t0

    sep = "─" * 55
    print(f"\n{sep}")
    print("  SUMMARY")
    print(sep)
    print(f"  ✅  Files merged successfully : {len(ok)}")
    print(f"  📄  Total pages              : {total_pages}")
    print(f"  ⏱️   Write time               : {elapsed:.1f}s")
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"  📁  Output file              : {OUTPUT}  ({size_mb:.1f} MB)")

    if ok:
        print(f"\n  Included files ({len(ok)}):")
        for name, pages in ok:
            print(f"    • {name}  →  {pages} pag.")

    if errors:
        print(f"\n  ⚠️  Files with errors ({len(errors)}):")
        for name, reason in errors:
            print(f"    • {name}: {reason}")

    print(sep)


if __name__ == "__main__":
    main()