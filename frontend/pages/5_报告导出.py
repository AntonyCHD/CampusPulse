"""报告导出页面"""

import streamlit as st

st.title("📄 报告导出")

st.markdown("### 分析报告导出")

st.info("该页面支持导出 Markdown 和 PDF 格式的分析报告")

event_id = st.text_input("输入事件ID", placeholder="例如: E001")
export_format = st.selectbox("导出格式", ["Markdown (.md)", "PDF (.pdf)"])

if st.button("导出报告", type="primary"):
    if event_id:
        with st.spinner("正在生成报告..."):
            st.success(f"报告生成成功！格式: {export_format}")
            st.info("报告导出功能待实现")
    else:
        st.error("请先输入事件ID")
