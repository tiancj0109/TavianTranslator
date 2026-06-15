# Tavian Translator

基于 PyQt5 和腾讯云翻译 API 实现的 Windows 桌面极简翻译器。

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![Tencent Cloud](https://img.shields.io/badge/Tencent%20Cloud-TMT-blue.svg?style=flat-square&logo=tencent-cloud&logoColor=white)](https://cloud.tencent.com/product/tmt)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg?style=flat-square)](LICENSE)

---

## 项目简介

Tavian Translator 是一款专为高效工作流设计的 Windows 极简桌面翻译工具。它通过现代化、直观的 PyQt5 图形界面，为用户提供纯净、快速的高质量翻译体验。

---

## 核心特性

* **多语种互译**：支持中文、英文、日文、韩文互译，具备源语言自动检测功能。
* **极简桌面交互**：
  * 支持窗口始终置顶，方便对照阅读与输入。
  - 支持智能贴边定位与位置记忆，首次启动自动贴合屏幕右下角。
  - 支持无缝拖拽移动与窗口大小调整。
* **高效快捷键**：
  - `Shift + Space` 快速执行翻译。
  - `Shift + Esc` 隐藏窗口至系统托盘。
* **后台常驻与托盘**：最小化或关闭窗口时自动隐藏至系统托盘，支持开机自启配置，支持托盘菜单一键呼出与完全退出。
* **一键复制结果**：点击复制按钮即可将翻译结果存入剪贴板，并提供流畅的成功状态反馈。

---

## 技术架构

* **编程语言**：Python 3.12
* **GUI 框架**：PyQt5 (结合 QSS/CSS 样式表进行定制化 UI 设计)
* **翻译后端**：腾讯云机器翻译（TMT）SDK (`tencentcloud-sdk-python`)
* **配置持久化**：Windows `QSettings` 注册表存储

---

## 快速开始

### 1. 安装依赖

确保本地已安装 Python 3.8+ 环境，在项目根目录下执行以下命令安装依赖：

```bash
pip install PyQt5 tencentcloud-sdk-python
```

### 2. 配置 API 密钥

为保障 API 密钥安全，项目采用**环境变量**与**本地配置文件**双重读取机制。请任选以下一种方式配置您的腾讯云 API 密钥：

#### 方法 A：本地配置文件（推荐）
在项目根目录下创建 `config.json` 文件（该文件已被加入 `.gitignore` 规则中，不会被提交至仓库）：

```json
{
  "TENCENTCLOUD_SECRET_ID": "您的 SecretId",
  "TENCENTCLOUD_SECRET_KEY": "您的 SecretKey"
}
```

#### 方法 B：环境变量
将以下密钥配置到系统的环境变量中：
* `TENCENTCLOUD_SECRET_ID`
* `TENCENTCLOUD_SECRET_KEY`

### 3. 启动程序

密钥配置完成后，在根目录下执行：

```bash
python translator_app.py
```

---

## 独立打包

项目已配置好 PyInstaller 打包流程，您可以直接运行以下命令将脚本打包为无需 Python 环境的独立 Windows 可执行程序 (`.exe`)：

```bash
pyinstaller --noconfirm --onefile --windowed --name TranslatorApp translator_app.py
```

打包完成后，独立的可执行文件将生成在 `dist/` 目录下。

---

## 安全与隐私说明

* **密钥安全**：请勿将包含真实腾讯云 API 密钥的 `config.json` 文件或修改后的硬编码代码推送到任何公共 Git 仓库。
* **网络连接**：本程序翻译功能依赖腾讯云 API，运行时需保持网络畅通。

---

## 开源协议

本项目基于 [MIT License](LICENSE) 协议开源。