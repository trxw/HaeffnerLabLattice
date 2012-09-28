from PyQt4 import QtGui
from scriptcontrol import ScriptControl
from twisted.internet.defer import inlineCallbacks

class ScriptControlWidgets():
    def __init__(self, reactor):
        self.makeScriptControl(reactor)
        
    @inlineCallbacks
    def makeScriptControl(self, reactor):
        sc = ScriptControl(reactor)
        ####MR2 not clear on how this works
        status, params = yield sc.getWidgets()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControlWidgets = ScriptControlWidgets(reactor)
    reactor.run()