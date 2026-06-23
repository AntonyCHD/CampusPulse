# 校园舆情风险演化雷达

#### You:
现在我们小组需要完成《舆情与媒体安全》课程期末课设大作业，项目的四个附件，分别是，项目文件为大作业的详细说明，其中第四个附件即校园舆情检测系统的docx是我们小组的初版（我非常不满意），这个文档的提到的方向很模糊（假大空，并且技术深度非常浅），现在请你为我深度构思几个完全符合课程内容与课设要求的方向（每个方向大致讲讲该怎么做，什么技术（深度学习？机器学习？NLP？结合课程内容与说明文档等等，请你拓展思维，网络搜索等等）需要准备什么，能得到什么输出产物（我的期望是能够做一个可视化的demo，用来展示），技术栈，数据来源的话我还是希望使用校园墙的数据（已经得到授权获取数据），实现路线等等，此外毕竟是创新创业课程，因此方向我觉得产品化比较好，运用一些前沿技术？结合大模型？毕竟后续需要书写计划书，但也不要因此丧失技术深度，不过给讲的时候不要太过于技术化（比如大片使用专业术语）要好懂些）

#### ChatGPT:
我会把这件事按“课设评分-课程主题-可落地 Demo-论文技术深度”四条线重新梳理，不只是在原初版上修补。重点会放在能用校园墙授权数据做出可展示产品原型、同时能写出技术论文的方法。我已经看完初版思路和评分口径了：你现在这个方向不是不能用，而是“只靠 Prompt 调 API”会显得像演示脚本，不像有核心技术的课设。更好的路线是保留“校园墙数据”这个真实场景，把技术核心往“事件演化、证据核验、传播图谱、多模态媒体安全、大模型安全治理”上抬一层。

Zimo，我的判断很明确：**不要推翻“校园墙数据”这个场景，但要推翻现在初版的技术骨架。**\
你们初版的“主贴 + 评论区 + 大模型 JSON 输出”方向有场景优势，但问题是：它自己写明“不训练、不微调，只用 Prompt Engineering + 大模型 API + 领域知识注入”，这会让老师觉得像“调用接口做文本分析”，技术深度不够。课程要求本身覆盖人工智能安全、舆情安全、媒体安全三大板块，包括大模型安全测评、舆情大数据分析、社群仿真、大模型驱动舆情分析、内容安全审核、深度伪造对抗等方向；创业答辩也强调要有核心技术、真实场景、竞品分析、技术优势、应用价值和 Demo。所以你们最好的策略是：**用校园墙授权数据做真实底座，用“风险演化 + 证据核验 + 传播图谱 + 大模型辅助决策”包装成一个产品化原型。**

下面我给你几个真正适合课设、论文、答辩和 Demo 的方向。

---

## 我最推荐的主方向：校园舆情风险演化雷达

**项目名可以叫：CampusPulse / 群声雷达 / 校园舆情风险演化雷达。**

这不是简单判断“这条帖子负不负面”，而是判断一个校园事件正在经历什么阶段：\
**吐槽 → 求证 → 情绪共振 → 立场对立 → 组织化行动 → 线下风险。**

这个方向可以保留初版的“评论区很重要”思想，但要把它升级成一个完整系统。初版已经意识到传统监测只看主贴会漏掉评论区风险，也提出要识别情绪共振、风险升级、线下行动号召，但现在还停留在 Prompt 层。你们应该把它做成：

### 怎么做

系统输入校园墙帖子和评论区，先做四层分析：

第一层是**事件识别**：把多条类似帖子聚成同一个事件，比如“宿舍限电”“食堂涨价”“考试安排争议”“校园设施故障”。

第二层是**情绪与立场识别**：不只判断正负面，而是识别评论是在“支持、反对、求证、调侃、煽动、建议、辟谣”。立场检测在社交媒体、虚假信息检测、内容治理中是很典型的研究任务，近年的 LLM 立场检测综述也强调了它在误导信息检测、社交媒体治理和公共舆论理解中的价值([arXiv](https://arxiv.org/html/2505.08464v1))。

第三层是**评论链风险演化**：把评论按时间、回复关系、点赞数串起来，看风险是降温还是升温。比如“有人问是真的吗”是低风险，“大家一起去线下堵门”就是高风险。

第四层是**处置建议生成**：不是让模型空口生成，而是接入学校制度、过往回应模板、官方通知，做 RAG 检索后生成“建议回应”。

### 技术栈

前端 Demo：Streamlit 或 Gradio，时间够的话用 React + ECharts。\
后端：FastAPI + Python。\
数据：校园墙帖子、评论、点赞、时间、图片、回复关系。\
NLP：BGE-m3 / text2vec 中文向量、BERTopic 或 HDBSCAN 话题聚类、SnowNLP/情感分类器/中文 RoBERTa 做情绪基线。\
大模型：Qwen、DeepSeek、GPT API 均可，用结构化 JSON 输出。\
图谱：NetworkX / PyVis / ECharts 画评论传播图。\
存储：SQLite / DuckDB / Chroma / FAISS。

### Demo 可以展示什么

一个非常漂亮的三栏 Demo：

左边：选择校园墙案例。\
中间：显示事件演化时间线和评论传播图。\
右边：输出风险等级、风险原因、关键评论、建议回应话术、是否需要人工复核。

最好加一个对照按钮：

**传统关键词法：低风险**\
**评论链演化模型：高风险，因为第 17 条评论出现线下聚集号召，第 21 条评论获得高点赞，情绪开始共振。**

这个对照会非常杀。因为初版也提到要做“只输入主贴 vs 主贴+评论区”的对比实验，你们可以进一步升级成：

关键词法 vs 情感分析法 vs 大模型主贴分析 vs 评论链演化分析。

### 论文可以写什么

论文题目可以是：

**《面向校园墙场景的评论链驱动舆情风险演化识别方法研究》**

论文核心实验：

1. 只看主贴；
2. 主贴 + 评论区；
3. 主贴 + 评论区 + 时间顺序；
4. 主贴 + 评论区 + 回复图谱 + RAG 处置建议。

评价指标可以用准确率、召回率、F1、关键评论命中率、人工标注一致率。

### 产品化怎么讲

不要说“监控学生”，这个词很危险。要说：

**我们不是为了压制表达，而是帮助学校更早发现真实诉求，避免小问题在沉默中发酵。**

卖点是：传统舆情系统做“全网监测”，你们做“校园细粒度诉求治理”。人民在线官网就有标准化 SaaS 舆情服务、定制化舆情服务和舆情+社会治理等业务形态([People Online](https://www.peopleonline.cn/))；新华睿思 V7.0 也强调多模态、大模型、语义解析和研判溯源([新华网](https://www.news.cn/20250521/b00fcbdbb2f84e3883102f675ebf9095/c.html))。你们的差异化是：**不是和巨头比全网数据规模，而是比校园场景理解、评论链风险演化和低成本部署。**

---

## 方向二：校园传闻事实核验与澄清助手

**项目名：CampusFact / 校园澄清官 / 校园传闻核验助手。**

这个方向比“舆情监测”更温和，也更有社会价值。校园墙里经常有这类内容：

“听说某老师挂科率特别高？”\
“听说某宿舍楼要断电一周？”\
“食堂是不是偷偷涨价了？”\
“这个通知是真的假的？”

它的本质不是情绪分析，而是：**传闻、求证、事实核验、澄清传播。**

### 怎么做

系统把帖子中的“可核验主张”抽出来，比如：

“宿舍 12 点后断电。”\
“某食堂价格上涨。”\
“某考试安排改期。”

然后去检索证据：

学校官网通知、教务处公告、后勤公众号、学生手册、历史校园墙相似事件、人工上传的政策文件。

再让大模型输出：

可信度：高 / 中 / 低 / 无法判断。\
证据来源：哪份通知、哪条政策、哪段文本。\
建议回应：适合官方或学生组织发布的澄清话术。\
风险提示：是否可能继续发酵。

这个方向可以参考“证据检索 + 多模态事实核验”的研究思路。近年的多模态误导信息检测研究强调，不能只看声明本身，还需要检索相关文本和图片证据，再进行事实验证([arXiv](https://arxiv.org/abs/2407.14321))。

### 技术栈

OCR：PaddleOCR，用来识别截图里的通知、聊天记录、图片文字。\
RAG：Chroma / FAISS + BGE-m3。\
LLM：做 claim extraction、evidence reasoning、澄清生成。\
后端：FastAPI。\
前端：Streamlit，做“输入传闻 → 展示证据链 → 输出可信度”。

### Demo 输出

上传一条校园墙帖子，系统自动生成：

- 核心传闻；
- 检索到的学校通知；
- 证据匹配程度；
- 可信度评分；
- 一段“官方澄清建议”；
- 一段“学生可读版解释”。

这个 Demo 很适合答辩，因为老师一眼能看懂：**不是删帖，不是压热度，而是减少误会。**

### 论文题目

**《基于检索增强生成的校园传闻事实核验与澄清生成方法研究》**

实验可以做：

- 无 RAG 直接问大模型；
- 只检索关键词；
- 向量检索 + 大模型；
- 向量检索 + 证据排序 + 大模型。

比较模型是否胡编、证据是否命中、人工评分是否更可信。

---

## 方向三：校园情绪共振与群体行为早预警图谱

**项目名：ResonanceMap / 群声图谱 / 校园情绪共振地图。**

这个方向更“舆情大数据分析”和“社群仿真”。它关注的问题是：

不是某条帖子负面，而是**负面情绪有没有形成群体共振**。\
不是某个人在抱怨，而是**一群人是否在同一时间、围绕同一诉求、用相似语言快速聚集**。

### 怎么做

把校园墙数据变成图：

帖子是节点。\
评论是节点。\
用户匿名 ID 是节点。\
相似话题、回复关系、共同情绪、时间接近性是边。

然后系统识别：

- 哪些话题正在聚集；
- 哪些评论是“情绪放大器”；
- 哪些节点是“关键转折点”；
- 哪些事件可能从线上讨论转向线下行动。

社会事件检测研究中，社交媒体事件检测本来就是从社交帖子、在线讨论等数据源中识别、分类和跟踪事件；近期研究也在用 LLM 增强短文本理解、聚类和事件检测效率([ACL Anthology](https://aclanthology.org/2025.acl-long.233.pdf))。另有 2026 年 WWW 方向的研究把 RAG、结构熵和事件演化结合起来，用于开放世界社交事件检测与演化建模([arXiv](https://arxiv.org/html/2601.12035v1))。你们可以把这个思路降维到校园墙场景。

### 技术栈

- 向量聚类：BGE-m3 + HDBSCAN / KMeans；
- 图分析：NetworkX，PageRank，Louvain 社区发现；
- 时间突增检测：滑动窗口统计、Z-score、突增指数；
- 大模型：给每个聚类自动命名，比如“宿舍用电争议”“食堂价格不满”；
- 可视化：ECharts 关系图、时间热力图、事件气泡图。

### Demo 输出

一个大屏：

上方：今日校园热议事件 Top 5。\
左侧：情绪温度计。\
中间：话题关系图。\
右侧：风险解释。\
底部：事件时间线。

比如系统显示：

“宿舍限电”话题过去 3 小时评论量上升 260%，负向情绪集中在“通知不透明”“影响复习”，关键转折评论为“今晚一起去楼下问清楚”。

### 论文题目

**《基于话题图谱与时间突增检测的校园舆情共振识别方法研究》**

这个方向的技术深度比方向一更强，但做起来也更吃数据。如果你们能拿到足够多校园墙数据，方向三非常漂亮。

---

## 方向四：校园墙图文内容安全与截图鉴伪系统

**项目名：MediaGuard / 校园图文鉴真 / 溯图。**

这个方向更贴近“媒体安全”和“深度伪造对抗”。校园墙不只有文字，很多爆点来自截图：

聊天记录截图、通知截图、朋友圈截图、课程群截图、图片拼接、AI 生成图片、断章取义的视频截图。

问题是：\
**图片看起来像证据，但它可能是伪造的、裁剪的、断章取义的、AI 生成的。**

### 怎么做

系统输入一张校园墙图片或图文帖子，做四件事：

1. OCR 提取图片文字；
2. 判断图片文字与主贴描述是否一致；
3. 检测是否有明显编辑痕迹，比如分辨率异常、边缘拼接、重复区域、EXIF 缺失；
4. 如果是 AI 生成内容，尝试识别显式标识、隐式元数据、水印或生成痕迹。

这个方向很前沿，因为中国已经正式发布《人工智能生成合成内容标识办法》，其中明确人工智能生成合成内容包括文本、图片、音频、视频、虚拟场景等，并区分显式标识和隐式标识([国家市场监督管理总局](https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm))。办法还要求服务提供者在生成合成内容文件元数据中添加隐式标识，并鼓励数字水印等形式([国家市场监督管理总局](https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm))。所以你们可以把它讲成：**面向校园媒体安全的 AIGC 标识与截图证据可信度评估工具。**

### 技术栈

- OCR：PaddleOCR；
- 图像基础检测：OpenCV、ELA、感知哈希 pHash；
- 图文一致性：CLIP / Qwen-VL / GPT-4o 类视觉模型；
- AIGC 痕迹：元数据检查、显式水印检查、疑似生成分数；
- 前端：Streamlit 上传图片，展示检测报告。

### Demo 输出

上传一张“学校通知截图”，系统输出：

- OCR 识别文本；
- 图片是否疑似编辑；
- 图文描述是否一致；
- 是否含 AI 生成标识；
- 可信度评分；
- 是否建议人工核验。

### 论文题目

**《面向校园墙图文帖的多模态内容可信度评估方法研究》**

这个方向很有“媒体安全”味道，创新性强。但风险是：如果你们校园墙图片数据不多，可能 Demo 会变成单纯上传图片检测，和舆情结合不够紧。因此我建议它作为方向一的增强模块，而不是三人小组的唯一主线。

---

## 方向五：校园内容安全大模型测评与红队平台

**项目名：SafeWall-Eval / 校园内容安全测评靶场。**

这个方向最贴合“人工智能安全”和“大模型安全测评”。不是做一个舆情监测系统，而是做一个评测平台：

**校园墙内容审核模型到底靠不靠谱？遇到反讽、谐音、缩写、表情包、阴阳怪气、截图文字，它会不会漏判？**

### 怎么做

你们构造一个校园墙内容安全测试集，类型包括：

- 普通吐槽；
- 合理诉求；
- 反讽阴阳怪气；
- 谣言求证；
- 人身攻击；
- 隐私泄露；
- 线下聚集号召；
- 诱导网暴；
- AIGC 伪造内容。

然后让不同模型或不同 Prompt 去判断风险，看它们的误判、漏判、过度审核情况。

这很像一个“校园场景大模型安全测评集”。中国的生成式 AI 安全标准方向也强调模型输出安全、准确性、可靠性，以及对模型输入内容持续监测、防范注入攻击等安全要求([MLex](https://content.mlex.com/Attachments/2025-05-23_CZT297CHX8R49J68/SAMR_NSA_Basic_Security_Requirements_GenAI_service.pdf?utm_source=chatgpt.com))。

### 技术栈

- 测试集：校园墙授权数据 + 人工脱敏标注；
- 模型：Qwen / DeepSeek / GPT / 本地模型；
- 评测指标：准确率、召回率、误杀率、漏判率、一致性；
- 对抗样本：同义改写、谐音替换、表情符号插入、截图 OCR；
- Demo：模型测评排行榜 + 单案例对比。

### Demo 输出

选择一个测试样本，系统显示：

模型 A：低风险，漏判。\
模型 B：中风险，理由不完整。\
模型 C：高风险，命中“线下聚集号召”。\
最终人工标签：高风险。

这个方向论文深度强，但产品化稍弱。适合你们想突出“人工智能安全测评”的小组。

---

## 方向六：校园舆情处置智能体

**项目名：CampusSOP Agent / 舆情处置智能助手。**

这个方向偏产品化，适合答辩，但论文要小心别写得太空。它的核心不是“发现风险”，而是“发现之后怎么办”。

系统模拟多个角色：

- 舆情分析员：判断事件风险；
- 事实核验员：查证据；
- 学生视角代理：判断学生可能怎么理解；
- 管理者代理：生成处置方案；
- 合规审查员：检查回应是否激化矛盾、是否泄露隐私。

最后输出：

- 事件摘要；
- 风险等级；
- 建议回应；
- 不建议使用的话术；
- 24 小时处置流程；
- 需要联系的部门。

可以结合多智能体辩论做“处置建议不是一个模型拍脑袋，而是多个角色互相审查”。2025 年已有研究探索多智能体辩论用于零样本立场检测，以处理上下文不足和语言歧义问题([MDPI](https://www.mdpi.com/2076-3417/15/9/4612?utm_source=chatgpt.com))。你们可以把这种思想简化成“多角色复核机制”。

这个方向非常适合做答辩故事，但如果单独做，容易变成“套壳大模型”。所以我建议它作为方向一的最后一层：**风险识别之后，生成处置 SOP。**

---

## 综合推荐排序

我的最终建议是：

**主线选“校园舆情风险演化雷达”。**\
然后把方向二“事实核验”和方向六“处置智能体”作为两个模块塞进去。这样最稳、最完整、最像产品，也最容易写论文。

最终产品可以定义成：

> 面向高校校园墙场景的舆情风险演化与证据化处置平台。系统基于授权校园墙数据，融合评论链分析、话题聚类、情绪共振识别、事实核验 RAG 与大模型辅助决策，帮助高校从“看到负面帖子”升级为“理解事件如何发酵、为什么发酵、该如何温和处置”。

---

## 你们可以采用的最终技术架构

数据层：

校园墙主贴、评论、点赞、发布时间、图片、回复关系。\
所有数据先脱敏：姓名、学号、电话、宿舍号、头像、账号 ID 全部替换为匿名编号。

分析层：

1. 话题聚类：把相似帖子合并成事件；
2. 情绪识别：判断评论情绪；
3. 立场识别：支持、反对、求证、辟谣、煽动、建议；
4. 评论链建模：按时间和回复关系分析风险演化；
5. 关键评论发现：找出推动事件升温的评论；
6. RAG 证据检索：从校规、通知、后勤公告中找依据；
7. 大模型结构化研判：输出 JSON 报告。

展示层：

- 舆情事件列表；
- 风险热力图；
- 评论链时间线；
- 关键评论卡片；
- 证据链；
- 处置建议；
- 一键导出 PDF 报告。

---

## 数据应该怎么准备

你们不要只准备 5 个案例。5 个案例只能演示，撑不起论文。

最低配：

- 30 个校园墙事件；
- 每个事件 1 条主贴 + 10 到 30 条评论；
- 总评论数 500 条左右；
- 人工标注每个事件的风险等级、事件类型、关键评论、风险阶段。

中配：

- 100 个事件；
- 2000 到 5000 条评论；
- 可以训练一个轻量分类器或至少做统计评估。

字段建议：

```json
{
  "event_id": "E001",
  "post_id": "P001",
  "post_text": "脱敏后的主贴内容",
  "post_time": "2026-06-20 21:30",
  "comments": [
    {
      "comment_id": "C001",
      "parent_id": null,
      "text": "脱敏后的评论",
      "time": "2026-06-20 21:35",
      "like_count": 23,
      "stance_label": "求证",
      "emotion_label": "焦虑",
      "risk_signal": "无"
    }
  ],
  "human_label": {
    "risk_level": "中",
    "risk_stage": "情绪共振",
    "key_comments": ["C007", "C012"],
    "event_type": "后勤服务"
  }
}
```

---

## 论文和答辩要分开讲

你们附件里也已经意识到论文和答辩是两套逻辑：论文写技术方法，答辩讲 Demo 和商业价值。这个判断是对的，但要更彻底。

论文不要写“创业市场规模”。\
论文写：

**问题：** 校园舆情评论区存在隐性风险，传统关键词法难以识别反讽、共振和组织化倾向。\
**方法：** 评论链风险演化识别框架。\
**实验：** 与关键词法、情感分析法、大模型单帖分析做对比。\
**结论：** 评论链结构和时间演化能提高关键风险识别能力。

答辩写：

**痛点：** 高校不是没有舆情系统，而是缺少校园细粒度诉求理解。\
**产品：** 校园舆情风险演化雷达。\
**客户：** 高校宣传部、学生工作部、后勤、学院辅导员队伍。\
**价值：** 更早发现问题，更温和回应学生，更少误判和激化。\
**Demo：** 现场展示一个事件从低风险变中高风险的演化过程。

---

## 最后给你一个非常清晰的选题定位

我建议你们最终不要叫“校园舆情检测系统”。这个名字太普通、太像传统监控平台。

改成：

**《群声雷达：面向校园墙场景的舆情风险演化与证据化处置平台》**

这个名字有三个好处：

第一，“群声”比“监控”柔和，强调倾听学生。\
第二，“风险演化”体现技术深度。\
第三，“证据化处置”体现产品价值，不是模型乱判。

一句话介绍：

> 群声雷达是一套面向高校校园墙场景的轻量化舆情风险演化分析平台，基于授权校园墙数据，融合评论链建模、情绪共振识别、事实核验 RAG 与大模型辅助研判，帮助高校从“被动看见负面帖子”升级为“提前理解事件如何发酵并给出有证据的温和处置建议”。

这条线最适合你们：**有校园真实数据，有 Demo，有论文实验，有创业叙事，也有课程主题覆盖。**


#### You:
我仔细阅读了你的方案，差不多确定了就做你首要主推的校园舆情风险演化雷达，现在请你继续思考，并设计一份详细的详细设计文档与完整清晰的实现路径（包括但不限于，项目仓库结构与目录，所有抽象项目数据结构与类，前后端映射与数据通信，开发工作流，详细的核心算法以及对应的伪代码，项目模块设计，上线部署方式，模块直接耦合度等（如何通信，交换数据，接口可扩展），以及详细的编码规范指导）

#### ChatGPT:
我会把它写成一份“可以直接指导开发”的设计文档，而不是概念方案。接下来会同时对齐课程评分要求、初版已有约束、当前主流技术组件，并把系统拆成能三人协作落地的工程结构。我会把初版的“单次大模型研判”升级为“可验证的工程流水线”：数据脱敏入库 → 事件聚类 → 评论链建模 → 风险评分 → RAG 证据检索 → 结构化报告 → 可视化 Demo。这样答辩能讲产品，论文能讲方法，代码能真的跑。

下面这份设计我按\*\*“能做出来、能演示、能写论文、能答辩”\*\*四个目标来写。核心原则是：**前端漂亮、后端清晰、算法有层次、大模型不裸奔、输出可验证、现场可兜底。**

你们课程要求本身强调围绕“舆情、媒体以及相关联的人工智能与认知安全方向”选题，期末还要提交技术研究论文；创业答辩则看核心技术、场景需求、竞品分析、技术创新性、技术方案完备性、应用价值和 Demo。所以这个项目不能只是“调 API 生成 JSON”，而应该设计成一个**校园墙舆情事件演化分析系统**。

---

# 《群声雷达：校园舆情风险演化雷达》详细设计文档

## 1. 项目定位

项目全称建议：

**群声雷达：面向校园墙场景的舆情风险演化与证据化处置平台**

一句话：

> 基于授权校园墙数据，系统识别校园舆情事件从“吐槽、求证、情绪共振、立场对立、组织化行动、线下风险”的演化路径，并通过评论链建模、话题聚类、风险评分、RAG 证据检索与大模型结构化研判，生成可视化风险报告和温和处置建议。

这比初版更强。初版已经提出“主贴 + 评论区全链路对话链语义推理”，重点识别情绪共振、风险升级和线下行动号召，但技术路线仍然写成“不训练、不微调模型，只用 Prompt Engineering + 大模型 API + 领域知识注入”。现在要升级为：

**规则基线 + 传统 NLP + 图结构分析 + 大模型结构化研判 + RAG 证据检索 + 可视化 Demo。**

大模型是“研判器”，不是整个系统的唯一大脑。

---

## 2. 总体系统架构

推荐采用：

- **前端 Demo：Streamlit**
- **后端服务：FastAPI**
- **数据存储：SQLite / DuckDB**
- **向量检索：FAISS / Chroma**
- **图谱计算：NetworkX**
- **大模型接口：OpenAI-compatible SDK，可切换 OpenAI、DeepSeek、通义、智谱**
- **可视化：Streamlit 原生图表 + Plotly / PyVis / ECharts JSON**
- **部署：本地运行 + Docker Compose 兜底**

FastAPI 适合作为后端 API 框架，因为它基于 Python 类型提示构建 API，并能自动生成交互式 API 文档；这对你们调试接口、给答辩老师展示“后端不是脚本拼接”很有帮助。([FastAPI](https://fastapi.tiangolo.com/?utm_source=chatgpt.com), [FastAPI](https://fastapi.tiangolo.com/features/?utm_source=chatgpt.com)) Streamlit 适合快速做数据应用和 AI/ML Demo，官方定位就是用 Python 快速构建交互式数据应用。([Streamlit](https://streamlit.io/?utm_source=chatgpt.com), [Streamlit 文档](https://docs.streamlit.io/?utm_source=chatgpt.com)) Pydantic 则负责数据校验，它基于 Python 类型提示定义数据结构，非常适合把“大模型输出 JSON”变成可验证对象。([Pydantic](https://pydantic.dev/docs/validation/latest/get-started/?utm_source=chatgpt.com))

### 总体架构图

```text
┌────────────────────────────────────────────────────────────┐
│                      Streamlit Demo 前端                    │
│  事件列表 | 风险雷达 | 评论链图谱 | 时间线 | 证据链 | 报告导出 │
└───────────────────────▲────────────────────────────────────┘
                        │ HTTP / JSON
┌───────────────────────┴────────────────────────────────────┐
│                       FastAPI 后端服务                       │
│  /events  /analyze  /graph  /report  /baseline  /export      │
└───────────────▲─────────────▲──────────────▲────────────────┘
                │             │              │
┌───────────────┴───┐ ┌───────┴────────┐ ┌───┴────────────────┐
│ 数据处理层         │ │ 算法分析层       │ │ 大模型与RAG层        │
│ 脱敏/清洗/入库     │ │ 聚类/情绪/图谱   │ │ 证据检索/结构化研判  │
└───────────────▲───┘ └───────▲────────┘ └───▲────────────────┘
                │             │              │
┌───────────────┴─────────────┴──────────────┴────────────────┐
│                       数据与索引层                            │
│ SQLite/DuckDB | FAISS/Chroma | 本地缓存 JSON | 政策知识库       │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 功能模块设计

系统拆成 9 个模块，彼此通过**明确的数据结构**通信，避免互相写死。

| 模块 | 名称       | 责任                  | 输入                        | 输出             | 耦合度 |
| -- | -------- | ------------------- | ------------------------- | -------------- | --- |
| M1 | 数据导入模块   | 导入校园墙数据、脱敏、清洗       | 原始 JSON / Excel / CSV     | 标准化 EventRaw   | 低   |
| M2 | 数据标注模块   | 人工标注风险等级、关键评论、事件类型  | EventRaw                  | LabeledEvent   | 低   |
| M3 | 话题聚类模块   | 将相似帖子合并为同一事件        | Post 列表                   | EventCluster   | 中   |
| M4 | 评论链建模模块  | 按时间、回复关系、点赞构建评论图    | Event                     | CommentGraph   | 中   |
| M5 | 风险信号识别模块 | 识别情绪、立场、组织化号召、隐私泄露等 | Event + Comments          | RiskSignal\[]  | 中   |
| M6 | 风险演化评分模块 | 计算风险分数和演化阶段         | RiskSignal + GraphFeature | RiskAssessment | 中   |
| M7 | RAG 证据模块 | 检索学校通知、制度、历史案例      | EventSummary              | Evidence\[]    | 低   |
| M8 | LLM 研判模块 | 基于结构化上下文生成解释和建议     | Assessment + Evidence     | LLMReport      | 低   |
| M9 | 可视化模块    | 展示事件、图谱、时间线、报告      | API JSON                  | UI 页面          | 低   |

核心思想：\
**M4/M5/M6 是你们的技术深度，M8 是增强表达，不是替代算法。**

---

## 4. 推荐仓库结构

仓库名建议：

```text
campus-opinion-radar/
```

完整目录：

```text
campus-opinion-radar/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
│
├── docs/
│   ├── design.md                    # 详细设计文档
│   ├── api.md                       # API接口文档
│   ├── data_schema.md               # 数据结构说明
│   ├── annotation_guide.md          # 人工标注规范
│   ├── demo_script.md               # 答辩演示脚本
│   └── paper_experiment_plan.md     # 论文实验设计
│
├── data/
│   ├── raw/                         # 原始授权数据，不上传Git
│   ├── anonymized/                  # 脱敏后数据
│   ├── processed/                   # 标准化事件数据
│   ├── labels/                      # 人工标注
│   ├── knowledge_base/              # 校规/通知/处置模板
│   └── demo_cases/                  # 答辩演示案例
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI入口
│   │   ├── config.py                # 配置读取
│   │   ├── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes_events.py
│   │   │   ├── routes_analyze.py
│   │   │   ├── routes_graph.py
│   │   │   ├── routes_report.py
│   │   │   └── routes_baseline.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── event.py             # Pydantic数据模型
│   │   │   ├── comment.py
│   │   │   ├── risk.py
│   │   │   ├── graph.py
│   │   │   ├── evidence.py
│   │   │   └── report.py
│   │   │
│   │   ├── services/
│   │   │   ├── ingestion_service.py
│   │   │   ├── anonymize_service.py
│   │   │   ├── topic_service.py
│   │   │   ├── emotion_service.py
│   │   │   ├── stance_service.py
│   │   │   ├── graph_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── baseline_service.py
│   │   │   └── report_service.py
│   │   │
│   │   ├── algorithms/
│   │   │   ├── keyword_baseline.py
│   │   │   ├── burst_detection.py
│   │   │   ├── comment_graph.py
│   │   │   ├── risk_scoring.py
│   │   │   ├── key_comment_ranker.py
│   │   │   └── evolution_stage.py
│   │   │
│   │   ├── llm/
│   │   │   ├── prompts/
│   │   │   │   ├── risk_assessment_zh.md
│   │   │   │   ├── evidence_reasoning_zh.md
│   │   │   │   └── intervention_zh.md
│   │   │   ├── schemas.py
│   │   │   └── client.py
│   │   │
│   │   ├── storage/
│   │   │   ├── db.py
│   │   │   ├── repositories.py
│   │   │   └── vector_store.py
│   │   │
│   │   └── utils/
│   │       ├── text_cleaning.py
│   │       ├── time_utils.py
│   │       ├── json_utils.py
│   │       └── logger.py
│   │
│   └── tests/
│       ├── test_schema.py
│       ├── test_risk_scoring.py
│       ├── test_comment_graph.py
│       └── test_api.py
│
├── frontend/
│   ├── streamlit_app.py             # Demo入口
│   ├── pages/
│   │   ├── 1_事件总览.py
│   │   ├── 2_单事件分析.py
│   │   ├── 3_对比实验.py
│   │   ├── 4_证据化处置.py
│   │   └── 5_报告导出.py
│   ├── components/
│   │   ├── event_card.py
│   │   ├── risk_radar.py
│   │   ├── timeline.py
│   │   ├── comment_graph.py
│   │   └── evidence_panel.py
│   └── api_client.py
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_annotation_analysis.ipynb
│   ├── 03_baseline_experiment.ipynb
│   └── 04_ablation_study.ipynb
│
├── scripts/
│   ├── ingest_data.py
│   ├── anonymize_data.py
│   ├── build_vector_index.py
│   ├── run_batch_analysis.py
│   ├── export_demo_cache.py
│   └── evaluate_methods.py
│
├── cache/
│   ├── llm_responses/
│   ├── demo_reports/
│   └── graph_json/
│
└── outputs/
    ├── reports/
    ├── figures/
    └── experiment_results/
```

**关键要求：**

- `data/raw/` 不进 Git。
- `data/demo_cases/` 只放脱敏样例。
- 所有大模型输出必须缓存到 `cache/llm_responses/`。
- 答辩现场优先走缓存，避免 API 抽风。
- 论文实验结果统一放 `outputs/experiment_results/`。

---

## 5. 核心数据结构设计

建议所有核心数据结构都用 Pydantic 定义。这样 API 输入输出、模型输出、前端渲染可以共享同一套 schema。OpenAI 结构化输出也建议用 JSON Schema 约束，因为官方文档说明 Structured Outputs 可以让模型输出遵循你定义的 JSON Schema，避免缺 key 或枚举值幻觉问题。([OpenAI平台](https://platform.openai.com/docs/guides/structured-outputs)) 你们后端再用 Pydantic 二次校验，形成“双保险”。

### 5.1 基础枚举

```python
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "严重"

class EventType(str, Enum):
    LOGISTICS = "后勤服务"
    TEACHING = "教学教务"
    DORMITORY = "宿舍管理"
    CANTEEN = "食堂餐饮"
    SAFETY = "校园安全"
    ADMIN = "管理制度"
    RUMOR = "传闻求证"
    OTHER = "其他"

class EvolutionStage(str, Enum):
    COMPLAINT = "个体吐槽"
    VERIFICATION = "信息求证"
    RESONANCE = "情绪共振"
    POLARIZATION = "立场对立"
    MOBILIZATION = "组织化行动"
    OFFLINE_RISK = "线下风险"

class StanceLabel(str, Enum):
    SUPPORT = "支持"
    OPPOSE = "反对"
    QUESTION = "求证"
    MOCK = "调侃反讽"
    SUGGEST = "建议"
    RUMOR_REFUTE = "辟谣"
    MOBILIZE = "号召"
    ATTACK = "攻击"

class EmotionLabel(str, Enum):
    NEUTRAL = "中性"
    ANGER = "愤怒"
    ANXIETY = "焦虑"
    DISAPPOINTMENT = "失望"
    SATIRE = "讽刺"
    FEAR = "恐慌"
    TRUST = "信任"
```

### 5.2 帖子与评论

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Comment(BaseModel):
    comment_id: str
    parent_id: Optional[str] = None
    user_hash: Optional[str] = None
    text: str
    clean_text: Optional[str] = None
    created_at: datetime
    like_count: int = 0
    reply_count: int = 0

    emotion: Optional[EmotionLabel] = None
    stance: Optional[StanceLabel] = None
    risk_signals: List[str] = Field(default_factory=list)

class Post(BaseModel):
    post_id: str
    source: str = "campus_wall"
    user_hash: Optional[str] = None
    title: Optional[str] = None
    text: str
    clean_text: Optional[str] = None
    created_at: datetime
    like_count: int = 0
    comment_count: int = 0
    image_paths: List[str] = Field(default_factory=list)

class CampusEvent(BaseModel):
    event_id: str
    event_type: EventType
    post: Post
    comments: List[Comment]
    tags: List[str] = Field(default_factory=list)
    data_note: str = "授权获取并脱敏处理"
```

### 5.3 图结构数据

```python
class GraphNode(BaseModel):
    node_id: str
    node_type: str          # post / comment
    label: str
    risk_score: float = 0.0
    size: int = 10
    group: Optional[str] = None

class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: str          # reply / temporal / semantic
    weight: float = 1.0

class CommentGraph(BaseModel):
    event_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
```

### 5.4 风险信号

```python
class RiskSignal(BaseModel):
    signal_type: str
    comment_id: Optional[str] = None
    evidence_text: str
    score: float
    reason: str

class RiskAssessment(BaseModel):
    event_id: str
    risk_level: RiskLevel
    risk_score: float
    current_stage: EvolutionStage
    evolution_path: List[EvolutionStage]
    key_comments: List[str]
    risk_signals: List[RiskSignal]
    confidence: float
```

### 5.5 RAG 证据与最终报告

```python
class Evidence(BaseModel):
    evidence_id: str
    title: str
    source: str
    content: str
    score: float
    evidence_type: str      # policy / notice / history_case / response_template

class InterventionAdvice(BaseModel):
    summary: str
    official_statement: str
    action_items: List[str]
    avoid_phrases: List[str]
    responsible_department: List[str]
    urgency: str

class FinalReport(BaseModel):
    event_id: str
    event_summary: str
    risk_assessment: RiskAssessment
    evidence: List[Evidence]
    intervention: InterventionAdvice
    generated_at: datetime
    mode: str               # realtime / cached
```

---

## 6. 前后端映射与 API 设计

前端只负责展示，不直接跑算法。所有分析都走后端 API。这样好处是：

- Streamlit 可以换成 React；
- 算法可以独立测试；
- 论文实验可以直接调用后端；
- Demo 崩了也能用缓存 JSON。

### 6.1 API 总览

| API                        | 方法   | 用途                   | 前端页面  |
| -------------------------- | ---- | -------------------- | ----- |
| `/api/events`              | GET  | 获取事件列表               | 事件总览  |
| `/api/events/{event_id}`   | GET  | 获取单个事件原始数据           | 单事件分析 |
| `/api/analyze/{event_id}`  | POST | 运行完整分析流水线            | 单事件分析 |
| `/api/baseline/{event_id}` | POST | 运行关键词/情感基线           | 对比实验  |
| `/api/graph/{event_id}`    | GET  | 获取评论图谱数据             | 单事件分析 |
| `/api/report/{event_id}`   | GET  | 获取最终报告               | 报告页   |
| `/api/export/{event_id}`   | GET  | 导出 Markdown / PDF 报告 | 报告导出  |
| `/api/cache/{event_id}`    | GET  | 读取演示缓存               | 答辩兜底  |

### 6.2 前端页面映射

```text
事件总览页
  └── GET /api/events
      └── 展示风险Top事件、事件类型分布、今日新增事件

单事件分析页
  ├── GET /api/events/{event_id}
  ├── POST /api/analyze/{event_id}
  └── GET /api/graph/{event_id}
      └── 展示主贴、评论、风险阶段、关键评论、图谱

对比实验页
  ├── POST /api/baseline/{event_id}?method=keyword
  ├── POST /api/baseline/{event_id}?method=sentiment
  └── POST /api/analyze/{event_id}
      └── 展示关键词法 vs 情感法 vs 评论链法

证据化处置页
  └── GET /api/report/{event_id}
      └── 展示证据链、处置建议、避免话术

报告导出页
  └── GET /api/export/{event_id}?format=md/pdf
```

### 6.3 关键接口示例

#### 获取事件列表

```http
GET /api/events?risk_level=高&limit=20
```

响应：

```json
{
  "items": [
    {
      "event_id": "E001",
      "title": "宿舍限电争议",
      "event_type": "宿舍管理",
      "risk_level": "高",
      "risk_score": 83.5,
      "current_stage": "组织化行动",
      "comment_count": 42,
      "updated_at": "2026-06-23T21:00:00"
    }
  ],
  "total": 1
}
```

#### 运行完整分析

```http
POST /api/analyze/E001
```

请求体：

```json
{
  "mode": "realtime",
  "use_llm": true,
  "use_rag": true,
  "top_n_comments": 20
}
```

响应：

```json
{
  "event_id": "E001",
  "risk_level": "高",
  "risk_score": 83.5,
  "current_stage": "组织化行动",
  "evolution_path": ["信息求证", "情绪共振", "组织化行动"],
  "key_comments": ["C007", "C012"],
  "intervention": {
    "summary": "该事件已从个体抱怨发展为评论区共振，并出现线下聚集倾向。",
    "official_statement": "建议先发布事实说明，回应具体诉求，避免使用命令式语气。",
    "action_items": ["联系宿舍管理部门核实", "发布说明", "安排辅导员线下沟通"],
    "avoid_phrases": ["请勿造谣", "学校已经处理", "不要再讨论"],
    "responsible_department": ["后勤处", "学生工作部"],
    "urgency": "24小时内回应"
  }
}
```

---

## 7. 核心算法设计

这是整个项目最重要的部分。你们答辩时要讲清楚：

**我们不是让大模型直接猜风险，而是先把评论区变成可计算的风险结构，再让大模型解释和生成建议。**

---

# 7.1 数据脱敏算法

### 目标

保护学生隐私，避免把真实姓名、手机号、学号、宿舍号、账号 ID 暴露到 Demo 和论文里。

### 规则

- 姓名：替换为 `[姓名]`
- 学号：替换为 `[学号]`
- 手机号：替换为 `[电话]`
- 宿舍房间：替换为 `[宿舍号]`
- 用户 ID：hash 成 `U_xxxxx`
- 图片：只保留脱敏后截图，或 OCR 后仅存文本

### 伪代码

```text
Algorithm AnonymizeEvent(event_raw):
    input: 原始校园墙事件
    output: 脱敏后的标准事件

    for each post/comment in event_raw:
        text = 原始文本
        text = 替换手机号为 [电话]
        text = 替换学号为 [学号]
        text = 替换宿舍号为 [宿舍号]
        text = 替换疑似姓名为 [姓名]
        user_id = hash(raw_user_id + salt)
        保存 clean_text 和 user_hash

    return anonymized_event
```

---

# 7.2 评论预过滤算法

初版已经提到“评论 >20 条时，按点赞、敏感词、互动筛 Top-N”。这点可以保留，但要变成正式算法。

### 目的

评论很多时，不把所有评论丢给大模型，而是先筛出最有代表性的评论，降低成本，提高解释性。

### 评分公式

对每条评论计算：

```text
comment_importance =
    0.35 * normalized_like_count
  + 0.25 * risk_keyword_score
  + 0.20 * reply_depth_score
  + 0.10 * emotion_intensity
  + 0.10 * temporal_turning_score
```

### 信号解释

- `like_count`：点赞越高，说明共鸣越强。
- `risk_keyword_score`：出现“集合、投诉、人肉、曝光、冲、堵门”等风险词。
- `reply_depth_score`：被回复越多，说明引发讨论。
- `emotion_intensity`：愤怒、焦虑、恐慌、讽刺强度。
- `temporal_turning_score`：是否出现在风险急剧升高的时间段。

### 伪代码

```text
Algorithm SelectTopComments(comments, top_n):
    for comment in comments:
        like_score = normalize(log(1 + comment.like_count))
        keyword_score = match_risk_keywords(comment.text)
        reply_score = normalize(comment.reply_count)
        emotion_score = estimate_emotion_intensity(comment.text)
        turning_score = detect_temporal_turning(comment.created_at)

        comment.importance =
            0.35 * like_score +
            0.25 * keyword_score +
            0.20 * reply_score +
            0.10 * emotion_score +
            0.10 * turning_score

    sort comments by importance descending
    return top_n comments
```

---

# 7.3 话题聚类算法

### 目的

校园墙同一事件可能出现多个帖子。比如：

- “今天宿舍又停电？”
- “为什么 12 点强制断电？”
- “限电影响期末复习怎么办？”

这些应该聚成一个事件，而不是三个孤立帖子。

### 推荐实现

MVP 阶段：

- 用中文句向量模型生成 embedding；
- 用余弦相似度判断是否归为同一事件；
- 相似度超过阈值 `0.78` 归并。

增强版：

- 使用 BERTopic / HDBSCAN 聚类。BERTopic 使用 transformer embeddings 和 c-TF-IDF 形成可解释的话题簇，适合从大量文本中抽取主题。([Maarten Gr.github](https://maartengr.github.io/BERTopic/index.html?utm_source=chatgpt.com))

### 伪代码

```text
Algorithm ClusterPosts(posts):
    embeddings = Encode(posts.clean_text)

    clusters = []
    for post in posts:
        best_cluster = None
        best_sim = 0

        for cluster in clusters:
            sim = cosine(post.embedding, cluster.centroid)
            if sim > best_sim:
                best_sim = sim
                best_cluster = cluster

        if best_sim >= TOPIC_THRESHOLD:
            assign post to best_cluster
            update cluster centroid
        else:
            create new cluster with post

    return clusters
```

---

# 7.4 评论链图谱构建算法

### 目的

评论区不是一堆句子，而是一条会呼吸的河流。\
我们要看清楚：

- 谁回复了谁；
- 哪条评论引发共鸣；
- 风险信号何时出现；
- 事件是降温还是升温。

NetworkX 适合做这部分，因为它是用于创建、操作和研究复杂网络结构、动态与功能的 Python 包。([NetworkX](https://networkx.org/?utm_source=chatgpt.com))

### 图结构

节点：

- 主贴节点 `post`
- 评论节点 `comment`

边：

- `reply_edge`：回复关系
- `temporal_edge`：时间先后关系
- `semantic_edge`：语义相似关系

### 节点属性

```json
{
  "risk_score": 0.72,
  "emotion": "愤怒",
  "stance": "号召",
  "like_count": 32,
  "created_at": "2026-06-23T20:30:00"
}
```

### 伪代码

```text
Algorithm BuildCommentGraph(event):
    G = DirectedGraph()

    add node event.post_id as post node

    sort comments by created_at

    for comment in comments:
        add node comment.comment_id with attributes:
            emotion, stance, like_count, risk_signals

        if comment.parent_id exists:
            add edge parent_id -> comment_id, type="reply"
        else:
            add edge post_id -> comment_id, type="reply"

    for i from 0 to len(comments)-2:
        add edge comments[i] -> comments[i+1], type="temporal"

    for each pair(comment_i, comment_j):
        if cosine(embedding_i, embedding_j) > SEMANTIC_THRESHOLD:
            add edge i -> j, type="semantic", weight=similarity

    return G
```

---

# 7.5 风险信号识别算法

### 风险信号类型

建议定义 8 类：

| 信号                    | 解释       | 示例         |
| --------------------- | -------- | ---------- |
| negative\_emotion     | 明显负面情绪   | “真的受不了了”   |
| collective\_resonance | 多人表达相同不满 | “我也是”“同感”  |
| rumor\_spread         | 未证实传闻扩散  | “听说是因为……”  |
| sarcasm               | 反讽阴阳怪气   | “学校真是太贴心了” |
| mobilization          | 行动号召     | “今晚一起去问”   |
| confrontation         | 对抗倾向     | “不解决就闹大”   |
| privacy\_leak         | 隐私泄露     | 曝光姓名、电话、宿舍 |
| offline\_risk         | 线下聚集风险   | “去楼下集合”    |

### 实现方式

MVP 用规则 + 小模型：

- 关键词词典；
- 情绪词典；
- 正则表达式；
- 简单分类器；
- 大模型复核。

增强版：

- 人工标注 500 条评论；
- 微调中文 RoBERTa / MacBERT；
- 或训练 Logistic Regression / LightGBM，特征包括 embedding + 关键词 + 互动数据。

### 伪代码

```text
Algorithm DetectRiskSignals(comment):
    signals = []

    if contains_negative_emotion(comment.text):
        signals.append("negative_emotion")

    if contains_collective_words(comment.text):
        signals.append("collective_resonance")

    if contains_uncertain_claim(comment.text):
        signals.append("rumor_spread")

    if contains_sarcasm_pattern(comment.text):
        signals.append("sarcasm")

    if contains_action_call(comment.text):
        signals.append("mobilization")

    if contains_privacy_pattern(comment.text):
        signals.append("privacy_leak")

    if contains_offline_location_and_time(comment.text):
        signals.append("offline_risk")

    return signals
```

---

# 7.6 情绪共振指数

这是你们论文最有“技术味”的指标之一。

### 定义

情绪共振不是“负面评论多”这么简单，而是同时满足：

- 多人表达相同情绪；
- 时间上集中出现；
- 互动数据较高；
- 评论之间语义相似。

### 公式

```text
ResonanceScore =
    α * negative_ratio
  + β * semantic_concentration
  + γ * interaction_amplification
  + δ * temporal_density
```

建议权重：

```text
α = 0.30
β = 0.25
γ = 0.25
δ = 0.20
```

### 各项含义

```text
negative_ratio = 负向/焦虑/愤怒评论数 / 总评论数

semantic_concentration = 高相似评论对数量 / 全部评论对数量

interaction_amplification = 高点赞风险评论点赞数 / 总点赞数

temporal_density = 风险评论在短时间窗口内的集中程度
```

### 伪代码

```text
Algorithm ComputeResonanceScore(comments):
    negative_ratio = count_negative(comments) / len(comments)

    semantic_pairs = 0
    high_sim_pairs = 0
    for each pair in comments:
        semantic_pairs += 1
        if cosine(pair.embedding) > 0.80:
            high_sim_pairs += 1
    semantic_concentration = high_sim_pairs / semantic_pairs

    risk_likes = sum(like_count of comments with risk_signals)
    total_likes = sum(all like_count) + 1
    interaction_amplification = risk_likes / total_likes

    temporal_density = max_risk_comments_in_window(comments, window=30min) / len(comments)

    score = 0.30*negative_ratio + 0.25*semantic_concentration
          + 0.25*interaction_amplification + 0.20*temporal_density

    return score
```

---

# 7.7 风险演化阶段识别

### 阶段定义

```text
S0 个体吐槽：主贴负面，但评论稀疏
S1 信息求证：评论以“真的假的”“有通知吗”为主
S2 情绪共振：多人表达相同不满
S3 立场对立：评论区出现争吵、攻击、阵营化
S4 组织化行动：出现投诉、集合、转发扩散、线下行动号召
S5 线下风险：出现明确时间地点和行动目标
```

### 阶段判断规则

| 阶段 | 触发条件              |
| -- | ----------------- |
| S0 | 主贴负面，评论少于 5 条     |
| S1 | 求证类评论比例 > 30%     |
| S2 | 共振指数 > 0.55       |
| S3 | 攻击/对立信号 > 20%     |
| S4 | 行动号召信号 ≥ 1 且互动较高  |
| S5 | 行动号召 + 时间地点 + 高互动 |

### 伪代码

```text
Algorithm InferEvolutionStage(event, comments, signals):
    if len(comments) < 5 and post_is_negative(event.post):
        return "个体吐槽"

    if ratio(stance == "求证") > 0.30:
        stage = "信息求证"

    if resonance_score > 0.55:
        stage = "情绪共振"

    if confrontation_ratio > 0.20:
        stage = "立场对立"

    if has_signal("mobilization") and key_comment_like_high:
        stage = "组织化行动"

    if has_signal("offline_risk") and contains_time_location:
        stage = "线下风险"

    return stage
```

---

# 7.8 总风险评分算法

### 风险评分公式

```text
RiskScore =
    20 * PostRisk
  + 25 * ResonanceScore
  + 20 * MobilizationScore
  + 15 * GraphInfluenceScore
  + 10 * BurstScore
  + 10 * EvidenceUncertainty
```

### 解释

- `PostRisk`：主贴风险；
- `ResonanceScore`：评论区情绪共振；
- `MobilizationScore`：行动号召强度；
- `GraphInfluenceScore`：关键评论在图中的影响力；
- `BurstScore`：短时间突增；
- `EvidenceUncertainty`：事实不清时提高复核优先级。

### 风险等级

```text
0-39   低
40-64  中
65-84  高
85-100 严重
```

### 伪代码

```text
Algorithm ComputeRiskScore(event, graph, signals, evidence):
    post_risk = compute_post_risk(event.post)
    resonance = compute_resonance_score(event.comments)
    mobilization = compute_mobilization_score(signals)
    graph_influence = compute_key_node_influence(graph)
    burst = compute_burst_score(event.comments)
    uncertainty = compute_evidence_uncertainty(evidence)

    risk_score =
        20 * post_risk +
        25 * resonance +
        20 * mobilization +
        15 * graph_influence +
        10 * burst +
        10 * uncertainty

    risk_level = map_score_to_level(risk_score)
    return risk_score, risk_level
```

---

# 7.9 关键评论发现算法

### 目的

答辩时不能只说“风险高”，必须指出：

**是哪几条评论推动了风险升级。**

### 特征

```text
comment_key_score =
    0.30 * risk_signal_score
  + 0.25 * graph_centrality
  + 0.20 * like_score
  + 0.15 * temporal_turning_score
  + 0.10 * semantic_representativeness
```

### 伪代码

```text
Algorithm RankKeyComments(comments, graph):
    centrality = PageRank(graph)

    for comment in comments:
        risk_signal_score = count(comment.risk_signals) / MAX_SIGNAL_COUNT
        graph_score = centrality[comment.comment_id]
        like_score = normalize(log(1 + comment.like_count))
        turning_score = is_before_stage_shift(comment)
        semantic_score = similarity_to_event_centroid(comment)

        comment.key_score =
            0.30*risk_signal_score +
            0.25*graph_score +
            0.20*like_score +
            0.15*turning_score +
            0.10*semantic_score

    return top_k comments by key_score
```

---

# 7.10 RAG 证据检索算法

### 目的

避免大模型胡编处置建议。

系统要检索：

- 学校通知；
- 后勤公告；
- 学生手册；
- 过往回应模板；
- 历史相似案例。

### 知识库结构

```text
knowledge_base/
├── policies/
│   ├── dormitory_rules.md
│   ├── canteen_management.md
│   └── student_appeal_process.md
├── notices/
│   ├── 2026_power_notice.md
│   └── 2026_exam_notice.md
├── response_templates/
│   ├── logistics_response.md
│   ├── rumor_clarification.md
│   └── emergency_response.md
└── history_cases/
    ├── E_old_001.md
    └── E_old_002.md
```

### 伪代码

```text
Algorithm RetrieveEvidence(event_summary):
    query = build_query(event_summary)

    dense_results = vector_search(query, top_k=5)
    keyword_results = bm25_search(query, top_k=5)

    merged = reciprocal_rank_fusion(dense_results, keyword_results)

    reranked = rerank_by:
        relevance_to_event
        source_priority
        freshness
        evidence_type

    return top 5 evidence
```

---

# 7.11 大模型结构化研判

### 输入给大模型的内容

不能把原始评论一股脑扔进去。要传结构化上下文：

```json
{
  "event_summary": "...",
  "risk_score": 83.5,
  "current_stage": "组织化行动",
  "risk_signals": [
    {"type": "mobilization", "comment_id": "C007", "text": "..."},
    {"type": "collective_resonance", "comment_id": "C012", "text": "..."}
  ],
  "key_comments": ["C007", "C012"],
  "evidence": [
    {"title": "宿舍管理规定", "content": "..."}
  ],
  "baseline_result": {
    "keyword_method": "中风险",
    "comment_chain_method": "高风险"
  }
}
```

### 输出 JSON Schema

```json
{
  "event_summary": "string",
  "risk_reason": "string",
  "evolution_explanation": ["string"],
  "key_comment_explanations": [
    {
      "comment_id": "string",
      "reason": "string",
      "risk_signal": "string"
    }
  ],
  "intervention": {
    "official_statement": "string",
    "action_items": ["string"],
    "avoid_phrases": ["string"],
    "responsible_department": ["string"],
    "urgency": "string"
  },
  "human_review_required": true
}
```

官方结构化输出文档建议先定义 JSON Schema，并用结构化格式让模型响应；文档还建议字段名清晰、重要字段有标题和描述，并通过 evals 测试结构是否适合场景。([OpenAI平台](https://platform.openai.com/docs/guides/structured-outputs))

### 伪代码

```text
Algorithm GenerateLLMReport(assessment, evidence):
    prompt = load_prompt("risk_assessment_zh.md")

    llm_input = {
        assessment,
        evidence,
        key_comments,
        baseline_results
    }

    response = call_llm_with_json_schema(prompt, llm_input, FinalReportSchema)

    try:
        report = PydanticValidate(response)
    except ValidationError:
        report = fallback_template(assessment, evidence)

    return report
```

---

## 8. 基线方法与对比实验设计

这个模块非常重要，因为初版也要求导出“有/无评论区对比实验数据”给论文组。你们要把这个变成正式实验。

### 8.1 方法对比

| 方法         | 输入                 | 技术      | 作用           |
| ---------- | ------------------ | ------- | ------------ |
| Baseline A | 主贴                 | 关键词匹配   | 模拟传统舆情系统     |
| Baseline B | 主贴                 | 情感分析    | 判断负面倾向       |
| Baseline C | 主贴 + 评论            | 大模型直接判断 | 证明裸 LLM 的不稳定 |
| Ours-1     | 主贴 + 评论 + 时间       | 评论链演化   | 证明时间顺序有用     |
| Ours-2     | 主贴 + 评论 + 图谱 + RAG | 完整系统    | 最终方法         |

### 8.2 评价指标

```text
风险等级准确率 Accuracy
高风险召回率 High-risk Recall
关键评论命中率 Key Comment Hit Rate
阶段识别准确率 Stage Accuracy
处置建议人工评分 Human Rating
JSON有效率 Schema Valid Rate
```

### 8.3 实验输出

```text
outputs/experiment_results/
├── baseline_keyword.csv
├── baseline_sentiment.csv
├── llm_direct.csv
├── ours_comment_chain.csv
├── ours_full.csv
└── ablation_summary.csv
```

### 8.4 消融实验

```text
完整系统
- 去掉评论区
- 去掉时间顺序
- 去掉图谱中心性
- 去掉RAG证据
- 去掉大模型解释
```

你们论文里就写：

> 实验表明，仅基于主贴的关键词方法容易漏判反讽、情绪共振和组织化倾向；引入评论链结构、时间演化和关键评论排序后，系统能够更准确地定位风险升级节点。

---

## 9. 前端 Demo 设计

### 9.1 页面一：事件总览

展示：

- 今日事件数；
- 高风险事件数；
- 风险趋势折线；
- 事件类型分布；
- 高风险事件列表。

视觉建议：

```text
左侧：筛选栏
中间：事件卡片
右侧：风险分布小图
```

### 9.2 页面二：单事件分析

展示：

- 主贴文本；
- 评论区；
- 风险分数；
- 当前阶段；
- 演化路径；
- 关键评论；
- 评论图谱。

### 9.3 页面三：对比实验

这页是答辩杀手锏。

```text
关键词法：中风险，只命中“投诉”
情感法：中风险，负面占比 46%
裸 LLM：中风险，未指出关键评论
群声雷达：高风险，命中 C007 线下行动号召
```

### 9.4 页面四：证据化处置

展示：

- 检索到的通知/校规；
- 证据匹配程度；
- 建议回应话术；
- 不建议使用的话术；
- 责任部门；
- 24 小时处置流程。

### 9.5 页面五：报告导出

导出 Markdown 或 PDF：

```text
事件摘要
风险等级
演化路径
关键评论
证据链
处置建议
人工复核建议
```

---

## 10. 模块通信与解耦设计

### 10.1 解耦原则

不要让模块直接读取彼此内部变量。所有模块只通过标准对象通信。

```text
Event -> CommentGraph -> RiskSignal[] -> RiskAssessment -> Evidence[] -> FinalReport
```

### 10.2 服务层接口

```python
class TopicService:
    def cluster_posts(self, posts: list[Post]) -> list[CampusEvent]:
        ...

class GraphService:
    def build_comment_graph(self, event: CampusEvent) -> CommentGraph:
        ...

class RiskService:
    def assess(self, event: CampusEvent, graph: CommentGraph) -> RiskAssessment:
        ...

class RagService:
    def retrieve(self, query: str) -> list[Evidence]:
        ...

class LLMService:
    def generate_report(
        self,
        event: CampusEvent,
        assessment: RiskAssessment,
        evidence: list[Evidence]
    ) -> FinalReport:
        ...
```

### 10.3 可扩展点

未来可以替换：

- 情绪识别模型；
- 立场识别模型；
- 向量数据库；
- 大模型供应商；
- 前端框架；
- 数据源。

只要 schema 不变，其他模块不用大改。

---

## 11. 部署方案

### 11.1 本地开发模式

```bash
# 1. 创建环境
python -m venv .venv

# 2. 激活环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动后端
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 5. 启动前端
streamlit run frontend/streamlit_app.py
```

### 11.2 Docker Compose 部署

Docker Compose 官方定位就是用来定义和运行多容器应用，可以通过一个 YAML 文件管理服务、网络和卷，适合你们把前端、后端、数据库和向量库一起拉起来。([Docker Documentation](https://docs.docker.com/compose/?utm_source=chatgpt.com))

`docker-compose.yml`：

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
      - ./outputs:/app/outputs

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
```

启动：

```bash
docker compose up --build
```

### 11.3 答辩兜底模式

必须做。

```text
实时模式：
前端 -> 后端 -> 算法 -> LLM API -> 返回报告

演示模式：
前端 -> 后端 -> cache/demo_reports/E001.json -> 返回报告
```

前端加一个开关：

```text
[ ] 实时分析
[x] 演示缓存
```

初版已经提醒“API 现场抽风时要做缓存，Demo 有实时/演示双模式按钮”，这一条必须保留。

---

## 12. 开发工作流

### 12.1 分支策略

```text
main          稳定可演示版本
dev           日常开发版本
feature/data  数据处理
feature/api   后端接口
feature/ui    前端页面
feature/algo  算法模块
feature/llm   大模型与RAG
```

### 12.2 每日开发顺序

第一阶段：跑通闭环。

```text
Day 1:
  数据样例 JSON
  FastAPI /health
  Streamlit 调后端
  单案例展示

Day 2:
  数据脱敏
  评论预过滤
  关键词基线
  风险评分初版

Day 3:
  评论图谱
  关键评论排序
  LLM结构化报告
  缓存模式

Day 4:
  RAG证据检索
  对比实验页面
  报告导出
  演示脚本

Day 5:
  Bug修复
  UI美化
  论文实验导出
  答辩演练
```

### 12.3 Pull Request 检查清单

每次合并前检查：

```text
[ ] 是否通过 pytest
[ ] 是否通过 ruff/black 格式检查
[ ] 是否没有上传 raw 数据
[ ] 是否没有提交 API Key
[ ] 是否更新 docs/api.md
[ ] 是否新增必要单元测试
[ ] 是否缓存了演示案例结果
```

---

## 13. 编码规范

### 13.1 Python 规范

- Python 版本：3.11+
- 全部函数必须有类型标注。
- 业务对象必须用 Pydantic schema。
- 算法函数不要直接读文件。
- 服务层不要写 UI。
- API 层不要写算法。
- 大模型调用必须有超时、重试、缓存、schema 校验。

示例：

```python
def compute_resonance_score(comments: list[Comment]) -> float:
    """计算评论区情绪共振指数，返回 0-1 之间的分数。"""
    if not comments:
        return 0.0
    ...
```

### 13.2 命名规范

```text
文件名：snake_case.py
类名：PascalCase
函数名：snake_case
变量名：snake_case
常量名：UPPER_CASE
API路径：kebab-case 或 snake_case，保持统一
```

### 13.3 日志规范

日志至少记录：

```text
event_id
module
duration_ms
mode: realtime/cached
llm_model
cache_hit
error_type
```

示例：

```python
logger.info(
    "risk_assessment_finished",
    extra={
        "event_id": event.event_id,
        "risk_score": assessment.risk_score,
        "duration_ms": duration_ms,
        "mode": mode,
    },
)
```

### 13.4 大模型调用规范

必须满足：

```text
1. 所有 prompt 放在 backend/app/llm/prompts/
2. 所有输出必须走 JSON Schema
3. 所有输出必须 Pydantic 校验
4. 校验失败走 fallback_template
5. 结果写入 cache/llm_responses/
6. 不允许在 prompt 中放真实个人信息
```

### 13.5 前端规范

- 页面只调用 API，不直接跑算法。
- 图表数据由后端返回 JSON。
- 每个页面一个主任务。
- 所有异常都要展示为用户可读提示。
- 答辩用案例必须固定排序，避免现场找不到。

---

## 14. 最小可行版本 MVP

你们时间有限，先做 MVP，再做增强。

### MVP 必须完成

```text
1. 导入 5-10 个脱敏校园墙案例
2. 展示事件列表
3. 单事件分析
4. 评论预过滤
5. 风险信号识别
6. 风险评分
7. 关键评论排序
8. LLM结构化报告
9. 关键词法 vs 评论链法对比
10. 缓存模式
```

### 增强版再做

```text
1. 话题聚类
2. RAG证据检索
3. 评论图谱可视化
4. PDF报告导出
5. 批量实验评估
6. OCR图文分析
```

---

## 15. 答辩演示路径

现场演示别乱点，固定剧本：

```text
第一步：打开事件总览
  展示系统不是单案例脚本，而是有事件列表和风险排序。

第二步：选择“宿舍限电争议”
  展示主贴和评论区。

第三步：点击“运行分析”
  展示风险阶段从“信息求证”到“情绪共振”再到“组织化行动”。

第四步：展示关键评论
  指出哪条评论导致风险升级。

第五步：切到“对比实验”
  传统关键词法只识别到负面情绪，但群声雷达识别出组织化行动。

第六步：展示证据化处置
  系统给出温和回应话术、行动建议、责任部门和避免话术。

第七步：导出报告
  证明系统有实际应用闭环。
```

---

## 16. 论文实现路径

论文不要写产品商业模式。初版也已经说明论文线要围绕“基于对话链的校园舆情语义分析框架”，并做“有/无评论区效果对比”的消融实验。你们最终论文可以升级成：

**《面向校园墙场景的评论链驱动舆情风险演化识别方法研究》**

论文方法章节对应代码模块：

```text
3.1 数据采集与脱敏          -> anonymize_service.py
3.2 评论链建模              -> comment_graph.py
3.3 风险信号识别            -> risk_scoring.py
3.4 情绪共振指数            -> risk_scoring.py
3.5 关键评论排序            -> key_comment_ranker.py
3.6 大模型结构化研判        -> llm_service.py
3.7 RAG证据化处置           -> rag_service.py
```

实验章节对应：

```text
4.1 数据集构建
4.2 标注规范
4.3 对比方法
4.4 消融实验
4.5 结果分析
4.6 案例分析
```

---

## 17. 最终技术亮点提炼

答辩时可以讲 4 个创新点：

### 创新点一：从“帖子级判断”升级为“评论链演化判断”

传统方法看主贴，我们看主贴、评论、回复、时间和互动。

### 创新点二：提出校园舆情情绪共振指数

不是简单负面情感，而是综合情绪比例、语义集中、互动放大和时间密度。

### 创新点三：关键评论定位

系统能指出风险升级的触发评论，而不是只给一个分数。

### 创新点四：证据化处置

处置建议来自校规、通知、历史案例和模板检索，不是大模型凭空发挥。

---

## 18. 你们真正应该交付的东西

最终项目交付清单：

```text
代码：
  campus-opinion-radar 完整仓库
  可运行前端
  可运行后端
  缓存演示案例

数据：
  脱敏校园墙案例
  人工标注表
  知识库文档
  对比实验结果

文档：
  README.md
  design.md
  api.md
  annotation_guide.md
  demo_script.md

答辩：
  PPT
  Demo
  Q&A
  竞品对比表

论文：
  技术论文
  实验结果表
  消融实验图
  案例分析图
```

---

# 最终建议版本

你们现在不要从“大而全”开始写代码。最稳路线是：

```text
第 1 个闭环：
脱敏案例 -> 风险评分 -> 大模型结构化报告 -> 前端展示

第 2 个闭环：
关键词法对比 -> 关键评论定位 -> 对比实验页

第 3 个闭环：
评论图谱 -> 情绪共振指数 -> 风险演化路径

第 4 个闭环：
RAG证据检索 -> 处置建议 -> 报告导出
```

最小可演示核心是：

> 选择一个校园墙事件，系统展示评论区如何把事件从“个体吐槽”推向“情绪共振”甚至“组织化行动”，并指出关键评论、给出证据化处置建议。

这就是你们项目的灵魂：\
**不是压住声音，而是听懂声音；不是监控学生，而是让问题在变成风暴前被看见。**
