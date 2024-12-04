# 小栋FRPS管理工具 (FrpsManager-GUI)

一个简单易用的 FRPS 图形化管理工具，帮助用户快速配置和管理 FRPS 服务。

## 功能特点

- 图形化界面，操作简单直观
- 支持自定义服务端口和映射端口
- 实时显示服务状态
- 自动检查更新
- 一键启动/停止服务
- 端口占用自动检测
- 界面简洁，使用方便

## 系统要求

- Windows 7/8/10/11
- Python 3.6 或更高版本（如果从源码运行）
- 网络连接

## 安装使用

### 方式一：直接使用发布版本

1. 从 [发布页面](https://blog.biekanle.com/software/1255.html) 下载最新版本
2. 解压下载的文件
3. 运行 `小栋FRPS管理工具.exe`

### 方式二：从源码运行

1. 克隆仓库
```bash
git clone https://github.com/xiaodong1111/FrpsManager-GUI
cd FrpsManager-GUI
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行程序
```bash
python frps_gui.py
# 或者使用
start.bat
```

## 依赖

这个项目依赖以下第三方库：

- PyQt6 - GUI框架
- psutil - 用于系统进程管理
- requests - 用于网络请求和更新检查
- pyinstaller - 用于将Python程序打包成exe文件

用户可以通过以下命令一键安装所有依赖：

```bash
pip install -r requirements.txt
```

## 打包说明

如果你想将源码打包成可执行文件，可以使用以下命令：

```bash
# 方式一：使用打包脚本
build.bat

# 方式二：直接使用 pyinstaller
pyinstaller frps_gui.spec
```

打包完成后，可执行文件将生成在 `dist` 目录中。