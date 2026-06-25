# 校园舆情监测系统 - 启动指南

## ✅ 系统组成

- **后端**: FastAPI (端口 8000)
- **前端**: Vue 3 + Element Plus (端口 5173)

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd "C:\Users\31982\Desktop\代码\舆情与媒体安全"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

后端API将运行在: http://localhost:8000

### 2. 启动前端服务

```bash
cd "C:\Users\31982\Desktop\代码\舆情与媒体安全\frontend-vue"
npm run dev
```

前端界面将运行在: http://localhost:5173

### 3. 访问系统

在浏览器中打开: **http://localhost:5173**

## 📋 功能页面

1. **事件总览** (/)
   - 查看所有事件列表
   - 支持风险等级和事件类型筛选
   - 显示评论数和点赞数

2. **单事件分析** (/event/:id)
   - 风险等级、分数、当前阶段
   - 演化路径可视化
   - 风险信号详细列表
   - 关键评论识别

3. **评论图谱** (/graph/:id)
   - 网络图谱可视化
   - 三种边类型（回复边、时间边、语义边）
   - 节点按风险着色
   - 可切换边类型显示

4. **方法对比** (/comparison)
   - 关键词法 vs 情感分析法 vs 评论链演化法
   - 并排对比三种方法的结果
   - 方法优劣分析

5. **报告导出** (/report/:id)
   - 完整分析报告预览
   - 导出Markdown格式
   - 包含风险评估和处置建议

## 🔧 技术栈

### 后端
- FastAPI 0.115.0
- BGE-M3 (语义向量)
- NetworkX (图算法)
- PyVis (图谱可视化)

### 前端
- Vue 3.5
- TypeScript
- Vite 8.1.0
- Element Plus
- vis-network (网络图)
- Axios

## 📊 测试数据

- 事件总数: 39个
- 评论总数: 2363条
- 示例事件ID: E2889899

## 🛠️ 开发命令

### 后端
```bash
# 启动后端（开发模式）
uvicorn backend.app.main:app --reload

# 运行测试
python scripts/test_api.py

# 重新导入数据
python scripts/ingest_data.py
```

### 前端
```bash
cd frontend-vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 📝 API端点

- `GET /api/events/` - 获取事件列表
- `POST /api/analyze/{event_id}` - 分析事件
- `GET /api/graph/{event_id}` - 获取图谱数据
- `GET /api/report/{event_id}` - 获取报告
- `POST /api/baseline/{event_id}` - 基线对比

## ⚠️ 注意事项

1. **首次分析较慢**: 需要加载BGE-M3模型（~2GB），首次运行会下载模型文件
2. **缓存机制**: 分析结果会自动缓存，后续访问速度更快
3. **端口占用**: 确保8000和5173端口未被占用
4. **数据准备**: 确保已运行`python scripts/ingest_data.py`导入数据

## 🐛 常见问题

### 问题1: 前端无法连接后端
**解决**: 确保后端服务已启动在8000端口，Vite已配置代理

### 问题2: 模型加载失败
**解决**: 检查网络连接，模型会从HuggingFace下载

### 问题3: 图谱不显示
**解决**: 检查浏览器控制台错误，确保vis-network已安装

## 📦 生产部署

### 后端部署
```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 前端部署
```bash
cd frontend-vue
npm run build
# dist/ 目录部署到 Nginx/Apache
```

### Nginx 配置示例
```nginx
server {
    listen 80;
    
    # 前端
    location / {
        root /path/to/frontend-vue/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🎉 系统特性

- ✅ 响应式设计，自适应各种屏幕
- ✅ 实时数据加载，自动缓存
- ✅ 交互式图谱可视化
- ✅ 完整的类型安全（TypeScript）
- ✅ 优雅的UI设计（Element Plus）
- ✅ 快速开发体验（Vite HMR）

---

**当前状态**: 
- ✅ 后端API正常运行
- ✅ Vue前端成功启动
- ✅ 所有5个页面已实现
- ✅ 系统可以完整使用

**访问地址**: http://localhost:5173
