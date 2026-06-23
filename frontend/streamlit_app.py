"""Streamlit application entry point."""

import streamlit as st

st.set_page_config(
    page_title="群声雷达 - Campus Opinion Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application entry point."""
    st.title("📡 群声雷达 - Campus Opinion Radar")
    st.markdown("### 面向校园墙场景的舆情风险演化与证据化处置平台")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("今日事件数", "0", "0")
    with col2:
        st.metric("高风险事件", "0", "0")
    with col3:
        st.metric("待处置", "0", "0")

    st.divider()

    st.info("👈 请从左侧导航栏选择功能页面开始使用")

    with st.expander("系统功能概览"):
        st.markdown("""
        - **事件总览**: 查看所有校园墙事件，按风险等级筛选
        - **单事件分析**: 深度分析单个事件的风险演化路径
        - **对比实验**: 对比不同方法的风险识别效果
        - **证据化处置**: 基于证据生成处置建议
        - **报告导出**: 导出分析报告（Markdown/PDF）
        """)

    with st.expander("技术架构"):
        st.markdown("""
        - **前端**: Streamlit
        - **后端**: FastAPI + Python 3.11+
        - **语义表示**: BGE-M3 中文向量模型
        - **图分析**: NetworkX 评论链建模
        - **大模型**: OpenAI-compatible API
        - **存储**: SQLite + FAISS/Chroma
        """)


if __name__ == "__main__":
    main()
