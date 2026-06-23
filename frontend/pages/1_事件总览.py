"""事件总览页面"""

import streamlit as st

st.title("📊 事件总览")

st.info("该页面将展示所有校园墙事件，支持按风险等级和事件类型筛选")

# 筛选区域
col1, col2, col3 = st.columns(3)

with col1:
    risk_filter = st.selectbox("风险等级", ["全部", "低", "中", "高", "严重"])

with col2:
    event_type_filter = st.selectbox(
        "事件类型",
        ["全部", "后勤服务", "教学教务", "宿舍管理", "食堂餐饮", "校园安全", "管理制度", "传闻求证", "其他"],
    )

with col3:
    sort_by = st.selectbox("排序方式", ["风险等级", "更新时间", "评论数"])

st.divider()

# 事件列表占位
st.warning("暂无事件数据，请先导入校园墙数据")
