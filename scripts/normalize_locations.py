
import json
from pathlib import Path

# ==========================
# 1. 讀取校園資料
# ==========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "locations.json"

locations = json.loads(
    DATA_FILE.read_text(encoding="utf-8")
)

if not isinstance(locations, list):
    raise ValueError("locations.json 必須是 JSON 陣列")


# ==========================
# 2. 建築物的固定 ID 與分類
# ==========================

BUILDING_INFO = {
    "行政大樓": ("administration", "administration"),
    "教學研究綜合大樓": ("teaching-research", "academic"),
    "總圖書館": ("main-library", "library"),
}

seen_building_ids = set()
seen_service_ids = set()
service_count = 0

# ==========================
# 3. 統一建築物與服務格式
# ==========================

for b_index, building in enumerate(locations, start=1):

    name = building["name"]

    building_id, category = BUILDING_INFO.get(
        name,
        (f"building-{b_index:03d}", "other")
    )

    # 保留既有資料，只補齊缺少欄位
    building.setdefault("id", building_id)
    building.setdefault("category", category)
    building.setdefault("aliases", [])
    building.setdefault("description", "")
    building.setdefault("coordinate_status", "unverified")
    building.setdefault("coordinate_source", "")
    building.setdefault("info_source", "")
    building.setdefault("units", [])

    # 檢查建築物 ID 是否重複
    if building["id"] in seen_building_ids:
        raise ValueError(
            f"重複的建築物 ID：{building['id']}"
        )

    seen_building_ids.add(building["id"])

    # 處理建築內的行政單位
    for u_index, unit in enumerate(
        building["units"], start=1
    ):

        unit.setdefault(
            "id",
            f"{building['id']}-unit-{u_index:02d}"
        )

        unit.setdefault("services", [])

        # 處理行政服務
        for s_index, service in enumerate(
            unit["services"], start=1
        ):

            service.setdefault(
                "id",
                f"{building['id']}-{u_index:02d}-{s_index:02d}"
            )

            # 防止服務 ID 重複
            if service["id"] in seen_service_ids:
                raise ValueError(
                    f"重複的服務 ID：{service['id']}"
                )

            seen_service_ids.add(service["id"])

            # 統一服務資料欄位
            service.setdefault("description", "")
            service.setdefault("keywords", [])
            service.setdefault("steps", [])
            service.setdefault("service_location", "")
            service.setdefault("location_note", "")
            service.setdefault("url", "")
            service.setdefault("source_url", "")

            # 尚未核對的資料，不可標示成已確認
            service.setdefault("verified_at", None)
            service.setdefault(
                "verification_status", "pending"
            )

            service_count += 1


# ==========================
# 4. 儲存更新後的 JSON
# ==========================

DATA_FILE.write_text(
    json.dumps(
        locations,
        ensure_ascii=False,
        indent=2
    ) + "\n",
    encoding="utf-8"
)

print("資料庫格式統一完成！")
print(f"建築物數量：{len(locations)}")
print(f"行政服務數量：{service_count}")
print(f"資料檔案：{DATA_FILE}")
