# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QLabel

def main():
    try:
        app = QApplication(sys.argv)
        label = QLabel('Hello PyQt5!')
        label.show()
        print("Application started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()