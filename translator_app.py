# -*- coding: utf-8 -*-

import sys
import os
import json
import winreg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QComboBox, QCheckBox, QSystemTrayIcon, 
    QMenu, QAction, QMessageBox, QStyle, QDesktopWidget, QDialog, 
    QLabel, QDialogButtonBox, QLineEdit, QFormLayout
)
from PyQt5.QtCore import Qt, QPoint, QSettings, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QIcon, QTextCursor

# 自定义文本编辑框，用于处理快捷键
class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
    
    def keyPressEvent(self, event):
        # 检查是否按下了Shift+空格
        if event.key() == Qt.Key_Space and event.modifiers() & Qt.ShiftModifier:
            if self.main_window:
                self.main_window.translate_text()
            return  # 不调用父类方法，防止输入空格
        # 检查是否按下了Shift+Esc
        elif event.key() == Qt.Key_Escape and event.modifiers() & Qt.ShiftModifier:
            if self.main_window:
                self.main_window.hide_window()
            return  # 不调用父类方法，防止其他处理
        else:
            # 其他按键正常处理
            super().keyPressEvent(event)

# 设置对话框
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('设置')
        self.setFixedSize(420, 360)
        
        layout = QVBoxLayout()
        
        # 1. 开机自启复选框
        self.autostart_checkbox = QCheckBox('开机自启')
        self.autostart_checkbox.setChecked(self.is_auto_start_enabled())
        layout.addWidget(self.autostart_checkbox)
        
        # 2. 密钥配置表单
        form_layout = QFormLayout()
        
        self.secret_id_input = QLineEdit()
        self.secret_id_input.setPlaceholderText("请输入腾讯云 Secret ID")
        if self.parent and hasattr(self.parent, 'SECRET_ID'):
            self.secret_id_input.setText(self.parent.SECRET_ID)
            
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("请输入腾讯云 Secret Key")
        if self.parent and hasattr(self.parent, 'SECRET_KEY'):
            self.secret_key_input.setText(self.parent.SECRET_KEY)
            
        form_layout.addRow("Secret ID:", self.secret_id_input)
        form_layout.addRow("Secret Key:", self.secret_key_input)
        layout.addLayout(form_layout)
        
        # 3. 密钥获取提示信息
        hint_label = QLabel()
        hint_label.setWordWrap(True)
        hint_label.setTextFormat(Qt.RichText)
        hint_label.setOpenExternalLinks(True)
        hint_label.setText(
            "<div style='color: #555555; font-size: 12px; line-height: 1.5;'>"
            "<b>如何获取密钥：</b><br>"
            "1. 登录腾讯云控制台，前往 <a href='https://console.cloud.tencent.com/cam/capi'>API密钥管理</a> 页面申请并创建密钥。<br>"
            "2. 如果您没有密钥，可以直接联系 "
            "<b>田长金（<a href='mailto:473272738@qq.com'>473272738@qq.com</a>）</b> 索取测试密钥。"
            "</div>"
        )
        layout.addWidget(hint_label)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def is_auto_start_enabled(self):
        """检查是否已设置开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "TranslatorApp")
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False
        
    def set_auto_start(self, enable):
        """设置开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            if enable:
                # 获取当前exe路径
                exe_path = sys.executable
                winreg.SetValueEx(key, "TranslatorApp", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "TranslatorApp")
                except WindowsError:
                    pass  # 值不存在
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False
        
    def accept(self):
        # 1. 尝试保存开机自启设置
        autostart_enabled = self.autostart_checkbox.isChecked()
        autostart_success = self.set_auto_start(autostart_enabled)
        
        # 2. 保存密钥到 QSettings
        secret_id = self.secret_id_input.text().strip()
        secret_key = self.secret_key_input.text().strip()
        
        if self.parent:
            self.parent.settings.setValue("TENCENTCLOUD_SECRET_ID", secret_id)
            self.parent.settings.setValue("TENCENTCLOUD_SECRET_KEY", secret_key)
            
            # 3. 尝试写入同目录的 config.json (作为备份)
            try:
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
                config_data = {}
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                config_data["TENCENTCLOUD_SECRET_ID"] = secret_id
                config_data["TENCENTCLOUD_SECRET_KEY"] = secret_key
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=4)
            except Exception:
                pass
                
        if not autostart_success:
            QMessageBox.warning(self, "警告", "设置已保存，但修改开机自启失败，请检查系统权限。")
            
        super().accept()
import tencentcloud
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化配置
        self.settings = QSettings('TranslatorApp', 'Settings')
        self.init_ui()
        self.init_translator()
        self.init_tray_icon()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('翻译器')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 置顶
        # 窗口默认支持调整大小
        
        # 设置窗口大小
        self.resize(300, 200)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)  # 减少布局间距
        control_layout = QHBoxLayout()
        
        # 创建控件
        self.source_text = CustomTextEdit(self)
        self.source_text.setPlaceholderText("请输入要翻译的文本... (Shift+空格翻译, Shift+Esc最小化)")
        
        self.target_text = CustomTextEdit(self)
        self.target_text.setPlaceholderText("翻译结果...")
        self.target_text.setReadOnly(True)
        
        # 语言选择下拉框
        self.source_lang_combo = QComboBox()
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
        self.target_lang_combo.setCurrentIndex(2)  # 英文（修改索引为2，因为"英文"在列表中是第3个元素，索引从0开始）
        
        # 复制按钮
        self.copy_btn = QPushButton('复制')
        self.copy_btn.clicked.connect(self.copy_result)
        
        # 翻译按钮
        self.translate_btn = QPushButton('翻译')
        self.translate_btn.clicked.connect(self.translate_text)
        
        # 添加快捷键提示
        self.translate_btn.setShortcut("Shift+Space")
        
        # 置顶复选框
        self.stay_top_checkbox = QCheckBox('窗口置顶')
        self.stay_top_checkbox.setChecked(True)
        self.stay_top_checkbox.stateChanged.connect(self.toggle_stay_top)
        
        # 控制按钮
        self.minimize_btn = QPushButton('最小化')
        self.minimize_btn.clicked.connect(self.hide_window)
        
        self.close_btn = QPushButton('关闭')
        self.close_btn.clicked.connect(self.close_window)
        
        # 布局设置
        control_layout.addWidget(self.source_lang_combo)
        control_layout.addWidget(self.target_lang_combo)
        control_layout.addWidget(self.translate_btn)
        control_layout.addWidget(self.copy_btn)
        control_layout.addWidget(self.stay_top_checkbox)
        control_layout.addWidget(self.minimize_btn)
        control_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.source_text)
        main_layout.addWidget(self.target_text)
        main_layout.addLayout(control_layout)
        
        central_widget.setLayout(main_layout)
        
        # 启用拖拽移动窗口
        self.drag_position = None
        
    def init_translator(self):
        """初始化翻译器"""
        self.client = None
        
        # 1. 优先从 QSettings 读取
        self.SECRET_ID = self.settings.value("TENCENTCLOUD_SECRET_ID", "")
        self.SECRET_KEY = self.settings.value("TENCENTCLOUD_SECRET_KEY", "")
        
        # 2. 其次从环境变量获取
        if not self.SECRET_ID or not self.SECRET_KEY:
            self.SECRET_ID = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
            self.SECRET_KEY = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
        
        # 3. 最后从同目录 config.json 读取
        if not self.SECRET_ID or not self.SECRET_KEY:
            try:
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        self.SECRET_ID = config_data.get("TENCENTCLOUD_SECRET_ID", "")
                        self.SECRET_KEY = config_data.get("TENCENTCLOUD_SECRET_KEY", "")
            except Exception:
                pass
                
        # 4. 如果仍未检测到密钥，引导用户去设置
        if not self.SECRET_ID or not self.SECRET_KEY:
            reply = QMessageBox.information(
                self, 
                "配置提示", 
                "未检测到腾讯云 API 密钥。\n\n"
                "本软件翻译功能依赖腾讯云服务。您可以：\n"
                "1. 前往腾讯云控制台「API密钥管理」申请并创建密钥。\n"
                "2. 直接联系田长金（473272738@qq.com）索取测试密钥。\n\n"
                "是否现在打开「设置」配置密钥？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                QTimer.singleShot(100, self.open_settings)
            return
            
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
            QMessageBox.critical(self, "错误", f"初始化翻译器失败: {str(e)}")
            
    def init_tray_icon(self):
        """初始化系统托盘图标"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            # 如果系统托盘不可用，不显示警告，因为这在某些系统上是正常的
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        # 使用应用程序默认图标
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        
    def translate_text(self):
        """执行翻译"""
        source_text = self.source_text.toPlainText().strip()
        if not source_text:
            QMessageBox.warning(self, "警告", "请输入要翻译的文本")
            return
            
        if not hasattr(self, 'client') or self.client is None:
            QMessageBox.warning(self, "配置提示", "请先在「设置」中配置腾讯云 API 密钥。")
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
            QMessageBox.critical(self, "翻译失败", f"接口调用失败：{err}")
        except Exception as e:
            QMessageBox.critical(self, "翻译失败", f"未知错误：{str(e)}")
            
    def copy_result(self):
        """复制翻译结果到剪贴板"""
        result_text = self.target_text.toPlainText()
        if result_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(result_text)
            # 改变按钮文字为"复制成功"，1秒后恢复
            self.copy_btn.setText("复制成功")
            QTimer.singleShot(1000, lambda: self.copy_btn.setText("复制"))
        else:
            # 如果没有内容可复制，也给出提示
            self.copy_btn.setText("无内容")
            QTimer.singleShot(1000, lambda: self.copy_btn.setText("复制"))
            
    def toggle_stay_top(self, state):
        """切换窗口置顶状态"""
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
    def hide_window(self):
        """隐藏窗口"""
        self.hide()
        
    def show_window(self):
        """显示窗口"""
        self.show()
        self.activateWindow()
        
    def close_window(self):
        """关闭窗口（最小化到托盘）"""
        self.hide()
        
    def exit_app(self):
        """退出应用程序"""
        self.save_settings()
        QApplication.quit()
        
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.init_translator()
            if self.client:
                QMessageBox.information(self, "提示", "设置已保存，翻译服务初始化成功！")
            else:
                QMessageBox.warning(self, "提示", "设置已保存，但检测到密钥为空或初始化失败。")
        
    def on_tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.Trigger:
            self.show_window()
            
    def load_settings(self):
        """加载设置"""
        # 加载窗口位置
        pos = self.settings.value("window_position", None)
        if pos:
            self.move(pos)
        else:
            # 默认位置设在右下角
            self.move_to_bottom_right()
            
    def showEvent(self, event):
        """重写showEvent确保窗口在右下角显示"""
        super().showEvent(event)
        # 只在第一次显示时调整位置
        if not hasattr(self, '_positioned'):
            self.move_to_bottom_right()
            self._positioned = True
            
    def save_settings(self):
        """保存设置"""
        # 保存窗口位置
        self.settings.setValue("window_position", self.pos())
        
    def move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        # 获取主屏幕的几何信息
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
        else:
            # 兼容性处理
            screen_geometry = QApplication.desktop().availableGeometry()
            
        # 确保窗口大小已正确设置
        self.adjustSize()
        window_geometry = self.geometry()
        
        # 计算窗口位置，确保不超出屏幕边界
        x = max(0, min(screen_geometry.width() - window_geometry.width(), 
                      screen_geometry.width() - window_geometry.width() - 20))
        y = max(0, min(screen_geometry.height() - window_geometry.height(), 
                      screen_geometry.height() - window_geometry.height() - 60))
        
        self.move(x, y)
        
    # 鼠标事件用于拖拽窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def keyPressEvent(self, event):
        # 检查是否按下了Shift+空格
        if event.key() == Qt.Key_Space and event.modifiers() & Qt.ShiftModifier:
            self.translate_text()
            return  # 事件已处理，不传递给其他处理器
        # 检查是否按下了Shift+Esc
        elif event.key() == Qt.Key_Escape and event.modifiers() & Qt.ShiftModifier:
            self.hide_window()
            return  # 事件已处理，不传递给其他处理器
        super().keyPressEvent(event)
            
    def keyReleaseEvent(self, event):
        # 不需要特殊处理Shift+Z的释放事件
        super().keyReleaseEvent(event)
            
    def closeEvent(self, event):
        """重写关闭事件，使窗口关闭时最小化到托盘而不是退出"""
        event.ignore()
        self.hide()

def main():
    # 确保只有一个实例在运行
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("翻译器")
    app.setApplicationDisplayName("翻译器")
    
    try:
        translator = TranslatorApp()
        translator.show()
        print("Translator app started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting translator app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()