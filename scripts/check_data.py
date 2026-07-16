import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def main():
    total = 0
    for path in sorted(DATA_DIR.glob("서울_*.json")):
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        items = payload.get("items", [])
        total += len(items)
        sample_keys = sorted(items[0].keys()) if items else []
        print(f"{path.name}: {len(items)}개 / keys={sample_keys}")
    print(f"합계: {total}개")
    print("주의: 축제 JSON의 기본 목록에는 행사 시작일·종료일 필드가 없습니다.")


if __name__ == "__main__":
    main()
