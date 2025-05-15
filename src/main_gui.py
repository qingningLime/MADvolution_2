import sys
import warnings
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                            QDialog, QListWidget, QMessageBox, QTabWidget,
                            QTextEdit, QProgressBar, QSlider, QGroupBox,
                            QGridLayout, QFormLayout, QComboBox, QSpinBox,
                            QLineEdit)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont, QIcon

# 忽略sip兼容性警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 窗口设置
        self.setWindowTitle("MADvolution 视频处理工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.clicked.connect(self.open_settings)
        
        # 主控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = QLabel("MADvolution 视频处理套件")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Normal))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #1C1C1E;
                padding-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # 功能按钮
        self.create_button("依赖安装工具", layout)
        self.create_button("音乐分析工具", layout)
        self.create_button("视频批量分析工具", layout)
        self.create_button("AI剪辑脚本生成", layout)
        self.create_button("视频剪辑工具", layout)
        self.create_button("缓存清理", layout)
        
        # 设置按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF;
                color: white;
                border: none;
                padding: 16px 32px;
                font-size: 16px;
                border-radius: 10px;
                min-width: 240px;
                min-height: 56px;
            }
        """)
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 底部信息
        footer = QLabel("版本 2.0 | © 2025 MADvolution_剪辑进化")
        footer.setFont(QFont("Microsoft YaHei", 10))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                color: #8E8E93;
                padding-top: 10px;
            }
        """)
        layout.addWidget(footer)
        
        # 应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F7;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 16px 32px;
                font-size: 16px;
                border-radius: 10px;
                min-width: 240px;
                min-height: 56px;
            }
            QPushButton:hover {
                background-color: #0069D9;
            }
            QPushButton:pressed {
                padding: 17px 33px;
                font-size: 15px;
            }
            QLabel {
                color: #1C1C1E;
                font-size: 16px;
            }
        """)
    
    def create_button(self, text, layout):
        btn = QPushButton(text)
        btn.setFont(QFont("Microsoft YaHei", 16, QFont.Normal))
        btn.setMinimumSize(240, 56)
        btn.clicked.connect(lambda: self.on_button_click(text))
        layout.addWidget(btn)
    
    def open_settings(self):
        """打开模型配置对话框"""
        dialog = self.SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 保存配置到config.json
            if dialog.save_config():
                QMessageBox.information(self, "成功", "配置已保存")
            else:
                QMessageBox.warning(self, "错误", "保存配置失败")

    class SettingsDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("⚙️ 模型配置")
            self.setFixedSize(700, 800)
            self.setStyleSheet("""
                QDialog {
                    background-color: #F5F5F7;
                    border-radius: 12px;
                }
                QTabWidget::pane {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 12px;
                    margin-top: 8px;
                }
                QTabBar::tab {
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 14px;
                    min-width: 120px;
                }
                QTabBar::tab:selected {
                    background-color: #007AFF;
                    color: white;
                }
                QGroupBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 16px;
                    margin-top: 16px;
                    font-size: 14px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px;
                }
                QLineEdit, QComboBox {
                    padding: 8px;
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    font-size: 14px;
                    min-height: 36px;
                }
            """)

            # 主布局
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)
            self.setLayout(main_layout)

            # 标题
            title = QLabel("模型配置")
            title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
            title.setStyleSheet("color: #1C1C1E;")
            main_layout.addWidget(title)

            # 选项卡
            tabs = QTabWidget()
            main_layout.addWidget(tabs)

            # Ollama配置页
            ollama_tab = QWidget()
            ollama_layout = QVBoxLayout(ollama_tab)
            ollama_layout.setContentsMargins(16, 16, 16, 16)
            ollama_layout.setSpacing(24)
            
            # 服务器配置组
            server_group = QGroupBox("服务器配置")
            server_layout = QFormLayout()
            server_layout.setVerticalSpacing(16)
            server_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
            server_group.setLayout(server_layout)
            
            self.ollama_url = QLineEdit("http://localhost:11434")
            self.ollama_url.setPlaceholderText("输入Ollama服务地址 (如: http://localhost:11434)")
            server_layout.addRow("服务地址:", self.ollama_url)
            
            # 模型配置组
            model_group = QGroupBox("模型配置")
            model_layout = QFormLayout()
            model_layout.setVerticalSpacing(16)
            model_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
            model_group.setLayout(model_layout)
            
            self.ollama_model = QComboBox()
            self.ollama_model.addItems(["minicpm-v", "llama3", "mistral"])
            model_layout.addRow("多模态模型:", self.ollama_model)
            
            self.embedding_model = QComboBox()
            self.embedding_model.addItems(["shaw/dmeta-embedding-zh", "bge-small", "bge-large"])
            model_layout.addRow("Embedding模型:", self.embedding_model)
            
            ollama_layout.addWidget(server_group)
            ollama_layout.addWidget(model_group)
            ollama_layout.addStretch()
            
            tabs.addTab(ollama_tab, "🖥️ 本地模型")

            # 云端API配置页
            cloud_tab = QWidget()
            cloud_layout = QVBoxLayout(cloud_tab)
            cloud_layout.setContentsMargins(16, 16, 16, 16)
            cloud_layout.setSpacing(24)
            
            # API配置组
            api_group = QGroupBox("API配置")
            api_layout = QFormLayout()
            api_layout.setVerticalSpacing(16)
            api_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
            api_group.setLayout(api_layout)
            
            self.api_url = QLineEdit("https://api.deepseek.com")
            self.api_url.setPlaceholderText("输入API服务地址 (如: https://api.deepseek.com)")
            api_layout.addRow("服务地址:", self.api_url)
            
            self.api_key = QLineEdit()
            self.api_key.setPlaceholderText("输入您的API密钥")
            self.api_key.setEchoMode(QLineEdit.Password)
            api_layout.addRow("API密钥:", self.api_key)
            
            # 模型配置组
            model_group = QGroupBox("模型配置")
            model_layout = QFormLayout()
            model_layout.setVerticalSpacing(16)
            model_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
            model_group.setLayout(model_layout)
            
            self.cloud_model = QComboBox()
            self.cloud_model.addItems(["deepseek-chat", "gpt-4", "claude-3"])
            model_layout.addRow("模型选择:", self.cloud_model)
            
            cloud_layout.addWidget(api_group)
            cloud_layout.addWidget(model_group)
            cloud_layout.addStretch()
            
            tabs.addTab(cloud_tab, "☁️ 云端API")

            # 按钮区域
            btn_group = QWidget()
            btn_layout = QHBoxLayout(btn_group)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(16)
            
            cancel_btn = QPushButton("取消")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: #1C1C1E;
                    padding: 12px 24px;
                    font-size: 14px;
                    border-radius: 8px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #D1D1D6;
                }
            """)
            cancel_btn.clicked.connect(self.reject)
            btn_layout.addWidget(cancel_btn)
            
            save_btn = QPushButton("💾 保存配置")
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    padding: 12px 24px;
                    font-size: 14px;
                    border-radius: 8px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #0069D9;
                }
            """)
            save_btn.clicked.connect(self.accept)
            btn_layout.addWidget(save_btn)
            
            main_layout.addWidget(btn_group)

            # 加载当前配置
            self.load_config()

        def load_config(self):
            """从config.json加载当前配置"""
            import json
            try:
                with open("src/config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.ollama_url.setText(config.get("ollama", {}).get("base_url", ""))
                    self.ollama_model.setCurrentText(config.get("model_name", ""))
                    self.embedding_model.setCurrentText(config.get("ollama", {}).get("embedding_model", ""))
                    self.api_url.setText(config.get("ai_auto_processor", {}).get("base_url", ""))
                    self.api_key.setText(config.get("ai_auto_processor", {}).get("api_key", ""))
                    self.cloud_model.setCurrentText(config.get("ai_auto_processor", {}).get("model", ""))
            except Exception as e:
                print(f"加载配置失败: {e}")

        def save_config(self):
            """保存当前配置到文件"""
            import json
            try:
                # 读取当前配置
                with open("src/config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 只更新需要修改的字段
                ollama_config = config.setdefault("ollama", {})
                ollama_config["embedding_model"] = self.embedding_model.currentText()
                ollama_config["base_url"] = self.ollama_url.text()
                
                config["model_name"] = self.ollama_model.currentText()
                
                ai_config = config.setdefault("ai_auto_processor", {})
                ai_config["api_key"] = self.api_key.text()
                ai_config["base_url"] = self.api_url.text()
                ai_config["model"] = self.cloud_model.currentText()
                
                # 写入文件
                with open("src/config.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"保存配置失败: {e}")
                return False

    def on_button_click(self, text):
        try:
            if text == "依赖安装工具":
                import subprocess
                subprocess.Popen(["python", "src/install_deps.py"])
            elif text == "音乐分析工具":
                from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                                          QPushButton, QListWidget, QMessageBox)
                from PyQt5.QtCore import Qt
                
                from PyQt5.QtWidgets import QHBoxLayout  # 确保导入
                class DragDropDialog(QDialog):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.setWindowTitle("文件导入")
                        self.setFixedSize(600, 450)
                        
                        layout = QVBoxLayout()
                        self.setLayout(layout)
                        
                        # 拖拽区域
                        self.drop_area = QLabel("拖拽文件到此处\n(实验性功能，目前无法使用)")
                        self.drop_area.setAlignment(Qt.AlignCenter)
                        self.drop_area.setStyleSheet("""
                            QLabel {
                                border: 2px dashed #aaa;
                                border-radius: 15px;
                                padding: 40px;
                                font-size: 18px;
                                margin: 20px;
                                color: #555;
                            }
                            QLabel:hover {
                                border-color: #4CAF50;
                                background-color: #f8f8f8;
                            }
                        """)
                        self.drop_area.setAcceptDrops(True)
                        # 启用拖拽功能
                        self.drop_area.setAttribute(Qt.WA_AcceptTouchEvents, True)
                        self.drop_area.setAttribute(Qt.WA_AcceptDrops, True)
                        layout.addWidget(self.drop_area)
                        
                        # 文件列表
                        self.file_list = QListWidget()
                        self.file_list.setStyleSheet("""
                            QListWidget {
                                font-size: 16px;
                                padding: 10px;
                            }
                        """)
                        layout.addWidget(self.file_list)
                        
                        # 操作按钮
                        btn_layout = QHBoxLayout()
                        add_btn = QPushButton("＋ 添加更多文件")
                        add_btn.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 12px 24px;
                                background-color: #2196F3;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #0b7dda;
                            }
                        """)
                        add_btn.clicked.connect(self.add_files)
                        btn_layout.addWidget(add_btn)
                        
                        confirm_btn = QPushButton("🔍 开始分析")
                        confirm_btn.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 12px 24px;
                                background-color: #4CAF50;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #45a049;
                            }
                        """)
                        confirm_btn.clicked.connect(self.accept)
                        btn_layout.addWidget(confirm_btn)
                        
                        layout.addLayout(btn_layout)
                        
                        self.files = []
                    
                    def dragEnterEvent(self, event):
                        if event.mimeData().hasUrls():
                            # 接受所有URL拖拽，在drop时再过滤
                            event.acceptProposedAction()
                        else:
                            event.ignore()
                    
                    def dropEvent(self, event):
                        if event.mimeData().hasUrls():
                            for url in event.mimeData().urls():
                                file_path = url.toLocalFile()
                                if True:  # 接受所有文件类型
                                    if file_path not in self.files:
                                        self.files.append(file_path)
                                        self.file_list.addItem(file_path.split('/')[-1])
                            event.acceptProposedAction()
                            return
                        event.ignore()
                    
                    def add_files(self):
                        from PyQt5.QtWidgets import QFileDialog
                        files, _ = QFileDialog.getOpenFileNames(
                            self,
                            "选择文件",
                            "",
                            "所有文件 (*.*)"
                        )
                        for file in files:
                            if file not in self.files:
                                self.files.append(file)
                                self.file_list.addItem(file.split('/')[-1])
                
                dialog = DragDropDialog(self)
                if dialog.exec_() == QDialog.Accepted and dialog.files:
                    import os
                    import shutil
                    os.makedirs("input/music_input", exist_ok=True)
                    for file in dialog.files:
                        try:
                            shutil.copy(file, "input/music_input")
                        except Exception as e:
                            QMessageBox.warning(self, "错误", f"无法拷贝文件 {file}:\n{str(e)}")
                            return
                    import subprocess
                    import os
                    import shutil
                    process = subprocess.Popen(["python", "src/music_analyzer(音乐分析工具).py"])
                    # 等待程序完成
                    process.wait()
                    if process.returncode == 0:
                        # 清空输入目录
                        music_input_dir = "input/music_input"
                        for filename in os.listdir(music_input_dir):
                            file_path = os.path.join(music_input_dir, filename)
                            try:
                                if os.path.isfile(file_path):
                                    os.unlink(file_path)
                                elif os.path.isdir(file_path):
                                    shutil.rmtree(file_path)
                            except Exception as e:
                                print(f"删除文件失败: {file_path}, 错误: {e}")
                        
                        from PyQt5.QtWidgets import QMessageBox
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setWindowTitle("操作成功")
                        msg.setText("🎉 音乐分析完成！")
                        msg.setInformativeText(f"文件已处理并保存到output_Music目录\n已自动清理{music_input_dir}目录")
                        msg.setStyleSheet("""
                            QMessageBox {
                                background-color: #f5f5f5;
                                font-family: Microsoft YaHei;
                            }
                            QLabel {
                                font-size: 14px;
                            }
                        """)
                        msg.exec_()
            elif text == "AI剪辑脚本生成":
                from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                                          QPushButton, QListWidget, QMessageBox,
                                          QTabWidget, QWidget, QTextEdit,
                                          QProgressBar, QSlider, QHBoxLayout)
                from PyQt5.QtCore import Qt, QProcess

                class AIScriptDialog(QDialog):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.setWindowTitle("AI剪辑脚本生成")
                        self.setFixedSize(800, 600)
                        self.setStyleSheet("""
                            QDialog {
                                background-color: #F5F5F7;
                                border-radius: 12px;
                            }
                        """)
                        
                        # 主布局
                        main_layout = QVBoxLayout()
                        main_layout.setContentsMargins(24, 24, 24, 24)
                        main_layout.setSpacing(24)
                        self.setLayout(main_layout)
                        
                        # 标题
                        title = QLabel("AI剪辑脚本生成器")
                        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
                        title.setStyleSheet("color: #1C1C1E;")
                        main_layout.addWidget(title)
                        
                        # 输入区域
                        input_group = QGroupBox("剪辑需求")
                        input_group.setStyleSheet("""
                            QGroupBox {
                                border: 1px solid #E0E0E0;
                                border-radius: 8px;
                                padding: 16px;
                                margin-top: 16px;
                            }
                            QGroupBox::title {
                                subcontrol-origin: margin;
                                left: 8px;
                                padding: 0 4px;
                            }
                        """)
                        input_layout = QVBoxLayout(input_group)
                        
                        self.input_edit = QTextEdit()
                        self.input_edit.setPlaceholderText("请详细描述您的剪辑需求，包括视频风格、节奏、转场效果等...")
                        self.input_edit.setStyleSheet("""
                            QTextEdit {
                                border: 1px solid #E0E0E0;
                                border-radius: 6px;
                                padding: 12px;
                                font-size: 14px;
                                min-height: 200px;
                                background-color: white;
                            }
                        """)
                        input_layout.addWidget(self.input_edit)
                        main_layout.addWidget(input_group)
                        
                        # 按钮区域
                        btn_group = QWidget()
                        btn_layout = QHBoxLayout(btn_group)
                        btn_layout.setContentsMargins(0, 0, 0, 0)
                        btn_layout.setSpacing(16)
                        
                        # 生成脚本按钮
                        run_btn = QPushButton("✨ 生成脚本")
                        run_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #007AFF;
                                color: white;
                                padding: 12px 24px;
                                font-size: 14px;
                                border-radius: 8px;
                                min-width: 120px;
                            }
                            QPushButton:hover {
                                background-color: #0069D9;
                            }
                        """)
                        run_btn.clicked.connect(self.run_script)
                        btn_layout.addWidget(run_btn)
                        
                        # 打开文档按钮
                        docs_btn = QPushButton("📂 打开文档")
                        docs_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #34C759;
                                color: white;
                                padding: 12px 24px;
                                font-size: 14px;
                                border-radius: 8px;
                                min-width: 120px;
                            }
                            QPushButton:hover {
                                background-color: #2DB24A;
                            }
                        """)
                        docs_btn.clicked.connect(self.open_docs)
                        btn_layout.addWidget(docs_btn)
                        
                        # 编辑脚本按钮
                        edit_btn = QPushButton("✏️ 编辑脚本")
                        edit_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #AF52DE;
                                color: white;
                                padding: 12px 24px;
                                font-size: 14px;
                                border-radius: 8px;
                                min-width: 120px;
                            }
                            QPushButton:hover {
                                background-color: #9B45C7;
                            }
                        """)
                        edit_btn.clicked.connect(self.edit_script)
                        btn_layout.addWidget(edit_btn)
                        
                        main_layout.addWidget(btn_group)
                        
                        # 状态区域
                        status_group = QGroupBox("状态")
                        status_group.setStyleSheet("""
                            QGroupBox {
                                border: 1px solid #E0E0E0;
                                border-radius: 8px;
                                padding: 16px;
                            }
                        """)
                        status_layout = QVBoxLayout(status_group)
                        
                        self.status_label = QLabel("就绪")
                        self.status_label.setAlignment(Qt.AlignCenter)
                        self.status_label.setStyleSheet("""
                            QLabel {
                                font-size: 14px;
                                color: #8E8E93;
                            }
                        """)
                        status_layout.addWidget(self.status_label)
                        
                        self.progress_bar = QProgressBar()
                        self.progress_bar.setRange(0, 100)
                        self.progress_bar.setTextVisible(False)
                        self.progress_bar.setStyleSheet("""
                            QProgressBar {
                                height: 6px;
                                border-radius: 3px;
                                background-color: #E0E0E0;
                            }
                            QProgressBar::chunk {
                                background-color: #007AFF;
                                border-radius: 3px;
                            }
                        """)
                        status_layout.addWidget(self.progress_bar)
                        
                        main_layout.addWidget(status_group)
                    
                    def run_script(self):
                        """运行脚本生成器"""
                        user_input = self.input_edit.toPlainText()
                        if not user_input:
                            QMessageBox.warning(self, "警告", "请输入剪辑需求")
                            return
                            
                        self.status_label.setText("正在生成脚本...")
                        
                        try:
                            import subprocess
                            import os
                            
                            # 检查分析数据目录
                            analysis_dir = "ai分析数据"
                            if not os.path.exists(analysis_dir) or not os.listdir(analysis_dir):
                                QMessageBox.warning(self, "警告", "ai分析数据目录不存在或为空")
                                return
                            
                            # 运行脚本生成器
                            process = subprocess.Popen(
                                ["python", "src/mad_script_generator(ai生成剪辑脚本).py"],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            
                            # 传递用户输入
                            process.communicate(input=user_input + "\nq\n")
                            
                            if process.returncode == 0:
                                self.status_label.setText("脚本生成成功！")
                                QMessageBox.information(self, "完成", "AI剪辑脚本生成完成！")
                            else:
                                self.status_label.setText("生成失败")
                                QMessageBox.warning(self, "错误", "脚本生成过程中出现错误")
                        except Exception as e:
                            self.status_label.setText("发生错误")
                            QMessageBox.critical(self, "错误", f"运行脚本时出错:\n{str(e)}")
                    
                    def open_docs(self):
                        """打开分析文档文件夹"""
                        try:
                            import os
                            import subprocess
                            
                            # 同时打开两个文件夹
                            subprocess.Popen(f'explorer "ai分析数据"')
                            subprocess.Popen(f'explorer "mad剪辑提示词"')
                            
                            self.status_label.setText("已打开分析文档")
                        except Exception as e:
                            self.status_label.setText("打开失败")
                            QMessageBox.warning(self, "错误", f"无法打开文件夹:\n{str(e)}")
                    
                    def edit_script(self):
                        """编辑生成的脚本文件"""
                        try:
                            import os
                            import subprocess
                            
                            script_path = "ai剪辑脚本/mad_script.md"
                            if not os.path.exists(script_path):
                                QMessageBox.warning(self, "警告", "脚本文件不存在，请先生成脚本")
                                return
                                
                            subprocess.Popen(['notepad', script_path])
                            self.status_label.setText("正在编辑脚本")
                        except Exception as e:
                            self.status_label.setText("编辑失败")
                            QMessageBox.warning(self, "错误", f"无法打开脚本文件:\n{str(e)}")
                
                dialog = AIScriptDialog(self)
                dialog.exec_()
            elif text == "视频剪辑工具":
                import subprocess
                process = subprocess.Popen(["python", "src/auto_cut_video(视频切割).py"])
                process.wait()
                if process.returncode == 0:
                    from PyQt5.QtWidgets import QMessageBox
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("操作成功") 
                    msg.setText("✂️ 视频剪辑完成！")
                    msg.setInformativeText("剪辑后的视频已保存到output目录")
                    msg.setStyleSheet("""
                        QMessageBox {
                            background-color: #f5f5f5;
                            font-family: Microsoft YaHei;
                        }
                        QLabel {
                            font-size: 14px;
                        }
                    """)
                    msg.exec_()
            elif text == "视频批量分析工具":
                from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                                          QPushButton, QListWidget, QMessageBox,
                                          QTabWidget, QWidget)
                from PyQt5.QtCore import Qt

                class VideoBatchDialog(QDialog):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.setWindowTitle("批量视频处理")
                        self.setFixedSize(600, 450)
                        
                        layout = QVBoxLayout()
                        self.setLayout(layout)
                        
                        # 创建选项卡
                        tabs = QTabWidget()
                        layout.addWidget(tabs)
                        
                        # 视频选项卡
                        video_tab = QWidget()
                        video_layout = QVBoxLayout(video_tab)
                        
                        video_label = QLabel("视频文件 (将保存到input/视频批处理/视频)")
                        video_layout.addWidget(video_label)
                        
                        self.video_list = QListWidget()
                        self.video_list.setStyleSheet("""
                            QListWidget {
                                font-size: 16px;
                                padding: 10px;
                            }
                        """)
                        video_layout.addWidget(self.video_list)
                        
                        add_video_btn = QPushButton("＋ 添加视频文件")
                        add_video_btn.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 12px 24px;
                                background-color: #2196F3;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #0b7dda;
                            }
                        """)
                        add_video_btn.clicked.connect(self.add_videos)
                        video_layout.addWidget(add_video_btn)
                        
                        tabs.addTab(video_tab, "视频文件")
                        
                        # 字幕选项卡
                        subtitle_tab = QWidget()
                        subtitle_layout = QVBoxLayout(subtitle_tab)
                        
                        subtitle_label = QLabel("字幕文件 (将保存到input/视频批处理/字幕)")
                        subtitle_layout.addWidget(subtitle_label)
                        
                        self.subtitle_list = QListWidget()
                        self.subtitle_list.setStyleSheet("""
                            QListWidget {
                                font-size: 16px;
                                padding: 10px;
                            }
                        """)
                        subtitle_layout.addWidget(self.subtitle_list)
                        
                        add_subtitle_btn = QPushButton("＋ 添加字幕文件")
                        add_subtitle_btn.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 12px 24px;
                                background-color: #4CAF50;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #45a049;
                            }
                        """)
                        add_subtitle_btn.clicked.connect(self.add_subtitles)
                        subtitle_layout.addWidget(add_subtitle_btn)
                        
                        tabs.addTab(subtitle_tab, "字幕文件")
                        
                        # 确认按钮
                        confirm_btn = QPushButton("🔍 开始批量处理")
                        confirm_btn.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 12px 24px;
                                background-color: #FF9800;
                                color: white;
                                border-radius: 6px;
                            }
                            QPushButton:hover {
                                background-color: #e68a00;
                            }
                        """)
                        confirm_btn.clicked.connect(self.accept)
                        layout.addWidget(confirm_btn)
                        
                        self.video_files = []
                        self.subtitle_files = []
                    
                    def add_videos(self):
                        from PyQt5.QtWidgets import QFileDialog
                        files, _ = QFileDialog.getOpenFileNames(
                            self,
                            "选择视频文件",
                            "",
                            "视频文件 (*.mp4 *.avi *.mov *.mkv)"
                        )
                        for file in files:
                            if file not in self.video_files:
                                self.video_files.append(file)
                                self.video_list.addItem(file.split('/')[-1])
                    
                    def add_subtitles(self):
                        from PyQt5.QtWidgets import QFileDialog
                        files, _ = QFileDialog.getOpenFileNames(
                            self,
                            "选择字幕文件",
                            "",
                            "字幕文件 (*.srt *.ass *.lrc)"
                        )
                        for file in files:
                            if file not in self.subtitle_files:
                                self.subtitle_files.append(file)
                                self.subtitle_list.addItem(file.split('/')[-1])
                
                dialog = VideoBatchDialog(self)
                if dialog.exec_() == QDialog.Accepted:
                    import os
                    import shutil
                    
                    # 处理视频文件
                    video_dir = "input/视频批处理/视频"
                    os.makedirs(video_dir, exist_ok=True)
                    for file in dialog.video_files:
                        try:
                            shutil.copy(file, video_dir)
                        except Exception as e:
                            QMessageBox.warning(self, "错误", f"无法拷贝视频文件 {file}:\n{str(e)}")
                            return
                    
                    # 处理字幕文件
                    subtitle_dir = "input/视频批处理/字幕"
                    os.makedirs(subtitle_dir, exist_ok=True)
                    for file in dialog.subtitle_files:
                        try:
                            shutil.copy(file, subtitle_dir)
                        except Exception as e:
                            QMessageBox.warning(self, "错误", f"无法拷贝字幕文件 {file}:\n{str(e)}")
                            return
                    
                    # 运行批量处理程序
                    import subprocess
                    process = subprocess.Popen(["python", "src/batch_video_processor(批量处理视频内容).py"])
                    process.wait()
                    if process.returncode == 0:
                        from PyQt5.QtWidgets import QMessageBox
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setWindowTitle("操作成功")
                        msg.setText("📹 批量处理完成！")
                        msg.setInformativeText("所有视频已处理完成并保存到output目录")
                        msg.setStyleSheet("""
                            QMessageBox {
                                background-color: #f5f5f5;
                                font-family: Microsoft YaHei;
                            }
                            QLabel {
                                font-size: 14px;
                            }
                        """)
                        msg.exec_()
            elif text == "缓存清理":
                import subprocess
                process = subprocess.Popen(["python", "src/clear_cache缓存清理工具.py"])
                process.wait()
                if process.returncode == 0:
                    from PyQt5.QtWidgets import QMessageBox
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("操作成功")
                    msg.setText("🧹 缓存清理完成！")
                    msg.setInformativeText("所有缓存文件已成功清理")
                    msg.setStyleSheet("""
                        QMessageBox {
                            background-color: #f5f5f5;
                            font-family: Microsoft YaHei;
                        }
                        QLabel {
                            font-size: 14px;
                        }
                    """)
                    msg.exec_()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"无法启动 {text}:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
