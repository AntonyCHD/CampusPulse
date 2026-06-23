"""证据化处置页面"""

import streamlit as st

st.title("📋 证据化处置")

st.markdown("### 基于证据的处置建议生成")

st.info("该页面展示证据链、处置建议、避免话术和责任部门")

event_id = st.text_input("输入事件ID", placeholder="例如: E001")

if event_id:
    st.markdown(f"### 事件 {event_id} 处置建议")

    st.markdown("#### 证据链")
    st.info("证据检索待实现")

    st.markdown("#### 处置建议")
    st.warning("处置建议生成待实现")

    st.markdown("#### 避免使用的话术")
    st.error("示例：请勿造谣、学校已经处理、不要再讨论")

    st.markdown("#### 责任部门")
    st.info("示例：后勤处、学生工作部")
else:
    st.warning("请输入事件ID")
