import labrad
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure()
dv.cd(['','QuickMeasurements','Keithly 6487 Current Monitoring','2012Aug10'])
dv.open(39)
data = dv.get().asarray
### two current sources ###
thorlabs = data[0,7660]
ilx = data[76701:116194]

##normalize

thorlabs_i = thorlabs[:,1]-np.average(thorlabs[:,1])
ilx_i = ilx[:,1]-np.average(ilx[:,1])

pyplot.plot(thorlabs_i)
pyplot.plot(ilx_i)

pyplot.legend()
pyplot.xlabel( 'Time (s)')
pyplot.ylabel('Current')
pyplot.title('Current Sources')
pyplot.show()
