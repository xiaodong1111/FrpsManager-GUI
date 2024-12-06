import os
import sys
import subprocess
import psutil
import socket
import webbrowser
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QTextEdit, QMessageBox, QInputDialog, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
CURRENT_VERSION = "1.0.2"
VERSION_API = "https://www.dazhuzai.cn/api.php"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except:
            return True

def kill_frpc_process():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'frpc.exe':
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FRPSThread(QThread):
    output_signal = pyqtSignal(str)
    success_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    
    def __init__(self, server_port, remote_port, server_config=1):
        super().__init__()
        self.server_port = server_port
        self.remote_port = remote_port
        self.server_config = server_config  # 1 表示服务器1，2 表示服务器2
        self.process = None
        
    def run(self):
        try:
            # 先终止已存在的frpc进程
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == 'frpc.exe':
                        proc.kill()
                except:
                    pass
            
            # 根据不同服务器选择不同配置
            if self.server_config == 1:
                config = f"""[common]
server_addr = xxxx
server_port = 15443
token = xMR8FijgeyRGXmvy

[tcp_{self.server_port}]
type = tcp
local_ip = 127.0.0.1
local_port = {self.remote_port}
remote_port = {self.server_port}
"""
            else:
                config = f"""[common]
server_addr = xxxx
server_port = 7000
token = token123456

[tcp_{self.server_port}]
type = tcp
local_ip = 127.0.0.1
local_port = {self.remote_port}
remote_port = {self.server_port}
"""
            # 创建临时配置文件用于frpc运行
            temp_config_path = 'temp_frpc.ini'
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                f.write(config)

            # 使用临时配置文件启动frpc
            CREATE_NO_WINDOW = 0x08000000
            self.process = subprocess.Popen(
                ['frpc.exe', '-c', temp_config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=CREATE_NO_WINDOW
            )
            
            # 等待一段时间确保frpc已经读取配置文件
            import time
            time.sleep(1)
            
            # 删除临时配置文件
            try:
                os.remove(temp_config_path)
            except:
                pass
            
            while self.process.poll() is None:
                output = self.process.stdout.readline()
                if output and ("start proxy success" in output or "success" in output.lower()):
                    self.success_signal.emit()
                    break  # 成功后停止读取更多输出
                    
        except Exception as e:
            self.output_signal.emit(f"错误: {str(e)}")
            try:
                os.remove(temp_config_path)
            except:
                pass

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.stop_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 检查更新
        self.check_update()
        
        # 设置应用图标
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        
        # 禁止调整窗口大小
        self.setFixedSize(600, 400)
        
        self.frps_thread = None
        
        self.setWindowTitle("小栋FRPS管理工具")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        self.create_controls(layout)
        main_widget.setLayout(layout)
        
        # 设置白色主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 3px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)
        
    def create_controls(self, layout):
        port_layout = QHBoxLayout()
        
        server_port_label = QLabel("服务端口:")
        self.server_port_input = QLineEdit()
        self.server_port_input.setText("")
        
        proxy_port_label = QLabel("映射端口:")
        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setText("")
        
        port_layout.addWidget(server_port_label)
        port_layout.addWidget(self.server_port_input)
        port_layout.addWidget(proxy_port_label)
        port_layout.addWidget(self.proxy_port_input)
        
        # 修改服务器选择下拉框部分
        server_select_layout = QHBoxLayout()
        server_select_widget = QWidget()  # 创建一个容器widget
        server_select_widget.setStyleSheet("""
            QWidget {
                border: 1px solid #cccccc;
                padding: 5px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #cccccc;
                padding: 3px;
                min-width: 100px;
            }
            QComboBox:hover {
                border: 1px solid #bbbbbb;
            }
            QLabel {
                border: none;
            }
        """)
        
        server_inner_layout = QHBoxLayout()  # 创建内部布局
        server_inner_layout.setContentsMargins(5, 5, 5, 5)  # 设置内边距
        
        server_label = QLabel("选择服务器:")
        self.server_combo = QComboBox()
        self.server_combo.addItems(["服务器1", "服务器2"])
        
        server_inner_layout.addWidget(server_label)
        server_inner_layout.addWidget(self.server_combo)
        server_inner_layout.addStretch()
        
        server_select_widget.setLayout(server_inner_layout)
        server_select_layout.addWidget(server_select_widget)
        server_select_layout.addStretch()
        
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("启动FRPS")
        self.stop_button = QPushButton("停止FRPS")
        
        self.start_button.clicked.connect(self.start_frps)
        self.stop_button.clicked.connect(self.stop_frps)
        
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        layout.addLayout(port_layout)
        layout.addLayout(server_select_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_area)
            
    def update_log(self, text):
        if text == "FRPS停止":
            self.log_area.clear()
            # 恢复黑色加粗文本样式
            self.log_area.setStyleSheet("""
                QTextEdit {
                    color: black;
                    background-color: white;
                    border: 1px solid #cccccc;
                    font-weight: bold;  /* 添加加粗 */
                }
            """)
            self.log_area.append(text)

    def start_frps(self):
        try:
            server_port = int(self.server_port_input.text())
            proxy_port = int(self.proxy_port_input.text())
            
            if not (1024 <= server_port <= 65535) or not (1024 <= proxy_port <= 65535):
                QMessageBox.warning(self, "错误", "端口号必须在1024-65535之间")
                return
            
            if is_port_in_use(server_port):
                kill_frpc_process()
                if is_port_in_use(server_port):
                    QMessageBox.warning(self, "错误", f"本地端口 {server_port} 已被占用，请检查是否有其他程序在使用此端口")
                    return
            
            # 获取选择的服务器配置（1或2）
            server_config = self.server_combo.currentIndex() + 1
            
            self.frps_thread = FRPSThread(server_port, proxy_port, server_config)
            self.frps_thread.output_signal.connect(self.update_log)
            self.frps_thread.success_signal.connect(self.on_frps_success)
            self.frps_thread.start()
            
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的端口号")

    def on_frps_success(self):
        self.log_area.clear()
        QMessageBox.information(self, "提示", "FRPS启动成功")
        # 设置绿色加粗文本样式
        self.log_area.setStyleSheet("""
            QTextEdit {
                color: #2ecc71;  /* 使用绿色 */
                background-color: white;
                border: 1px solid #cccccc;
                font-weight: bold;  /* 添加加粗 */
            }
        """)
        self.log_area.append(f"服务端口: {self.server_port_input.text()}, 映射端口: {self.proxy_port_input.text()}")
    def stop_frps(self, show_message=True):
        if self.frps_thread:
            self.frps_thread.stop_signal.connect(lambda: self.on_frps_stop(show_message))
            self.frps_thread.stop()
            self.frps_thread = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_frps_stop(self, show_message=True):
        self.log_area.clear()
        # 恢复黑色加粗文本样式
        self.log_area.setStyleSheet("""
            QTextEdit {
                color: black;
                background-color: white;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        self.log_area.append("FRPS已停止")
        if show_message:
            QMessageBox.information(self, "提示", "FRPS已停止")

    def closeEvent(self, event):
        # 调用stop_frps时不显示停止提示
        self.stop_frps(show_message=False)
        QMessageBox.information(self, "提示", "软件已关闭")
        event.accept()

    def check_update(self):
        """检查软件更新"""
        try:
            response = requests.get(VERSION_API, timeout=3)
            if response.status_code == 200:
                data = response.json()
                server_version = data.get('version')
                update_url = data.get('update_url')
                update_msg = data.get('update_msg', '').replace('\\n', '\n')  # 替换转义字符
                
                if server_version > CURRENT_VERSION:
                    message = f"发现新版本 {server_version}\n\n{update_msg}"
                    # 强制更新提示
                    QMessageBox.warning(
                        self,
                        "版本更新",
                        message + "\n\n当前版本已停用，请立即更新！"
                    )
                    webbrowser.open(update_url)
                    sys.exit()
        except Exception as e:
            # 检查更新失败时也退出
            QMessageBox.critical(
                self,
                "错误",
                "无法连接到更新服务器，请检查网络连接后重试！"
            )
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('icon.ico')))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())