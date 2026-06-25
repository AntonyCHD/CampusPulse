"""
PyVis 图谱可视化服务
"""

from pathlib import Path
from typing import Any

from pyvis.network import Network


class GraphVisualizer:
    """图谱可视化器"""

    def __init__(self, output_dir: str = "./cache/graph_html"):
        """初始化可视化器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_graph(
        self,
        graph_data: dict[str, Any],
        event_id: str,
        height: str = "600px",
        width: str = "100%",
    ) -> str:
        """
        渲染评论图谱为 HTML

        Args:
            graph_data: 图谱数据 {nodes: [...], edges: [...]}
            event_id: 事件ID
            height: 图谱高度
            width: 图谱宽度

        Returns:
            HTML 文件路径
        """
        net = Network(
            height=height,
            width=width,
            directed=True,
            notebook=False,
        )

        # 配置物理引擎
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -8000,
              "springLength": 150,
              "springConstant": 0.04,
              "damping": 0.09
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 100
          }
        }
        """)

        # 添加节点
        nodes = graph_data.get("nodes", [])
        for node in nodes:
            node_id = node.get("node_id", "")
            label = node.get("label", "")
            node_type = node.get("node_type", "comment")
            size = node.get("size", 15)
            risk_score = node.get("risk_score", 0.0)

            # 节点颜色
            if node_type == "post":
                color = "#3C5A78"  # 主贴用深蓝色
            elif risk_score > 0.7:
                color = "#E74C3C"  # 高风险红色
            elif risk_score > 0.4:
                color = "#F39C12"  # 中风险橙色
            else:
                color = "#95A5A6"  # 低风险灰色

            net.add_node(
                node_id,
                label=label,
                size=size,
                color=color,
                title=f"{node_id}\n{label}",
            )

        # 添加边
        edges = graph_data.get("edges", [])
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            edge_type = edge.get("edge_type", "reply")
            weight = edge.get("weight", 1.0)

            # 边样式
            if edge_type == "reply":
                color = "#2C3E50"
                width = 2
            elif edge_type == "temporal":
                color = "#BDC3C7"
                width = 1
            else:  # semantic
                color = "#9B59B6"
                width = 1.5

            net.add_edge(
                source,
                target,
                color=color,
                width=width,
                arrows="to",
                title=f"{edge_type} (权重: {weight:.2f})",
            )

        # 保存 HTML
        output_path = self.output_dir / f"{event_id}_graph.html"
        net.save_graph(str(output_path))

        return str(output_path)


# 全局单例
_graph_visualizer: GraphVisualizer | None = None


def get_graph_visualizer() -> GraphVisualizer:
    """获取图谱可视化器单例"""
    global _graph_visualizer
    if _graph_visualizer is None:
        _graph_visualizer = GraphVisualizer()
    return _graph_visualizer
