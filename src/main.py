import json
import sys
from pathlib import Path

from src.views import main_page, save_response_to_json

sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    """Главная страница"""
    date = "2025-07-27 00:00:00"
    result = main_page(date)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    save_response_to_json(result)


if __name__ == "__main__":
    main()
