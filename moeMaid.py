#  coding: utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import sys
import random
sys.path.append('lib')
import aiml


class MaidWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MaidWindow, self).__init__(parent, Qt.WindowStaysOnTopHint)
 
        self.picNames = {}
        self.curPix = None
        self.curCloth = None
        self.dragPosition = None
        self.talk = False
        self.talkText = None
        self.talkRect = None
        self.timer = None
        self.aiKernel = None
        self.setAcceptDrops(True)
        self.setFixedSize(QSize(500, 500))
        self._initMaid()
  
    def mousePressEvent(self, event):
        '''midButton: close. rightButton: change act'''
        if event.button()==Qt.LeftButton:
            self.dragPosition = event.globalPos()-self.frameGeometry().topLeft()
            event.accept()
        if event.button() == Qt.RightButton:
            self._paintMaid()
            event.accept()
        if event.button() == Qt.MidButton:
            self.close()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        t = event.mimeData().text()
        t = unicode(t)
        respond = self.aiKernel.respond(t).decode('utf8')
        self._paintMaid(respond)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos()-self.dragPosition)
            event.accept()

    def paintEvent(self, event):
        if not self.curPix:
            self._changeAct()
        
        painter = QPainter(self)
        painter.drawPixmap(0 , 0, self.curPix)
        if self.talk:
            painter.drawText(QRectF(self.talkRect), self.talkText)
         
    def _initMaid(self):
        self._loadPic()
        self.talkRect = QRect()
        self.talkRect.setSize(QSize(150, 50))
        self.talk = False
        self.talkText = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._maidAutoChange)
        self.timer.start(1000)
        self.aiKernel = aiml.Kernel()
        self.aiKernel.loadSubs('subbers.ini')
        self.aiKernel.learn('cn-startup.xml')
        self.aiKernel.respond('load aiml cn')
        self._paintMaid()

    def _loadPic(self):
        '''load image resources'''
        pic_names = []
        for fname in os.listdir(os.path.join(u'resources', 'img')):
            if 'png' in fname:
                pic_names.append(fname)

        for name in pic_names:
            n = name.split('_')
            if not n[1] in self.picNames:
                self.picNames[n[1]] = []

            self.picNames[n[1]].append(name)
            pix = QPixmap(os.path.join('resources', 'img', name), '0', Qt.AvoidDither|Qt.ThresholdAlphaDither|Qt.ThresholdDither)
            QPixmapCache.insert(name, pix)

    def _maidAutoChange(self):
        '''auto change act or cloth every 15-30 sec'''
        t = random.randint(15, 30)
        if t % 4 == 0:
            self._changeCloth()
        self._paintMaid()
        self.timer.setInterval(t*1000)

    def _maskRegion(self, talk_text=None):
        '''mask region'''
        pix_region = QRegion(self.curPix.mask())
        pix_rect = pix_region.boundingRect()
        main_region = pix_region 
        talk_region = None
        if talk_text:
            self.talkRect.moveTopLeft(pix_rect.topRight())
            talk_region = QRegion(self.talkRect, QRegion.Rectangle)
            main_region = main_region + talk_region
            self.talkText = talk_text
            self.talk = True
        else:
            self.talk = False
        self.setMask(main_region)

    def _changeAct(self):
        '''change maid's act in same cloth. if curent cloth is None, self.curPix is pure random.'''
        if not self.curCloth:
            self.curCloth = random.choice(self.picNames.keys())
        pic_name = random.choice(self.picNames[self.curCloth])
        pix = QPixmapCache.find(pic_name)
        if not pix:
            pix = QPixmap(os.path.join('resources', 'img', pic_name), '0', Qt.AvoidDither|Qt.ThresholdAlphaDither|Qt.ThresholdDither)
            QPixmapCache.insert(pic_name, pix)
        self.curPix = pix

    def _changeCloth(self):
        '''change maid's cloth'''
        other_cloth = self.picNames.keys()[:]
        other_cloth.remove(self.curCloth)
        self.curCloth = random.choice(other_cloth)

    def _paintMaid(self, text=None):
        '''change act and paint'''
        self._changeAct()
        self._maskRegion(text)
        self.update()

    def _maidSay(self, text):
        '''not change act. just say'''
        if not self.curPix:
            self._changeAct()
        self._maskRegion(text)
        self.update()


       
app = QApplication(sys.argv)
maid = MaidWindow()
maid.show()
app.exec_()
