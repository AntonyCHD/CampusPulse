# 群声雷达 - Campus Opinion Radar

面向校园墙场景的舆情风险演化与证据化处置平台

## 项目简介

群声雷达是一套基于授权校园墙数据的轻量化舆情风险演化分析平台，融合评论链建模、情绪共振识别、事实核验 RAG 与大模型辅助研判，帮助高校从"被动看见负面帖子"升级为"提前理解事件如何发酵并给出有证据的温和处置建议"。

## 核心功能

- **事件总览**: 查看所有校园墙事件，按风险等级筛选
- **单事件分析**: 深度分析单个事件的风险演化路径
- **对比实验**: 对比不同方法的风险识别效果
- **证据化处置**: 基于证据生成处置建议
- **报告导出**: 导出分析报告（Markdown/PDF）

## 技术架构

- **前端**: Streamlit
- **后端**: FastAPI + Python 3.11+
- **语义表示**: BGE-M3 中文向量模型
- **图分析**: NetworkX 评论链建模
- **大模型**: OpenAI-compatible API
- **存储**: SQLite + FAISS/Chroma

## 快速开始

### 1. 环境要求

- Python 3.11+
- 8GB+ RAM（运行 embedding 模型）
- 可选：CUDA（加速向量计算）

### 2. 本地开发模式

```bash
# 创建虚拟环境
python -m venv .venv

# 激活环境（Windows）
.venv\Scripts\activate

# 激活环境（macOS/Linux）
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API Key 等配置

# 启动后端
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
streamlit run frontend/streamlit_app.py
```

访问地址：
- 前端：http://localhost:8501
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 3. Docker Compose 部署

```bash
# 构建并启动
docker compose up --build

# 后台运行
docker compose up -d

# 停止服务
docker compose down
```

## 项目结构

```
campus-opinion-radar/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── schemas/     # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   ├── algorithms/  # 核心算法
│   │   ├── llm/         # 大模型调用
│   │   └── storage/     # 数据存储
│   └── tests/           # 单元测试
├── frontend/            # 前端应用
│   ├── pages/          # 页面
│   └── components/     # 组件
├── data/               # 数据目录
│   ├── raw/           # 原始数据（不提交）
│   ├── processed/     # 处理后数据
│   ├── labels/        # 人工标注
│   └── demo_cases/    # 演示案例
├── cache/             # 缓存目录
├── outputs/           # 输出目录
├── docs/              # 文档
└── scripts/           # 脚本工具
```

## 开发规范

详见 [docs/开发规范与部署.md](docs/开发规范与部署.md)

## MVP 开发路线

详见 [docs/MVP开发文档.md](docs/MVP开发文档.md)

## 实验与论文

详见 [docs/实验与论文设计.md](docs/实验与论文设计.md)

## 答辩与展示

详见 [docs/答辩展示与交付清单.md](docs/答辩展示与交付清单.md)

## 隐私与安全

- 所有数据必须经过脱敏处理
- 不上传原始个人信息到 Git
- 演示模式优先使用缓存数据
- 详见 [docs/开发规范与部署.md](docs/开发规范与部署.md) 隐私规范章节

## License

待定

## 团队

Campus Opinion Radar Team
