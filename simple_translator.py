# -*- coding: utf-8 -*-

import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QComboBox, QLabel
)
from PyQt5.QtCore import Qt
import tencentcloud
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

class SimpleTranslator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_translator()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('简单翻译器')
        self.setGeometry(300, 300, 400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        
        # 创建控件
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("请输入要翻译的文本...")
        
        self.target_text = QTextEdit()
        self.target_text.setPlaceholderText("翻译结果...")
        self.target_text.setReadOnly(True)
        
        # 语言选择标签和下拉框
        source_label = QLabel("源语言:")
        self.source_lang_combo = QComboBox()
        
        target_label = QLabel("目标语言:")
        self.target_lang_combo = QComboBox()
        
        # 添加语言选项
        languages = {
            '自动检测': 'auto',
            '中文': 'zh',
            '英文': 'en',
            '日文': 'jp',
            '韩文': 'kr'
        }
        
        for lang_name, lang_code in languages.items():
            self.source_lang_combo.addItem(lang_name, lang_code)
            self.target_lang_combo.addItem(lang_name, lang_code)
            
        # 设置默认语言
        self.source_lang_combo.setCurrentIndex(0)  # 自动检测
        self.target_lang_combo.setCurrentIndex(1)  # 英文
        
        # 翻译按钮
        self.translate_btn = QPushButton('翻译')
        self.translate_btn.clicked.connect(self.translate_text)
        
        # 布局设置
        control_layout.addWidget(source_label)
        control_layout.addWidget(self.source_lang_combo)
        control_layout.addWidget(target_label)
        control_layout.addWidget(self.target_lang_combo)
        control_layout.addWidget(self.translate_btn)
        
        main_layout.addWidget(self.source_text)
        main_layout.addWidget(self.target_text)
        main_layout.addLayout(control_layout)
        
        central_widget.setLayout(main_layout)
        
    def init_translator(self):
        """初始化翻译器"""
        import os
        # 优先从环境变量获取，其次从同目录 config.json 读取
        self.SECRET_ID = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
        self.SECRET_KEY = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
        
        if not self.SECRET_ID or not self.SECRET_KEY:
            try:
                # 尝试读取本地配置文件
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        self.SECRET_ID = config_data.get("TENCENTCLOUD_SECRET_ID", "")
                        self.SECRET_KEY = config_data.get("TENCENTCLOUD_SECRET_KEY", "")
            except Exception:
                pass
                
        try:
            cred = credential.Credential(self.SECRET_ID, self.SECRET_KEY)
            
            # 实例化http选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"

            # 实例化client选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 实例化客户端
            self.client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)
        except Exception as e:
            self.target_text.setPlainText(f"初始化翻译器失败: {str(e)}")
            
    def translate_text(self):
        """执行翻译"""
        source_text = self.source_text.toPlainText().strip()
        if not source_text:
            self.target_text.setPlainText("请输入要翻译的文本")
            return
            
        try:
            # 获取源语言和目标语言
            source_lang = self.source_lang_combo.currentData()
            target_lang = self.target_lang_combo.currentData()
            
            # 实例化翻译请求对象
            req = models.TextTranslateRequest()
            params = {
                "SourceText": source_text,
                "Source": source_lang,
                "Target": target_lang,
                "ProjectId": 0
            }
            req.from_json_string(json.dumps(params))
            
            # 调用翻译接口
            resp = self.client.TextTranslate(req)
            self.target_text.setPlainText(resp.TargetText)
            
        except TencentCloudSDKException as err:
            self.target_text.setPlainText(f"接口调用失败：{err}")
        except Exception as e:
            self.target_text.setPlainText(f"未知错误：{str(e)}")

def main():
    app = QApplication(sys.argv)
    translator = SimpleTranslator()
    translator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()