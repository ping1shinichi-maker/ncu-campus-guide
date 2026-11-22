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


def matches_query(location, query):
    """在建築、處室、業務名稱與關鍵字中進行簡單文字搜尋。"""
    if not query:
        return True

    terms = [str(location.get("name", "")), str(location.get("description", ""))]
    for unit in location.get("units", []):
        terms.append(str(unit.get("name", "")))
        for service in unit.get("services", []):
            terms.append(str(service.get("name", "")))
            terms.extend(str(k) for k in service.get("keywords", []))

    return query.casefold() in " ".join(terms).casefold()


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


# 將頁面分成左右兩欄
map_col, result_col = st.columns([2, 1])

# ==========================
# 左側：互動式校園地圖
# ==========================
with map_col:
    st.subheader("校園地圖")

    campus_map = folium.Map(
        location=CAMPUS_CENTER,
        zoom_start=16,
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
        height=520,
        width=800,
        key="campus_map",
        returned_objects=["last_object_clicked_tooltip"],
    )


# 取得使用者點擊的建築名稱
clicked_name = (map_data or {}).get(
    "last_object_clicked_tooltip"
)

# 尋找點擊名稱所對應的建築資料
selected_location = next(
    (
        location
        for location in filtered
        if location.get("name") == clicked_name
    ),
    None,
)


# ==========================
# 右側：建築物詳細資訊
# ==========================
with result_col:
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
