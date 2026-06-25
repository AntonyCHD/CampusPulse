# 快速启动指南

## 🚀 一键启动

**推荐方式：双击启动脚本**

```bash
# Windows 系统
start.bat

# 或命令行运行
./start.bat
```

启动后会自动打开两个窗口：
- **后端服务**：FastAPI (端口 8000)
- **前端服务**：Vue 3 (端口 5173)

## 🌐 访问地址

启动成功后，在浏览器访问：

- **前端界面**：http://localhost:5173
- **后端 API 文档**：http://localhost:8000/docs
- **后端健康检查**：http://localhost:8000/health

## 📋 手动启动

如果需要分别启动前后端：

### 1. 启动后端

```bash
# 进入项目根目录
cd "C:\Users\31982\Desktop\代码\舆情与媒体安全"

# 启动 FastAPI
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### 2. 启动前端

```bash
# 进入前端目录
cd frontend-vue

# 启动 Vite 开发服务器
npm run dev
```

## 🛑 停止服务

### 方式一：关闭命令行窗口

直接关闭运行服务的命令行窗口

### 方式二：查找并终止进程

```bash
# 查找占用端口的进程
netstat -ano | findstr "8000 5173"

# 强制关闭进程（替换 <PID> 为实际进程 ID）
taskkill /F /PID <PID>
```

## 🐛 常见问题

### 问题 1：端口被占用

**现象**：启动时提示端口已被占用

**解决**：
```bash
# 查找占用 8000 和 5173 端口的进程
netstat -ano | findstr "8000 5173"

# 强制关闭这些进程
taskkill /F /PID <进程ID>
```

### 问题 2：前端无法连接后端

**现象**：前端页面显示"加载失败"或 API 错误

**解决**：
1. 确认后端已启动在 8000 端口
2. 检查浏览器控制台是否有跨域错误
3. 确认 Vite 代理配置正确（`frontend-vue/vite.config.ts`）

### 问题 3：依赖安装失败

**后端依赖问题**：
```bash
# 重新安装 Python 依赖
pip install -r requirements.txt --force-reinstall

# 如果使用虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**前端依赖问题**：
```bash
cd frontend-vue

# 清除缓存并重新安装
rm -rf node_modules package-lock.json
npm install
```

### 问题 4：模型下载失败

**现象**：首次启动时 BGE-M3 模型下载失败

**解决**：
- 确保网络可以访问 HuggingFace
- 模型会自动下载到 `~/.cache/huggingface/`
- 下载约 2GB，需要一定时间

## 📦 系统要求

### 后端
- Python 3.9+
- 8GB+ 内存（用于模型加载）
- 10GB+ 磁盘空间（用于模型缓存）

### 前端
- Node.js 16+
- npm 或 yarn

## 📚 更多文档

- [完整启动指南](docs/STARTUP_GUIDE.md)
- [项目 README](README.md)
- [MVP 完成总结](docs/MVP_COMPLETE_SUMMARY.md)

---

**提示**：首次启动会下载 BGE-M3 模型，可能需要 5-10 分钟。后续启动会使用缓存，速度会更快。
