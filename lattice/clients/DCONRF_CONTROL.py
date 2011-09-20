from PyQt4 import QtGui, QtCore, uic
from twisted.internet.defer import inlineCallbacks
import os

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class DCONRF_CONTROL(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        self.reactor = reactor
        super(DCONRF_CONTROL, self).__init__(parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/dconrf.ui')
        uic.loadUi(path,self)
        self.connect()
   
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.dc_box
    	#connect functions
        value = yield self.server.getdcoffsetrf()
        self.doubleSpinBox.setValue(value)
        self.justUpdated = False
        self.doubleSpinBox.valueChanged.connect(self.onNewValue)
        #start timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    def onNewValue(self):
        self.justUpdated = True
    
    @inlineCallbacks
    def sendToServer(self):
        if(self.justUpdated):
            value = self.doubleSpinBox.value()
            yield self.server.setdcoffsetrf(value)
            self.justUpdated = False
    
    def closeEvent(self, x):
        self.reactor.stop()
             
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DCONRF_CONTROL = DCONRF_CONTROL(reactor)
    DCONRF_CONTROL.show()
    reactor.run()