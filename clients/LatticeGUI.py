from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

class LATTICE_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(LATTICE_GUI, self).__init__(parent)
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.clients.connection import connection
        cxn = connection()
        yield cxn.connect()
        self.create_layout(cxn)
    
    def create_layout(self, cxn):
        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor)
        tableOpticsWidget = self.makeTableOpticsWidget(reactor, cxn)
        translationStageWidget = self.makeTranslationStageWidget(reactor)
        control729Widget =  self.makecontrol729Widget(reactor, cxn)
        centralWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        self.tabWidget.addTab(lightControlTab,'&LaserRoom')
        self.tabWidget.addTab(tableOpticsWidget,'&Optics')
        self.tabWidget.addTab(translationStageWidget,'&Translation Stages')
        self.tabWidget.addTab(control729Widget,'&Control 729')
        self.createGrapherTab()
        scriptControl = self.makeScriptControl(reactor)
        grid.addWidget(scriptControl, 0, 0, 1, 1)
        grid.addWidget(self.tabWidget, 0, 1, 1, 3)
        centralWidget.setLayout(grid)
        self.setCentralWidget(centralWidget)
    
    def makeScriptControl(self, reactor):
        from common.clients.guiscriptcontrol.scriptcontrol import ScriptControl
        self.sc = ScriptControl(reactor, self)
        self.sc, self.experimentParametersWidget = self.sc.getWidgets()
        self.createExperimentParametersTab()
        return self.sc
    
    @inlineCallbacks
    def createGrapherTab(self):
        grapher = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapher, '&Grapher')
    
    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def createExperimentParametersTab(self):
        self.tabWidget.addTab(self.experimentParametersWidget, '&Experiment Parameters')
    
    def makecontrol729Widget(self, reactor, cxn):
        from common.clients.control_729.control_729 import control_729
        widget = control_729(reactor, cxn)
        return widget
    
    def makeTranslationStageWidget(self, reactor):
        widget = QtGui.QWidget()
#        from common.clients.APTMotorClient import APTMotorClient
        gridLayout = QtGui.QGridLayout()
#        gridLayout.addWidget(APTMotorClient(reactor), 0, 0)
        widget.setLayout(gridLayout)
        return widget
    
    def makeLightWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.CAVITY_CONTROL import cavityWidget
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(cavityWidget(reactor),0,0)
        gridLayout.addWidget(multiplexerWidget(reactor),0,1)
        widget.setLayout(gridLayout)
        return widget
    
    def makeVoltageWidget(self, reactor):
        widget = QtGui.QWidget()
#        from TRAPDRIVE_CONTROL import TRAPDRIVE_CONTROL as trapDriveWidget
        from ENDCAP_CONTROL import ENDCAP_CONTROL as endcapWidget 
        from COMPENSATION_CONTROL import COMPENSATION_CONTROL as compensationWidget
#        from DCONRF_CONTROL import DCONRF_CONTROL as dconrfWidget
        #from TRAPDRIVE_MODULATION_CONTROL import TRAPDRIVE_MODULATION_CONTROL as trapModWidget
        #from COMPENSATION_LINESCAN import COMPENSATION_LINESCAN_CONTROL as compLineWidget
        from HV_CONTROL import hvWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(endcapWidget(reactor),0,0,1,2)
        gridLayout.addWidget(compensationWidget(reactor),1,0,1,2)
        #gridLayout.addWidget(compLineWidget(reactor),2,0)
        gridLayout.addWidget(hvWidget(reactor),2,1)
#        gridLayout.addWidget(trapDriveWidget(reactor),3,0)
#        gridLayout.addWidget(dconrfWidget(reactor),3,1)
        #gridLayout.addWidget(trapModWidget(reactor),4,0)
        widget.setLayout(gridLayout)
        return widget
    
    def makeTableOpticsWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.clients.PMT_CONTROL import pmtWidget
        from common.clients.SWITCH_CONTROL import switchWidget
        from common.clients.DDS_CONTROL import DDS_CONTROL#RS_CONTROL_LAB, RS_CONTROL_LOCAL, 
        #from doublePassWidget import doublePassWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(pmtWidget(reactor),0, 0, 1, 1, alignment = QtCore.Qt.AlignRight)
        gridLayout.addWidget(switchWidget(reactor, cxn),1,0, 1, 1)#, 1, 2)
        gridLayout.addWidget(DDS_CONTROL(reactor, cxn),2, 0, 1, 2)#, 1, 2)
#        gridLayout.addWidget(RS_CONTROL_LOCAL(reactor),2,0)
#        gridLayout.addWidget(RS_CONTROL_LAB(reactor),2,1)
        widget.setLayout(gridLayout)
        return widget

    def stopReactor(self, res):
        self.reactor.stop()
        
    def closeEvent(self, x):
        dl = Deferred()
        dl.addCallback(self.sc.exitProcedure)
        dl.addCallback(self.stopReactor)
        dl.callback(True)

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import common.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    latticeGUI = LATTICE_GUI(reactor)
    latticeGUI.setWindowTitle('Lattice GUI')
    latticeGUI.show()
    reactor.run()