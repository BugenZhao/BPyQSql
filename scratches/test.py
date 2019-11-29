import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMacCocoaViewContainer, QApplication, QPushButton
import objc
from AppKit import *
import Foundation


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        frame = Foundation.NSMakeRect(0, 0, self.width(), self.height())
        view = objc.objc_object(c_void_p=self.winId().__int__())

        visualEffectView = NSVisualEffectView.new()
        visualEffectView.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        visualEffectView.setWantsLayer_(True)
        visualEffectView.setFrame_(frame)
        visualEffectView.setState_(NSVisualEffectStateActive)
        visualEffectView.setMaterial_(NSVisualEffectMaterialUltraDark)
        visualEffectView.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        visualEffectView.setWantsLayer_(True)

        self.setAttribute(Qt.WA_TranslucentBackground, True)

        window = view.window()
        content = window.contentView()

        container = QMacCocoaViewContainer(0, self)
        content.addSubview_positioned_relativeTo_(visualEffectView, NSWindowBelow, container)

        window.setTitlebarAppearsTransparent_(True)
        window.setStyleMask_(window.styleMask() | NSFullSizeContentViewWindowMask)

        # appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    sys.exit(app.exec_())
