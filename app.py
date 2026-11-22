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

map_col, result_col = st.columns([2, 1])

with map_col:
    st.subheader("校園地圖")
    campus_map = folium.Map(
        location=CAMPUS_CENTER,
        zoom_start=16,
        tiles="OpenStreetMap",
        control_scale=True,
    )
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
    st_folium(campus_map, height=520, width=800, key="campus_map")

with result_col:
    st.subheader("搜尋結果")
    if not locations:
        st.info("尚未加入建築資料。下一步請編輯 data/locations.json。")
    elif not filtered:
        st.warning("找不到符合的項目，請嘗試其他關鍵字。")
    else:
        for location in filtered:
            with st.expander(str(location.get("name", "未命名建築")), expanded=len(filtered) == 1):
                description = location.get("description", "")
                if description:
                    st.write(description)
                for unit in location.get("units", []):
                    st.markdown(f"**{unit.get('name', '未命名處室')}**")
                    for service in unit.get("services", []):
                        st.write("• " + str(service.get("name", "未命名業務")))
                        url = str(service.get("url", "")).strip()
                        if url.startswith(("https://", "http://")):
                            st.markdown(f"[官方資訊連結]({url})")

st.caption("地圖資料 © OpenStreetMap contributors。所有行政資訊應以校方官方公告為準。")
