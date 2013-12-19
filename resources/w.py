from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import random

class ShapeWidget(QWidget):
    def __init__(self,parent=None):
        super(ShapeWidget,self).__init__(parent)
 
        self.pixs = [QPixmap("test/moe%s.png" % (str(i)),"0",Qt.AvoidDither|Qt.ThresholdDither|Qt.ThresholdAlphaDither) for i in range(5)]
        self.picIdx = 0
        self.resize(self.pixs[self.picIdx].size())
        self.setMask(self.pixs[self.picIdx].mask())
        self.dragPosition=None
  
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self.dragPosition=event.globalPos()-self.frameGeometry().topLeft()
            event.accept()
        if event.button()==Qt.RightButton:
            self.picIdx = random.choice(range(5))
            self.repaint()
        if event.button() == Qt.MidButton:
            self.close()


    def mouseMoveEvent(self,event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos()-self.dragPosition)
            event.accept()

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.drawPixmap(0,0,self.pixs[self.picIdx])
        
app=QApplication(sys.argv)
form=ShapeWidget()
form.show()
app.exec_()
