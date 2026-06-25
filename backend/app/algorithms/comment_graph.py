"""
评论链图谱构建算法

使用 NetworkX 构建评论关系图，包含：
- 回复边 (reply_edge)
- 时间边 (temporal_edge)
- 语义边 (semantic_edge)
"""

from typing import Any

import networkx as nx
import numpy as np

from backend.app.schemas.comment import CommentGraph, GraphEdge, GraphNode


class CommentGraphBuilder:
    """评论图谱构建器"""

    def __init__(self, semantic_threshold: float = 0.80):
        """
        初始化图谱构建器

        Args:
            semantic_threshold: 语义相似度阈值
        """
        self.semantic_threshold = semantic_threshold

    def build_graph(self, event: dict[str, Any]) -> CommentGraph:
        """
        构建评论图谱

        Args:
            event: 事件数据（包含 post 和 comments）

        Returns:
            CommentGraph 对象
        """
        G = nx.DiGraph()
        nodes = []
        edges = []

        # 添加主贴节点
        post = event.get("post", {})
        post_node = GraphNode(
            node_id=post.get("post_id", "P000"),
            node_type="post",
            label=post.get("text", "")[:30] + "...",
            risk_score=0.0,
            size=20,
            group="post",
        )
        nodes.append(post_node)
        G.add_node(post_node.node_id, **post_node.model_dump())

        # 添加评论节点
        comments = event.get("comments", [])
        comment_nodes = []

        for comment in comments:
            comment_node = GraphNode(
                node_id=comment.get("comment_id", ""),
                node_type="comment",
                label=comment.get("text", "")[:20] + "...",
                risk_score=0.0,
                size=max(10, min(30, 10 + comment.get("like_count", 0) // 5)),
                group="comment",
            )
            comment_nodes.append(comment_node)
            nodes.append(comment_node)
            G.add_node(comment_node.node_id, **comment_node.model_dump())

        # 构建回复边
        for i, comment in enumerate(comments):
            parent_id = comment.get("parent_id")

            if parent_id:
                # 回复其他评论
                edge = GraphEdge(
                    source=parent_id,
                    target=comment.get("comment_id", ""),
                    edge_type="reply",
                    weight=1.0,
                )
            else:
                # 回复主贴
                edge = GraphEdge(
                    source=post.get("post_id", "P000"),
                    target=comment.get("comment_id", ""),
                    edge_type="reply",
                    weight=1.0,
                )

            edges.append(edge)
            G.add_edge(edge.source, edge.target, **edge.model_dump())

        # 构建时间边（按时间顺序连接相邻评论）
        for i in range(len(comments) - 1):
            current = comments[i]
            next_comment = comments[i + 1]

            edge = GraphEdge(
                source=current.get("comment_id", ""),
                target=next_comment.get("comment_id", ""),
                edge_type="temporal",
                weight=0.5,
            )
            edges.append(edge)
            G.add_edge(edge.source, edge.target, **edge.model_dump())

        # 构建语义边（高相似度评论之间）
        if len(comments) > 1:
            semantic_edges = self._build_semantic_edges(comments)
            edges.extend(semantic_edges)
            for edge in semantic_edges:
                G.add_edge(edge.source, edge.target, **edge.model_dump())

        return CommentGraph(
            event_id=event.get("event_id", ""),
            nodes=nodes,
            edges=edges,
        )

    def _build_semantic_edges(self, comments: list[dict[str, Any]]) -> list[GraphEdge]:
        """构建语义相似边"""
        semantic_edges = []

        # 提取评论的 embedding
        embeddings = []
        for comment in comments:
            emb = comment.get("embedding")
            if emb:
                embeddings.append(np.array(emb))
            else:
                embeddings.append(None)

        # 计算成对相似度
        for i in range(len(comments)):
            for j in range(i + 1, len(comments)):
                if embeddings[i] is None or embeddings[j] is None:
                    continue

                # 余弦相似度
                emb_i = embeddings[i]
                emb_j = embeddings[j]
                similarity = np.dot(emb_i, emb_j) / (
                    np.linalg.norm(emb_i) * np.linalg.norm(emb_j)
                )

                if similarity >= self.semantic_threshold:
                    edge = GraphEdge(
                        source=comments[i].get("comment_id", ""),
                        target=comments[j].get("comment_id", ""),
                        edge_type="semantic",
                        weight=float(similarity),
                    )
                    semantic_edges.append(edge)

        return semantic_edges

    def compute_centrality(self, graph: CommentGraph) -> dict[str, float]:
        """
        计算节点中心性（PageRank）

        Args:
            graph: 评论图谱

        Returns:
            {node_id: centrality_score}
        """
        G = nx.DiGraph()

        # 重建 NetworkX 图
        for node in graph.nodes:
            G.add_node(node.node_id)

        for edge in graph.edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)

        # 计算 PageRank
        try:
            centrality = nx.pagerank(G, weight="weight")
        except Exception:
            # 如果图为空或有问题，返回均匀分布
            centrality = {node.node_id: 1.0 / len(graph.nodes) for node in graph.nodes}

        return centrality


if __name__ == "__main__":
    # 测试图谱构建
    test_event = {
        "event_id": "E001",
        "post": {
            "post_id": "P001",
            "text": "测试主贴内容",
            "embedding": np.random.rand(1024).tolist(),
        },
        "comments": [
            {
                "comment_id": "C001",
                "parent_id": None,
                "text": "评论1",
                "like_count": 10,
                "embedding": np.random.rand(1024).tolist(),
            },
            {
                "comment_id": "C002",
                "parent_id": None,
                "text": "评论2",
                "like_count": 5,
                "embedding": np.random.rand(1024).tolist(),
            },
            {
                "comment_id": "C003",
                "parent_id": "C001",
                "text": "回复评论1",
                "like_count": 3,
                "embedding": np.random.rand(1024).tolist(),
            },
        ],
    }

    builder = CommentGraphBuilder()
    graph = builder.build_graph(test_event)

    print(f"图谱构建完成:")
    print(f"  节点数: {len(graph.nodes)}")
    print(f"  边数: {len(graph.edges)}")

    # 计算中心性
    centrality = builder.compute_centrality(graph)
    print(f"\n节点中心性:")
    for node_id, score in sorted(centrality.items(), key=lambda x: -x[1])[:5]:
        print(f"  {node_id}: {score:.4f}")
