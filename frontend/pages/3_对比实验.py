"""对比实验页面"""

import streamlit as st

st.title("⚖️ 对比实验")

st.markdown("### 不同方法的风险识别对比")

st.info("该页面用于对比关键词法、情感分析法、大模型主贴分析和评论链演化分析的差异")

event_id = st.text_input("输入事件ID", placeholder="例如: E001")

if st.button("运行对比实验", type="primary"):
    if event_id:
        with st.spinner("正在运行对比实验..."):
            st.success("实验完成！")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 关键词法")
                st.metric("风险等级", "中", help="仅基于关键词匹配")

            with col2:
                st.markdown("#### 评论链演化法")
                st.metric("风险等级", "高", help="基于评论链结构和语义分析")

            st.divider()
            st.markdown("#### 差异分析")
            st.warning("差异分析待实现")
    else:
        st.error("请先输入事件ID")
