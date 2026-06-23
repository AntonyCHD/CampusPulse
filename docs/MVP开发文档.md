# MVP 开发文档

本文档从《详细设计.md》中拆分出来，只描述最小可行版本的交付边界、数据要求和实现顺序。

### 1. 最小可行版本 MVP

MVP 的目标不是把所有设想都做完，而是在最短时间内交付一个可运行、可解释、可演示、可写论文初步实验的闭环。MVP 必须围绕当前 JSONL 数据集展开。

#### 1.1 MVP 要做什么

MVP 只做一个核心故事：

> 选择一个脱敏校园墙事件，系统展示主贴和评论区，基于语义向量、规则兜底和 Top-N LLM 弱标注识别风险信号，计算风险等级和演化阶段，定位关键评论，并生成结构化处置报告；同时展示“只看主贴/关键词法”和“语义评论链方法”的差异。

MVP 必须完成：

| 编号 | 功能 | 输入 | 输出 | 完成标准 |
| --- | --- | --- | --- | --- |
| MVP-1 | JSONL 导入 | `data/raw/campus_wall_sample.jsonl` | `data/processed/events.jsonl` | 5-10 个事件可导入，错误行能指出行号和字段 |
| MVP-2 | 脱敏与清洗 | 原始文本 | 脱敏文本、`clean_text` | Demo、缓存、报告中无真实姓名、学号、手机号、宿舍号、账号 ID |
| MVP-3 | 事件列表 | 标准化事件 | Streamlit 事件列表 | 可按风险等级、事件类型筛选；显示评论数和更新时间 |
| MVP-4 | 单事件分析 | `event_id` | 主贴、评论、信号、分数、阶段 | 点击事件后能完成一次分析并展示结果 |
| MVP-5 | 风险信号识别 | 评论文本 + embedding + Top-N 弱标注 | `RiskSignal[]` | 每个信号包含 `signal_type`、`comment_id`、`evidence_text`、`reason`、`source` |
| MVP-6 | 风险评分 | 信号、点赞、时间、评论数 | `RiskAssessment` | 输出 0-100 分、低/中/高/严重、当前阶段 |
| MVP-7 | 关键评论排序 | 评论图、信号、点赞 | `key_comments` | 至少返回 Top 3，能解释为什么关键 |
| MVP-8 | 基线对比 | 主贴、语义评论链结果 | `baseline_result` | 展示关键词/情感基线 vs 语义评论链法差异 |
| MVP-9 | 报告生成 | `RiskAssessment` | `FinalReport` | LLM 可选；无 API 时用模板生成；JSON 通过 schema 校验 |
| MVP-10 | 演示缓存 | 分析结果 | `cache/demo_reports/*.json` | 答辩现场可切到缓存模式，不依赖网络 |

#### 1.2 MVP 需要什么数据

当前数据集是 JSONL 格式。MVP 数据最低要求如下：

```text
文件：data/raw/campus_wall_sample.jsonl
数量：5-10 个事件
每个事件：1 条主贴 + 10-30 条评论
字段：event_id, post, comments
标注：risk_level, risk_stage, event_type, key_comments
隐私：必须脱敏后才能进入 processed/cache/outputs
```

建议至少准备以下事件类型，便于答辩展示风险层次：

| 事件类型 | 数量 | 目标风险 | 用途 |
| --- | --- | --- | --- |
| 后勤/宿舍争议 | 2 | 中/高 | 展示情绪共振和组织化行动 |
| 食堂/价格争议 | 1-2 | 中 | 展示诉求集中和证据化回应 |
| 教学教务安排 | 1-2 | 低/中 | 展示求证、信息澄清 |
| 传闻求证 | 1 | 中/高 | 展示事实不确定性和人工复核 |
| 普通吐槽 | 1-2 | 低 | 展示系统不会把所有负面都判成高风险 |

MVP 标注文件必须同步准备：

```text
data/labels/event_labels.jsonl
```

如果时间不足，允许先用 5 个事件演示，但论文实验至少应扩展到 30 个事件，否则只能写案例分析，不能有足够可信的定量结论。

#### 1.3 MVP 不做什么

为保证项目能交付，以下能力不进入第一版：

```text
1. 不做自动爬取与实时采集，只处理已授权导出的 JSONL。
2. 不做用户画像，不分析个人身份，只做匿名事件级分析。
3. 不做自动删帖、封禁、压热度等治理动作。
4. 不做复杂多模态鉴伪，图片字段先保留，P3 再做 OCR。
5. 不做端到端大模型训练，先用语义向量、规则兜底、图结构和可选 Top-N LLM 弱标注。
6. 不依赖实时 LLM API，所有演示案例必须有缓存。
```

#### 1.4 MVP 开发顺序

```text
Step 1 数据契约
  - 写 Pydantic schema
  - 写 JSONL loader
  - 写 schema 单元测试

Step 2 数据处理
  - 写脱敏函数
  - 写清洗函数
  - 生成 data/processed/events.jsonl

Step 3 分析核心
  - 风险信号规则
  - 评论图构建
  - 风险评分
  - 关键评论排序

Step 4 API 闭环
  - GET /api/events
  - GET /api/events/{event_id}
  - POST /api/analyze/{event_id}
  - GET /api/report/{event_id}

Step 5 前端闭环
  - 事件总览
  - 单事件分析
  - 关键评论卡片
  - 基线对比

Step 6 演示兜底
  - 导出 cache/demo_reports/*.json
  - 前端增加 cached/realtime 模式
  - 固定答辩案例顺序
```

#### 1.5 增强版再做

```text
P1:
  - 评论图谱可视化
  - LLM 结构化解释
  - Markdown 报告导出

P2:
  - RAG 证据检索
  - 批量实验评估
  - 消融实验表格

P3:
  - OCR 图文分析
  - 自动话题聚类
  - PDF 报告导出
  - 多模型测评
```

---

