import numpy as np
import matplotlib.pyplot as plot
import time
import instrument

""" Capture data from a DSO1002A oscilloscope and plot it"""



def performMeasurement():

  # start running
  scope.write(":SINGLE")
  while(True):
    scope.write("*OPC?")
    ans = scope.read(100).strip()
#    print "\n\n   *OPC? :" , ans
    if(int(ans) == 0):
      time.sleep(0.05)
#      print "   Scope is still busy"
    else :
#      print "   Scope is done."
      break
#    print "   Continuing"


def captureWaveForm(channel):
  if (channel == 1):
    channelName = "CHAN1"
  elif (channel == 2):
    channelName = "CHAN2"
  else :
    #TODO : This should be in the driver
    raise BaseError("Invalid Channel!")
  scope.write("WAV:DATA? " + channelName)
  time.sleep(0.2)
  rawdata = scope.read(int(1e4))

  data = np.frombuffer(rawdata[10:610], 'B')
#  print "data" , data[10:15]
  # now we need to rescale the data
  yinc = float(scope.ask(":WAV:YINC?"))
  yor  = float(scope.ask(":WAV:YOR?"))
  yref = float(scope.ask(":WAV:YREF?"))
  props = {}
  props["inverted"] = int(scope.ask(channelName+":INV?"))
  props["yinc"] = yinc
  props["yor"] = yor
  props["yref"] = yref

  
  data = (yref - data) * yinc - yor  # see page 285 in manual
  print data[100:110]
  return data, props


def calculateTimeBase(datalength):
  """ Calculate the timebase for the oscilloscope """
  " We need three things: Start time, end time and number of points"
  n = datalength
  increment = float(scope.ask(":WAV:XINC?"))
  t0 = float(scope.ask(":WAV:XOR?"))
  t = t0 + increment*np.arange(n)
  return t


def updatePlot(t,ch1,ch2,props1=None,props2=None):
  """ Update the figure """
  plot.clf()
  ch1label = 'ch1'
  ch2label = 'ch2'
  if(props1 is not None):
    print "Props found"
    # check if the channel was inverted
    if(props1["inverted"] ):
      ch1label += ' (inverted)'
  if(props2 is not None):
    print "Props found"
    # check if the channel was inverted
    if(props2["inverted"] ):
      ch2label += ' (inverted)'
      
      
      
  try :
    
    plot.plot(t,ch1,label=ch1label)
    plot.plot(t,ch2,label='ch2')
  except :
    print "t, ch1 ", t.size , ', ', ch1.size
    print "t, ch2 ", t.size , ', ', ch2.size


  plot.title("Oscilloscope data")
  plot.ylabel("Voltage (V)")
  plot.ylabel("Voltage (V)")
  plot.xlabel("Time (s)")
  plot.legend()
  plot.draw()


def saveData(t,ch1,ch2):
  'saves the setup of the oscilloscope and the resulted frames'
  # first get all the settings of the oscilloscope
  scopesettings = scope.ask('*LRN?')
  fsettings = open('out.settings','wb')
  fsettings.write(scopesettings)
  fsettings.close()

  print scopesettings

  data = np.array([t,ch1,ch2]).transpose()
  np.savetxt('out.scope',data)

  





  

if __name__ == '__main__':
  #TODO : rename RigolScope
  scope = instrument.RigolScope("/dev/usbtmc0")
  # initialize with old settings DOES NOT WORK
#  scope.write(open('out.settings').readline())

  # initialize plot
  plot.ion()

  while True :
    print "Acquiring Measurement"
    performMeasurement()
    print "\n\nNew Measurement."
    print "Saving channel 1"
    ch1, props1 = captureWaveForm(1)
    print "Props" 
    print props1
    print "Saving channel 2"
    ch2, props2 = captureWaveForm(2)

    # print some statistics for debugging
    t = calculateTimeBase(len(ch1))
    print "Updating plot"
    updatePlot(t,ch1,ch2,props1,props2)
    # save the data
    saveData(t,ch1,ch2)

