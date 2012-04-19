from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from ctypes import c_long, c_buffer, c_float, windll, pointer

class APTMotor():
    def __init__(self):
        self.aptdll = windll.LoadLibrary("C:\\APTDLLClient\\APT.dll")
        #self.aptdll.EnableEventDlg(False)
        self.aptdll.APTInit()
        print 'APT initialized'
        self.HWType = c_long(31) # 31 means TDC001 controller
    
    def getNumberOfHardwareUnits(self):
        numUnits = c_long()
        self.aptdll.GetNumHWUnitsEx(self.HWType, pointer(numUnits))
        return numUnits.value
    
    def getSerialNumber(self, index):
        HWSerialNum = c_long()
        hardwareIndex = c_long(index)
        self.aptdll.GetHWSerialNumEx(self.HWType, hardwareIndex, pointer(HWSerialNum))
        return HWSerialNum.value

    def initializeHardwareDevice(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        self.aptdll.InitHWDevice(HWSerialNum)
        # need some kind of error reporting here
        return True
    
#    @inlineCallbacks
#    def initializeHardwareDevice(self, serialNumber):
#        print serialNumber
#        HWSerialNum = c_long(serialNumber)
#        yield self.aptdll.InitHWDevice(HWSerialNum)
#        # need some kind of error reporting here
#        returnValue( True )
#        
    def getHardwareInformation(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        model = c_buffer(255)
        softwareVersion = c_buffer(255)
        hardwareNotes = c_buffer(255)
        self.aptdll.GetHWInfo(HWSerialNum, model, 255, softwareVersion, 255, hardwareNotes, 255)      
        hwinfo = [model.value, softwareVersion.value, hardwareNotes.value]
        return hwinfo
    
    def getStageAxisInformation(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        minimumPosition = c_float()
        maximumPosition = c_float()
        units = c_long()
        pitch = c_float()
        self.aptdll.MOT_GetStageAxisInfo(HWSerialNum, pointer(minimumPosition), pointer(maximumPosition), pointer(units), pointer(pitch))
        stageAxisInformation = [minimumPosition.value, maximumPosition.value, units.value, pitch.value]
        return stageAxisInformation
    
#    def setStageAxisInformation(self, serialNumber, minimumPosition, maximumPosition):
#        HWSerialNum = c_long(serialNumber)
#        minimumPosition = c_float()
#        maximumPosition = c_float()
#        units = c_long(1) #since idk what these do
#        pitch = c_float(.5) #since idk what these do
#        self.aptdll.MOT_SetStageAxisInfo(HWSerialNum, minimumPosition, maximumPosition, units, pitch)
#        return True

    
#    def getHardwareLimitSwitches(self, serialNumber):
#        HWSerialNum = c_long(serialNumber)
#        reverseLimitSwitch = c_long()
#        forwardLimitSwitch = c_long()
#        self.aptdll.MOT_GetHWLimSwitches(HWSerialNum, pointer(reverseLimitSwitch), pointer(forwardLimitSwitch))
#        hardwareLimitSwitches = [reverseLimitSwitch.value, forwardLimitSwitch.value]
#        return hardwareLimitSwitches
    
    def getVelocityParameters(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        minimumVelocity = c_float()
        acceleration = c_float()
        maximumVelocity = c_float()
        self.aptdll.MOT_GetVelParams(HWSerialNum, pointer(minimumVelocity), pointer(acceleration), pointer(maximumVelocity))
        velocityParameters = [minimumVelocity.value, acceleration.value, maximumVelocity.value]
        return velocityParameters
    
    def setVelocityParameters(self, serialNumber, minVel, acc, maxVel):
        HWSerialNum = c_long(serialNumber)
        minimumVelocity = c_float(minVel)
        acceleration = c_float(acc)
        maximumVelocity = c_float(maxVel)
        self.aptdll.MOT_SetVelParams(HWSerialNum, minimumVelocity, acceleration, maximumVelocity)
        return True
    
    def getVelocityParameterLimits(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        maximumAcceleration = c_float()
        maximumVelocity = c_float()
        self.aptdll.MOT_GetVelParamLimits(HWSerialNum, pointer(maximumAcceleration), pointer(maximumVelocity))
        velocityParameterLimits = [maximumAcceleration.value, maximumVelocity.value]
        return velocityParameterLimits  

    def getPosition(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        position = c_float()
        self.aptdll.MOT_GetPosition(HWSerialNum, pointer(position))
        return position.value    

    def moveRelative(self, serialNumber, relDistance):
        HWSerialNum = c_long(serialNumber)
        relativeDistance = c_float(relDistance)
        self.aptdll.MOT_MoveRelativeEx(HWSerialNum, relativeDistance, True)
        return True

    def moveAbsolute(self, serialNumber, absPosition):
        HWSerialNum = c_long(serialNumber)
        absolutePosition = c_float(absPosition)
        self.aptdll.MOT_MoveAbsoluteEx(HWSerialNum, absolutePosition, True)
        return True

    def identify(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        self.aptdll.MOT_Identify(HWSerialNum)
        return True
        
    def cleanUpAPT(self):
        self.aptdll.APTCleanUp()
        print 'APT cleaned up'  

class APTMotorServer(LabradServer):
    """ Contains methods that interact with the APT motor controller """
    
    name = "APT Motor Server"
    
    onVelocityParameterChange = Signal(111111, 'signal: velocity parameter change', 'w')
    onPositionChange = Signal(222222, 'signal: position change', 'w')
    
    # Device Dictionary (Known Ahead of Time)
    
   
    def initServer(self):
        self.deviceDict = {'Axial FB': 83825962,
                       'Radial FB': 83825936,
                       'Radial LR': 83815664,
                       'Axial LR': 63001773,
                       'Auxilliary': 83816548,
                       'Simulator1': 83000001,
                       'Simulator2': 83000002,
                       'Simulator3': 83000003}
        
        # Make sure none of these devices have been initialized yet
        self.initializedDict = {}
        for i in self.deviceDict.keys():
            self.initializedDict[self.deviceDict[i]] = False

        from twisted.internet import reactor
        reactor.callLater(0, self.doPrepareDevices)        
#        self.prepareDevices()        
        self.listeners = set()    
    
    @inlineCallbacks
    def doPrepareDevices(self):
        yield deferToThread(self.prepareDevices)
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified

    def prepareDevices(self):
        self.aptMotor = APTMotor()        
        numberOfHardwareUnits = self.aptMotor.getNumberOfHardwareUnits()
        for i in range(numberOfHardwareUnits):
            serialNumber = self.aptMotor.getSerialNumber(i)
            if (serialNumber in self.deviceDict.values()):
                #ok = yield self.aptMotor.initializeHardwareDevice(serialNumber)
                ok = self.aptMotor.initializeHardwareDevice(serialNumber)
                if (ok == True):
                    self.initializedDict[serialNumber] = True
    
    @setting(0, "Get Available Devices", returns = '*s')
    def getAvailableDevices(self, c):
        """Returns a List of Initialized Devices"""
        availableHardwareUnits = []
        for i in self.deviceDict.keys():
            if (self.initializedDict[self.deviceDict[i]] == True):
                availableHardwareUnits.append(i)
        return availableHardwareUnits

    @setting(1, "Select Device", name = 's', returns = '')
    def selectDevice(self, c, name):
        if name not in self.deviceDict.keys(): raise Exception("No such Device")
        c['Device'] = self.deviceDict[name]

    @setting(2, "Get Serial Number", returns = 'w')
    def getSerialNumber(self, c):
        return c['Device']
#    @setting(1, "Initialize Hardware Device", serialNumber = 'w', returns ='b')
#    def initializeHardwareDevice(self, c, serialNumber):
#        """Initializes Hardware Device"""
#        ok = yield deferToThread(self.aptMotor.initializeHardwareDevice, serialNumber)
#        if (ok == True):
#            c['Hardware Initialized'] = True
#            returnValue(True)
#        else:
#            print 'false?'
#            returnValue(False)
    
    @setting(3, "Get Device Information",  returns ='*s')
    def getHardwareInformation(self, c):
        """Returns Hardware Information
            Model, Software Version, Hardware Notes"""
        if (self.initializedDict[c['Device']] == True):
            c['Hardware Information'] = yield deferToThread(self.aptMotor.getHardwareInformation, c['Device'])
            returnValue(c['Hardware Information'])


    @setting(4, "Get Velocity Parameters", returns ='*v')
    def getVelocityParameters(self, c):
        """Returns Velocity Parameters
            Minimum Velocity, Acceleration, Maximum Velocity"""
        if (self.initializedDict[c['Device']] == True):
            c['Velocity Parameters'] = yield deferToThread(self.aptMotor.getVelocityParameters, c['Device'])
            returnValue(c['Velocity Parameters'])

    @setting(5, "Get Velocity Parameter Limits", returns ='*v')
    def getVelocityParameterLimits(self, c):
        """Returns Velocity Parameter Limits
            Maximum Acceleration, Maximum Velocity"""
        if (self.initializedDict[c['Device']] == True):
            c['Velocity Parameter Limits'] = yield deferToThread(self.aptMotor.getVelocityParameterLimits, c['Device'])
            returnValue(c['Velocity Parameter Limits'])

    @setting(6, "Set Velocity Parameters", minimumVelocity = 'v', acceleration = 'v', maximumVelocity = 'v', returns ='b')
    def setVelocityParameters(self, c, minimumVelocity, acceleration, maximumVelocity):
        """Sets Velocity Parameters
            Minimum Velocity, Acceleration, Maximum Velocity"""
        if (self.initializedDict[c['Device']] == True):
            ok = yield deferToThread(self.aptMotor.setVelocityParameters, c['Device'], minimumVelocity, acceleration, maximumVelocity)
            notified = self.getOtherListeners(c)
            self.onVelocityParameterChange(c['Device'], notified)
            returnValue(True)

    @setting(7, "Get Position", returns ='v')
    def getPosition(self, c):
        """Returns Current Position"""
        if (self.initializedDict[c['Device']] == True):
            c['Current Position'] = yield deferToThread(self.aptMotor.getPosition, c['Device'])
            returnValue(c['Current Position'])
        
    @setting(8, "Move Relative", relativeDistance = 'v', returns ='b')
    def moveRelative(self, c, relativeDistance):
        """Moves the Motor by a Distance Relative to its Current Position"""
        if (self.initializedDict[c['Device']] == True):
            ok = yield deferToThread(self.aptMotor.moveRelative, c['Device'], relativeDistance)
            notified = self.getOtherListeners(c)
            self.onPositionChange(c['Device'], notified)
            returnValue(ok)    

    @setting(9, "Move Absolute", absolutePosition = 'v', returns ='b')
    def moveAbsolute(self, c, absolutePosition):
        """Moves the Motor an Absolute Position"""
        if (self.initializedDict[c['Device']] == True):
            ok = yield deferToThread(self.aptMotor.moveAbsolute, c['Device'], absolutePosition)
            notified = self.getOtherListeners(c)
            self.onPositionChange(c['Device'], notified)   
            returnValue(ok)    

    @setting(10, "Identify Device", returns ='b')
    def identifyDevice(self, c):
        """Identifies Device by Flashing Front Panel LED for a Few Seconds"""
        if (self.initializedDict[c['Device']] == True):
            ok = yield deferToThread(self.aptMotor.identify, c['Device'])
            returnValue(ok)
    
    @setting(11, "Get Stage Axis Information", returns='*v')
    def getStageAxisInformation(self, c):
        if (self.initializedDict[c['Device']] == True):
            c['Stage Axis Information'] = yield deferToThread(self.aptMotor.getStageAxisInformation, c['Device'])
            returnValue(c['Stage Axis Information'])

#    @setting(13, "Set Stage Axis Information", minimumPosition = 'v', maximumPosition = 'v', returns='b')
#    def setStageAxisInformation(self, c, minimumPosition, maximumPosition):
#        if (self.initializedDict[c['Device']] == True):
#            ok = yield deferToThread(self.aptMotor.setStageAxisInformation, c['Device'], minimumPosition, maximumPosition)
#            returnValue(True)
##    When attempting to set new limits, they both get set to 0!!
    


#    @setting(12, "Get Hardware Limit Switches", returns='*v')
#    def getHardwareLimitSwitches(self, c):
#        if (self.initializedDict[c['Device']] == True):
#            c['Hardware Limit Switches'] = yield deferToThread(self.aptMotor.getHardwareLimitSwitches, c['Device'])
#            returnValue(c['Hardware Limit Switches'])
##    Sample Output: [Value(2.0, None), Value(2.0, None)]
    
    def stopServer(self):  
        """Cleans up APT DLL before closing"""
        self.aptMotor.cleanUpAPT()
        
if __name__ == "__main__":
    from labrad import util
    util.runServer(APTMotorServer())