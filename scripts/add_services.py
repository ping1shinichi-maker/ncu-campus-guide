
import json
from pathlib import Path

# 找到專案中的校園資料檔案
DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data" / "locations.json"
)

locations = json.loads(DATA_FILE.read_text(encoding="utf-8"))


def find_building(name):
    """根據名稱尋找建築物。"""
    return next(b for b in locations if b["name"] == name)


def upsert_service(unit, new_service):
    """新增業務；如果 ID 相同就更新，避免重複。"""
    services = unit.setdefault("services", [])

    for i, service in enumerate(services):
        if service.get("id") == new_service["id"]:
            services[i] = {**service, **new_service}
            return

    services.append(new_service)


# 教學研究綜合大樓：教務處
teaching = find_building("教學研究綜合大樓")
academic = next(
    u for u in teaching["units"]
    if u["name"] == "教務處"
)

# 調整原有總覽的關鍵字，避免與新業務重複
for service in academic["services"]:
    if service["name"].startswith("註冊組（3樓）"):
        service["name"] = "註冊組一般學籍服務（3樓）"
        service["keywords"] = [
            "註冊組", "註冊", "學籍", "學籍資料"
        ]


# 1. 學生證補發
upsert_service(academic, {
    "id": "student-card-replacement",
    "name": "學生證遺失補發",
    "keywords": [
        "學生證", "學生證不見", "學生證遺失",
        "學生證掛失", "補辦學生證", "補發學生證"
    ],
    "description": "由教務處註冊組辦理，請先完成掛失。",
    "steps": [
        "登入中大 Portal，進入學生服務、學籍成績服務，辦理學生證掛失。",
        "依註冊組說明填寫補發申請表，完成相關會簽及繳費。",
        "依規定至教研大樓 3 樓註冊組辦理後續領證。"
    ],
    "url": "https://pdc.adm.ncu.edu.tw/p/412-1019-1933.php?Lang=zh-tw",
    "source_url": "https://pdc.adm.ncu.edu.tw/p/412-1019-1706.php"
})


# 2. 成績單申請
upsert_service(academic, {
    "id": "transcript-application",
    "name": "中英文成績單申請",
    "keywords": [
        "成績單", "成績證明", "歷年成績",
        "英文成績單", "中文成績單", "申請成績"
    ],
    "description": "由教務處註冊組辦理，可依文件種類選擇不同申請方式。",
    "steps": [
        "確認需要中文或英文成績單及申請份數。",
        "可至教研大樓 1 樓申請機台或 3 樓註冊組辦理。",
        "如需 Email 申請或郵寄，請查看教務處官方申請說明。"
    ],
    "url": "https://pdc.adm.ncu.edu.tw/p/412-1019-1941.php?Lang=zh-tw"
})


# 3. 自行車證申請：總務處相關業務
admin = find_building("行政大樓")
general = next(
    u for u in admin["units"]
    if u["name"] == "總務處"
)

upsert_service(general, {
    "id": "bicycle-permit",
    "name": "自行車證申請",
    "keywords": [
        "自行車證", "腳踏車證",
        "自行車登記", "腳踏車登記",
        "腳踏車", "自行車"
    ],
    "description": "由總務處事務組辦理，先透過中大 Portal 線上申請。",
    "steps": [
        "登入中大 Portal，進入服務櫃台 iNCU。",
        "選擇總務專區、事務、自行車證申請。",
        "選擇申請張數並送出。",
        "依事務組最新指示攜帶學生證完成領證。"
    ],
    "location_note": (
        "目前地圖標示總務處相關位置，"
        "不代表已確認的自行車證領取地點。"
    ),
    "url": "https://portal.ncu.edu.tw/",
    "source_url": "https://www.oga.ncu.edu.tw/resource/attachment/1767233247.pdf"
})


# 儲存更新後的 JSON
DATA_FILE.write_text(
    json.dumps(locations, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("成功更新三項行政業務！")
