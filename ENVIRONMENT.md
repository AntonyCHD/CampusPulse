# 项目环境配置说明

## 虚拟环境

项目使用独立的 Python 虚拟环境：`.venv`

### 首次安装步骤

1. **安装依赖**（首次运行或更新依赖时）：
   ```bash
   # 双击运行
   install_deps.bat
   ```
   
   此脚本会：
   - 激活 .venv 虚拟环境
   - 升级 pip
   - 安装最新兼容版本的依赖（requirements_latest.txt）
   - 安装 PyTorch GPU 版本（CUDA 11.8）

2. **启动系统**：
   ```bash
   # 双击运行
   start.bat
   ```
   
   此脚本会：
   - 自动激活 .venv 虚拟环境
   - 检查依赖是否安装完整
   - 启动后端（FastAPI，端口 8000）
   - 启动前端（Vue，端口 5173）

### 依赖版本

- **requirements_latest.txt**: 最新兼容版本，使用 .venv 环境
- **requirements.txt**: 原始版本，已过时，不推荐使用

### 手动激活环境

如果需要手动操作：

```bash
# Windows
.venv\Scripts\activate

# 安装依赖
pip install -r requirements_latest.txt

# 安装 PyTorch GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 退出环境
deactivate
```

### CUDA 版本选择

如果你的显卡驱动支持不同的 CUDA 版本：

- **CUDA 11.8**: `--index-url https://download.pytorch.org/whl/cu118`
- **CUDA 12.1**: `--index-url https://download.pytorch.org/whl/cu121`
- **仅 CPU**: `pip install torch torchvision torchaudio`

修改 `install_deps.bat` 中的第 18 行以更改 CUDA 版本。

### 清理

删除虚拟环境：
```bash
rmdir /s /q .venv
```

---

**创建日期**: 2026-06-25  
**Python 版本**: 3.11  
**虚拟环境工具**: venv
