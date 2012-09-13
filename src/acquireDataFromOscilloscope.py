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
  # TODO : maybe insert delay?
  time.sleep(0.2)
  rawdata = scope.read(int(1e4))

  data = np.frombuffer(rawdata, 'B')
#  print "data" , data[10:15]
  # now we need to rescale the data
  yinc = float(scope.ask(":WAV:YINC?"))
  yoffset  = float(scope.ask(":WAV:YOR?"))
  
  print "Yinc : " , yinc
  print "Yoff px: ", yoffset / yinc + 100
  data = 100 - data  # centered at the origin, positive going up
  data = data * yinc + -yoffset #- yoffset
  print data[100:110]
  return data


def calculateTimeBase(datalength):
  """ Calculate the timebase for the oscilloscope """
  " We need three things: Start time, end time and number of points"
  n = datalength
  increment = float(scope.ask(":WAV:XINC?"))
  t0 = float(scope.ask(":WAV:XOR?"))
  t = t0 + increment*np.arange(n)
  return t


def updatePlot():
  """ Update the figure """
  #TODO : unchecked
  plot.clf()
  try :
  plot.plot(t,ch1)
  plot.plot(t,ch2)
  except :
    print "t, ch1 ", t1.size , ', ', ch1.size
    print "t, ch2 ", t2.size , ', ', ch2.size


  plot.title("Oscilloscope data")
  plot.ylabel("Voltage (V)")
  plot.ylabel("Voltage (V)")
  plot.xlabel("Time (s)")
  plot.draw()






  

if __name__ == '__main__':
  #TODO : rename RigolScope
  scope = instrument.RigolScope("/dev/usbtmc0")
  # initialize plot
  plot.ion()

  while True :
    print "Acquiring Measurement"
    performMeasurement()
    print "\n\nNew Measurement."
    print "Saving channel 1"
    ch1 = captureWaveForm(1)
    print "Saving channel 2"
    ch2 = captureWaveForm(2)
    print "Calculating X axis"
    t = calculateTimeBase(len(ch1))
   # print "Updating plot"
   # updatePlot(t,ch1,ch2)

# add ridiculous commeniiiiiAdd ridiculous commentt
