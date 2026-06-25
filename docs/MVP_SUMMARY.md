# 校园舆情监测系统 - MVP完成总结

## 项目概述

基于评论链演化分析的校园舆情监测系统，使用BGE-M3语义向量和三边图谱模型进行风险评估。

## ✅ 已完成功能

### Phase 1: 数据处理层
- ✅ 原始数据格式转换（totalhot → 标准schema）
- ✅ 隐私脱敏服务（用户ID哈希、敏感信息替换）
- ✅ 数据导入流程（39个事件，2363条评论）

### Phase 2: 算法核心层
- ✅ BGE-M3语义向量服务（1024维，支持缓存）
- ✅ 三边评论图谱构建
  - 回复边（parent-child关系）
  - 时间边（连续评论）
  - 语义边（相似度≥0.80）
- ✅ 风险信号检测（8种信号类型）
  - 规则匹配：negative_emotion, rumor_spread, sarcasm等
  - 模式提取：mobilization（时间地点）
  - 聚合分析：collective_resonance（≥30%共鸣）
- ✅ 六因子风险评分
  - post_risk(20%) + resonance(25%) + mobilization(20%)
  - graph_influence(15%) + burst(10%) + uncertainty(10%)
- ✅ 关键评论排序（PageRank + 信号 + 点赞数）

### Phase 3: API服务层
- ✅ FastAPI后端框架
- ✅ 5个API路由模块
  - `/api/events/` - 事件列表（支持筛选）
  - `/api/analyze/{event_id}` - 完整分析流程
  - `/api/graph/{event_id}` - 图谱数据
  - `/api/report/{event_id}` - 报告生成
  - `/api/baseline/{event_id}` - 基线对比
- ✅ 自动缓存机制

### Phase 4: 前端界面
- ✅ Vue 3 + TypeScript现代前端
- ✅ 5个功能页面全部实现
  - 事件总览（网格卡片，筛选）
  - 单事件分析（风险指标可视化）
  - 评论图谱可视化（vis-network交互式）
  - 方法对比（三种方法并排对比）
  - 报告导出（Markdown格式）
- ✅ Element Plus企业级UI组件

### Phase 5: 系统验证
- ✅ 完整功能测试通过
- ✅ 测试结果
  - 事件列表：20个事件
  - 分析示例：风险等级"中"，分数45.63
  - 图谱构建：54节点，122边
  - 基线对比：三种方法均正常

## 技术实现

**语义模型**: BGE-M3 (multilingual, 1024-dim)  
**图算法**: NetworkX (PageRank centrality)  
**风险评分**: 加权多因子模型  
**后端**: FastAPI + Pydantic  
**前端**: Vue 3 + TypeScript + Element Plus + vis-network  
**构建工具**: Vite 8.1.0  
**数据处理**: 结构保持脱敏  
**缓存**: JSON文件缓存（embeddings + 分析结果）

## 测试数据统计

- 事件总数：39个
- 评论总数：2363条
- 用户映射：2205个
- 事件类型：全部为"其他"类型

## 当前可用功能

### 快速启动
```bash
# 双击启动脚本（推荐）
start.bat

# 或手动启动
# 1. 启动后端
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# 2. 启动前端
cd frontend-vue
npm run dev
```

### 访问系统
- 前端界面: http://localhost:5173
- 后端API文档: http://localhost:8000/docs

### API调用示例
```python
import httpx

client = httpx.Client(timeout=60.0)

# 1. 获取事件列表
events = client.get("http://localhost:8000/api/events/").json()

# 2. 分析特定事件
result = client.post(
    "http://localhost:8000/api/analyze/E2889899",
    json={"mode": "cached", "use_llm": False}
).json()

# 3. 获取图谱
graph = client.get("http://localhost:8000/api/graph/E2889899").json()
```

## 核心文件清单

```
backend/app/
├── algorithms/
│   ├── comment_graph.py          # 三边图谱构建
│   ├── risk_signals.py           # 风险信号检测
│   ├── risk_scoring.py           # 风险评分引擎
│   └── key_comments.py           # 关键评论排序
├── services/
│   ├── embedding_service.py      # BGE-M3向量服务
│   ├── analysis_service.py       # 分析流水线
│   ├── anonymize_service.py      # 脱敏服务
│   ├── baseline_service.py       # 基线方法
│   └── graph_visualizer.py       # 图谱可视化服务
├── storage/
│   └── event_store.py            # 内存存储
└── api/
    ├── routes_events.py
    ├── routes_analyze.py
    ├── routes_graph.py
    ├── routes_report.py
    └── routes_baseline.py

frontend-vue/
├── src/
│   ├── api/
│   │   └── api.ts               # API客户端
│   ├── views/
│   │   ├── EventListView.vue    # 事件总览
│   │   ├── EventDetailView.vue  # 单事件分析
│   │   ├── GraphView.vue        # 评论图谱
│   │   ├── ComparisonView.vue   # 方法对比
│   │   └── ReportView.vue       # 报告导出
│   └── router/
│       └── index.ts             # 路由配置
└── vite.config.ts               # Vite配置

scripts/
├── ingest_data.py                # 数据导入流程
├── precompute_analysis.py        # 预计算脚本
└── test_api.py                   # 功能测试脚本

data/
├── raw/totalhot_articles_cleaned.jsonl
└── processed/events.jsonl        # 处理后数据
```

## 下一步建议

### 1. 功能增强
- LLM增强分析（DeepSeek API）
- 时间线演化可视化
- PDF报告导出
- 实时监控仪表盘

### 2. 部署优化
- Docker容器化
- Nginx反向代理
- Redis缓存替代文件缓存
- PostgreSQL持久化存储

### 3. 算法优化
- 微调BGE-M3适配校园场景
- 动态阈值调整
- 增量更新机制
- A/B测试框架

## 成果

- ✅ 完整的评论链分析MVP
- ✅ 前后端全部正常工作
- ✅ Vue 3现代化前端界面
- ✅ 核心算法验证通过
- ✅ 真实数据测试成功
- 📄 完整的技术文档和启动指南

## 联系与支持

系统已验证可正常运行。如需：
- 功能扩展
- 部署配置
- 算法优化

请随时反馈。
