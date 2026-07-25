import json
import sys
from pathlib import Path

from src.views import main_page, save_response_to_json

sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    """Главная страница"""
    #date = "2025-07-27 00:00:00"
    date = "2021-12-31 12:00:00"
    excel_path = Path(__file__).resolve().parent.parent / "data/operations.xlsx"

    result = main_page(date, str(excel_path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    save_response_to_json(result)


if __name__ == "__main__":
    main()
