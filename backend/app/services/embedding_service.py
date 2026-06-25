"""
BGE-M3 语义向量服务

提供文本的语义向量表示，支持批量计算和缓存
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """语义向量服务"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str = "cpu",
        cache_dir: str = "./cache/embeddings",
    ):
        """
        初始化语义向量服务

        Args:
            model_name: 模型名称
            device: 计算设备 (cpu/cuda)
            cache_dir: 缓存目录
        """
        self.model_name = model_name
        self.device = device
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 延迟加载模型
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        """延迟加载模型"""
        if self._model is None:
            print(f"正在加载语义向量模型: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name, device=self.device)
            print("[OK] 模型加载完成")
        return self._model

    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{text_hash}.pkl"

    def _load_from_cache(self, cache_key: str) -> np.ndarray | None:
        """从缓存加载向量"""
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return None
        return None

    def _save_to_cache(self, cache_key: str, embedding: np.ndarray):
        """保存向量到缓存"""
        cache_file = self.cache_dir / cache_key
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(embedding, f)
        except Exception as e:
            print(f"缓存保存失败: {e}")

    def encode(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        编码单个文本为向量

        Args:
            text: 输入文本
            use_cache: 是否使用缓存

        Returns:
            向量 (numpy array)
        """
        if not text or not text.strip():
            # 返回零向量
            return np.zeros(1024)  # BGE-M3 的向量维度

        # 尝试从缓存加载
        if use_cache:
            cache_key = self._get_cache_key(text)
            cached = self._load_from_cache(cache_key)
            if cached is not None:
                return cached

        # 计算向量
        embedding = self.model.encode(text, convert_to_numpy=True)

        # 保存到缓存
        if use_cache:
            self._save_to_cache(cache_key, embedding)

        return embedding

    def encode_batch(
        self,
        texts: list[str],
        batch_size: int = 32,
        use_cache: bool = True,
    ) -> list[np.ndarray]:
        """
        批量编码文本为向量

        Args:
            texts: 文本列表
            batch_size: 批处理大小
            use_cache: 是否使用缓存

        Returns:
            向量列表
        """
        embeddings = []

        for text in texts:
            embedding = self.encode(text, use_cache=use_cache)
            embeddings.append(embedding)

        return embeddings

    def compute_similarity(
        self,
        text1: str,
        text2: str,
        use_cache: bool = True,
    ) -> float:
        """
        计算两个文本的余弦相似度

        Args:
            text1: 文本1
            text2: 文本2
            use_cache: 是否使用缓存

        Returns:
            相似度 (0-1)
        """
        emb1 = self.encode(text1, use_cache=use_cache)
        emb2 = self.encode(text2, use_cache=use_cache)

        # 余弦相似度
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)

    def encode_event(
        self,
        event: dict[str, Any],
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        为事件中的所有文本生成向量

        Args:
            event: 事件数据
            use_cache: 是否使用缓存

        Returns:
            包含向量的事件数据
        """
        # 编码主贴
        if "post" in event:
            post_text = event["post"].get("clean_text", event["post"].get("text", ""))
            event["post"]["embedding"] = self.encode(post_text, use_cache=use_cache).tolist()

        # 编码评论
        if "comments" in event:
            for comment in event["comments"]:
                text = comment.get("clean_text", comment.get("text", ""))
                comment["embedding"] = self.encode(text, use_cache=use_cache).tolist()

        return event

    def get_cache_stats(self) -> dict[str, int]:
        """获取缓存统计信息"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        return {
            "cached_embeddings": len(cache_files),
            "cache_size_mb": sum(f.stat().st_size for f in cache_files) / (1024 * 1024),
        }


if __name__ == "__main__":
    # 测试语义向量服务
    service = EmbeddingService(device="cpu")

    # 测试单个文本编码
    print("测试单个文本编码:")
    text = "这是一条测试文本"
    embedding = service.encode(text)
    print(f"文本: {text}")
    print(f"向量维度: {embedding.shape}")
    print(f"向量前5个值: {embedding[:5]}")

    # 测试相似度计算
    print("\n测试相似度计算:")
    text1 = "食堂价格太贵了"
    text2 = "食堂饭菜很贵"
    text3 = "图书馆环境很好"
    sim12 = service.compute_similarity(text1, text2)
    sim13 = service.compute_similarity(text1, text3)
    print(f"'{text1}' vs '{text2}': {sim12:.4f}")
    print(f"'{text1}' vs '{text3}': {sim13:.4f}")

    # 测试缓存统计
    print("\n缓存统计:")
    stats = service.get_cache_stats()
    print(f"已缓存向量数: {stats['cached_embeddings']}")
    print(f"缓存大小: {stats['cache_size_mb']:.2f} MB")
