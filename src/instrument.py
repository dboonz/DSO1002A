import os
# bla
class usbtmc:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR,int(1024*1024))

        # TODO: Test that the file opened

    def write(self, command):
        # check if any errors were found previously
        os.write(self.FILE, ":SYST:ERR?")
        if(int(os.read(self.FILE, 500)[0] ) != 0):
          print "Error before command %s", command
        # write the command
        os.write(self.FILE, command);

    def read(self, length = 4000):
        return os.read(self.FILE, length)

    def getName(self):
        self.write("*IDN?")
        return self.read(300)

    def sendReset(self):
        self.write("*RST")


class RigolScope:
    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device):
        self.meas = usbtmc(device)

        self.name = self.meas.getName()

        print self.name

    def write(self, command):
        """Send an arbitrary command directly to the scope"""
        self.meas.write(command)

    def read(self, command):
        """Read an arbitrary amount of data directly from the scope"""
        return self.meas.read(command)

    def reset(self):
        """Reset the instrument"""
        self.meas.sendReset()

    def ask(self,command):
        """ Ask a question, should be short"""
        self.write(command)
        return self.read(6000)

