#!/usr/bin/python
import numpy
import matplotlib.pyplot as plot
from time import sleep
import instrument


""" Example program to plot the Y-T data from Channel 1"""

def startAndStopBlocking():
  " Start and stop the osciloscope in a blocking fashion"
  test.write(":RUN")
  # check if the oscilloscope is done
  while(True):
    test.write("*OPC?")
    if(int(test.read(100).strip()) == 0):
      sleep(0.01)
      print "Waiting another 100ms"
    else :
      print "Stopped waiting"
      break
    print "Continuing"

def getChannelData(channel):
    if (channel==1):
        channelName = "CHAN1"
    elif (channel==2):
        channelName = "CHAN2"
    else:
        print "Invalid channel!"
        return

    # Grab the data from channel 1
    #
    startAndStopBlocking()
    test.write(":WAV:POIN:MODE NORM")

    test.write(":WAV:DATA? " + channelName)
#    sleep(0.005)
    rawdata = test.read(9000)
    data = numpy.frombuffer(rawdata, 'B')

    # Get the voltage scale
    test.write(":" + channelName + ":SCAL?")
    voltscale = float(test.read(20))

    # And the voltage offset

    test.write(":" + channelName + ":OFFS?")
    voltoffset = float(test.read(20))

    # Walk through the data, and map it to actual voltages
    # First invert the data (ya rly)
    data = data * -1 + 255


    # Now, we know from experimentation that the scope display range is actually
    # 30-229.  So shift by 130 - the voltage offset in counts, then scale to
    # get the actual voltage.
    data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale

    # Get the timescale
    test.write(":TIM:SCAL?")
    timescale = float(test.read(20))

    # Get the timescale offset
    test.write(":TIM:OFFS?")
    timeoffset = float(test.read(20))

    # Now, generate a time axis.  The scope display range is 0-600, with 300 being
    # time zero.
    time = numpy.arange(-300.0/50*timescale, 300.0/50*timescale, timescale/50.0)

    # If we generated too many points due to overflow, crop the length of time.
    if (data.size > 600):
      data = data[0:600]
    if (time.size > data.size):
        time = time[0:600:1]


    # See if we should use a different time axis
#    if (time[599] < 1e-3):
#        time = time * 1e6
#        tUnit = "uS"
#    elif (time[599] < 1):
#        time = time * 1e3
#        tUnit = "mS"
#    else:
#        tUnit = "S"
    return [time, data]


# Initialize our scope
test = instrument.RigolScope("/dev/usbtmc0")

plot.ion()

while 1:
    t1, d1 = getChannelData(1)
    t2, d2 = getChannelData(2)

    # Start data acquisition again, and put the scope back in local mode
    test.write(":KEY:LOCK DIS")

    # Plot the data
    plot.clf()
    try :
      plot.plot(t1, d1)
      plot.plot(t2, d2)
    except : 
      print "ERROR PLOTTING"
      print "t1, d1 ", t1.size , ', ', d1.size
      print "t2, d2 ", t2.size , ', ', d2.size

    plot.title("Oscilloscope data")
    plot.ylabel("Voltage (V)")
    plot.xlabel("Time (s)")
    plot.xlim(t1[0], t1[599])
    plot.draw()
