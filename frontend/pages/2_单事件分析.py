"""单事件分析页面"""

import streamlit as st

st.title("🔍 单事件分析")

st.info("该页面将展示单个事件的完整分析，包括主贴、评论、风险评分、演化阶段、关键评论和图谱")

# 事件选择
event_id = st.text_input("输入事件ID", placeholder="例如: E001")

if event_id:
    st.markdown(f"### 事件 {event_id}")

    tab1, tab2, tab3, tab4 = st.tabs(["事件详情", "风险分析", "评论图谱", "时间线"])

    with tab1:
        st.markdown("#### 主贴内容")
        st.warning("待接入后端数据")

    with tab2:
        st.markdown("#### 风险评估结果")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("风险等级", "-")
        with col2:
            st.metric("风险分数", "-")
        with col3:
            st.metric("当前阶段", "-")

    with tab3:
        st.markdown("#### 评论传播图谱")
        st.info("图谱可视化待实现")

    with tab4:
        st.markdown("#### 事件时间线")
        st.info("时间线展示待实现")
else:
    st.warning("请输入事件ID开始分析")
