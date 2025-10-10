"""
Small script to run the project's ExtractorFactory on the provided image file and print the extracted InvoiceData.
Run with: python3 scripts/dry_run_extract.py media/notas_fiscais_uploads/nota-fiscal.jpeg
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apps.notas.extractors import ExtractorFactory


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/dry_run_extract.py <image-file>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    extractor = ExtractorFactory.get_extractor(path.name)
    content = path.read_bytes()
    data = extractor.extract(content, path.name)
    print("--- Extracted InvoiceData ---")
    # pydantic v2 compatibility: prefer model_dump_json when available
    try:
        json_out = data.model_dump_json(indent=2, ensure_ascii=False)
    except Exception:
        try:
            json_out = data.json()
        except Exception:
            json_out = str(data)
    print(json_out)


if __name__ == '__main__':
    main()
