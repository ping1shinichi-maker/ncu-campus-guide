"""掌上中大：校園資訊整合網站（起始版本）。

目前提供校園地圖、依文字搜尋資料的程式骨架。
請先在 data/locations.json 填入已查證的建築與業務資料。
"""
import json
from html import escape
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

DATA_FILE = Path(__file__).parent / "data" / "locations.json"
# 校園附近的暫定地圖中心；之後可依官方地圖資料微調。
CAMPUS_CENTER = (24.968, 121.194)


@st.cache_data
def load_locations():
    """從 JSON 讀取校園建築與服務資料。"""
    with DATA_FILE.open(encoding="utf-8") as f:
        locations = json.load(f)
    if not isinstance(locations, list):
        raise ValueError("locations.json 的最外層必須是 JSON 陣列。")
    return locations



def search_services(locations, query):
    """搜尋符合使用者問題的行政業務。"""

    query = query.strip().casefold()

    if not query:
        return []

    results = []

    for building in locations:
        for unit in building.get("units", []):
            for service in unit.get("services", []):

                # 業務與處室名稱
                names = [
                    str(service.get("name", "")),
                    str(unit.get("name", ""))
                ]

                # 這項業務對應的關鍵字
                keywords = [
                    str(k)
                    for k in service.get("keywords", [])
                ]

                # 檢查業務名稱或處室名稱
                name_match = any(
                    query in name.casefold()
                    for name in names
                )

                # 支援使用者輸入完整句子
                keyword_match = any(
                    query in keyword.casefold()
                    or (
                        len(keyword) >= 2
                        and keyword.casefold() in query
                    )
                    for keyword in keywords
                )

                if name_match or keyword_match:
                    results.append((building, unit, service))

    return results


def matches_query(location, query):
    """判斷建築物是否符合搜尋條件。"""

    query = query.strip().casefold()

    if not query:
        return True

    # 搜尋建築名稱與介紹
    building_match = any(
        query in str(location.get(field, "")).casefold()
        for field in ["name", "description"]
    )

    # 搜尋這棟建築物內的行政業務
    service_match = bool(
        search_services([location], query)
    )

    return building_match or service_match


def get_coordinates(location):
    """座標未填或格式不正確時不建立地圖標記。"""
    try:
        lat = float(location["latitude"])
        lon = float(location["longitude"])
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon)
    except (KeyError, TypeError, ValueError):
        pass
    return None


st.set_page_config(page_title="掌上中大 | NCU Campus Guide", page_icon="🏫", layout="wide")
st.title("🏫 掌上中大")
st.caption("中央大學校園資訊整合平台｜目前為起始版本")

try:
    locations = load_locations()
except (OSError, json.JSONDecodeError, ValueError) as exc:
    st.error(f"無法讀取校園資料：{exc}")
    st.stop()

query = st.text_input("搜尋建築物、處室或行政業務", placeholder="例如：圖書館、學生證、腳踏車證")
filtered = [item for item in locations if matches_query(item, query.strip())]

# 取得符合問題的行政業務
service_results = search_services(filtered, query)

# 建立選擇建築物的狀態
if "last_search" not in st.session_state:
    st.session_state.last_search = ""

if "target_building" not in st.session_state:
    st.session_state.target_building = "顯示全部"

# 建立下拉選單選項
options = ["顯示全部"] + [
    location["name"] for location in filtered
]

# 當搜尋文字改變時，自動更新定位目標
if st.session_state.last_search != query.strip():
    st.session_state.last_search = query.strip()

    if query.strip() and len(filtered) == 1:
        st.session_state.target_building = filtered[0]["name"]
    else:
        st.session_state.target_building = "顯示全部"

# 避免選到已不在搜尋結果中的建築
if st.session_state.target_building not in options:
    st.session_state.target_building = "顯示全部"

target_name = st.selectbox(
    "📍 定位建築物",
    options,
    key="target_building",
)

# 取得要定位的建築資料
target_location = next(
    (
        location for location in filtered
        if location.get("name") == target_name
    ),
    None,
)

target_coords = (
    get_coordinates(target_location)
    if target_location else None
)

# 決定地圖中心與縮放程度
map_center = (
    target_coords if target_coords is not None
    else CAMPUS_CENTER
)

map_zoom = 18 if target_coords is not None else 16

# 將頁面分成左右兩欄
map_col, result_col = st.columns([2, 1])

# ==========================
# 左側：互動式校園地圖
# ==========================
with map_col:
    st.subheader("校園地圖")

    campus_map = folium.Map(
    location=map_center,
    zoom_start=map_zoom,
    tiles="OpenStreetMap",
    control_scale=True,
)

    # 將建築物加入地圖
    for location in filtered:
        coords = get_coordinates(location)

        if coords is None:
            continue

        name = escape(str(location.get("name", "未命名建築")))

        folium.Marker(
            location=coords,
            tooltip=name,
            popup=folium.Popup(name, max_width=260),
        ).add_to(campus_map)

    # 接收使用者點擊地圖標記後的資訊
    map_data = st_folium(
    campus_map,
    center=map_center,
    zoom=map_zoom,
    height=520,
    width=800,
    key=f"campus_map_{target_name}",
    returned_objects=["last_object_clicked_tooltip"],
)



# 取得地圖上最後點擊的建築名稱
clicked_name = (map_data or {}).get(
    "last_object_clicked_tooltip"
)

# 點擊標記優先；否則使用下拉選單的選擇
if clicked_name:
    selected_name = clicked_name
elif target_name != "顯示全部":
    selected_name = target_name
else:
    selected_name = None

# 找出對應的完整建築資料
selected_location = next(
    (
        location for location in filtered
        if location.get("name") == selected_name
    ),
    None,
)



# ==========================
# 右側：建築物詳細資訊
# ==========================

with result_col:

    # ==========================
    # 行政業務搜尋結果
    # ==========================
    if query.strip():

        st.subheader("🔎 行政業務搜尋結果")

        if service_results:

            st.success(
                f"找到 {len(service_results)} 項相關業務"
            )

            for building, unit, service in service_results:

                with st.container(border=True):

                    # 顯示業務名稱
                    st.markdown(
                        f"**{service.get('name', '未命名業務')}**"
                    )

                    # 顯示負責處室與建築
                    st.caption(
                        f"{building['name']}｜{unit['name']}"
                    )

                    # 顯示官方網站連結
                    url = str(service.get("url", "")).strip()

                    if url.startswith(("https://", "http://")):
                        st.markdown(
                            f"[查看官方資訊]({url})"
                        )

        else:
            st.info(
                "目前找不到符合的行政業務，"
                "請嘗試較短的關鍵字。"
            )

        st.divider()

    # 原本的建築物詳細資訊
    st.subheader("建築物資訊")

    if not locations:
        st.info("尚未加入建築資料。")

    elif not filtered:
        st.warning("找不到符合的建築物。")

    elif selected_location is None:
        st.info("請點擊地圖上的建築物標記。")

        st.markdown("**目前的建築物：**")
        for location in filtered:
            st.write("•", location["name"])

    else:
        # 顯示建築名稱
        st.markdown(f"### {selected_location['name']}")

        # 顯示建築簡介
        st.write(selected_location.get("description", ""))

        st.divider()

        # 顯示該建築物內的處室
        for unit in selected_location.get("units", []):
            with st.expander(unit["name"], expanded=True):

                for service in unit.get("services", []):
                    st.write("•", service["name"])

                    url = service.get("url", "")

                    if url.startswith(("https://", "http://")):
                        st.markdown(
                            f"[前往官方網站]({url})"
                        )

        # 顯示建築資訊來源
        source = selected_location.get("info_source", "")
        if source.startswith(("https://", "http://")):
            st.markdown(f"[查看建築資訊來源]({source})")

        st.caption("建築標記位置僅供參考，部分座標仍待核對。")


st.caption(
    "地圖資料 © OpenStreetMap contributors。"
    "所有行政資訊應以校方官方公告為準。"
)
