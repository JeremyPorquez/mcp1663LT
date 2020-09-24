import hid


# from PySide2 import QtCore

# mutex = QtCore.QMutex()
# def muteDecorator(func):
#     def mute(*args, **kwargs):
#         mutex.lock()
#         result = func(*args, **kwargs)
#         mutex.unlock()
#         return result
#     return mute

cdef class mcp1663LT:
    cdef float voltage
    cdef float current
    cdef bint isBusy
    cdef bint overload
    cdef float targetVoltage
    cdef bint disable_high_voltage
    cdef int vout



    def __init__(self, int devNum=0, str path=None, parent=None):
        """
        :param devNum: (int) Start from zero. The device number as inserted in usb order.
        :param path: (str or utf-8) USB path. When not None, supersedes devNum.
        :param log: bool Creates a log file voltage settings. Currently disabled.
        """
        self.voltage = -1
        self.current = -1
        self.isBusy = 0
        self.overload = 0
        self.targetVoltage = 0
        self.disable_high_voltage = 1
        self.vout = 0

        dev = hid.device()
        cdef list devices = hid.enumerate(0x04D8, 0x00DD)
        self.devices = devices
        # cdef list devices = hid.enumerate(0x04D8, 0x00DD)
        # if len(devices) != 0:
        #     if path is not None:
        #         if isinstance(path, str):
        #             path = path.encode('utf-8')
        #         self.device_path = path.decode('utf-8')
        #         for d in devices:
        #             if d["path"] == path:
        #                 self.dev.open_path(d["path"])
        #     else:
        #         self.dev.open_path(devices[devNum]["path"])
        #         self.device_path = devices[devNum]['path'].decode("utf-8")
        # else:
        #     raise Exception("No USB power supply device detected.")
    #
    # # @muteDecorator
    # def _writeCommand(self, buf):
    #     self.dev.write([0x00] + buf + [0 for i in range(64 - len(buf))])
    #     return self.dev.read(64)
    #
    # def _setGPIO(self, values=None, ioMode=None, designation=None):
    #     '''values represent the value output for the GPIOs'''
    #
    #     ## SETUP DEFAULT VALUES
    #     if designation is None:
    #         designation = [0, 0, 0, 0]
    #     if ioMode is None:
    #         ioMode = [0, 0, 0, 0]
    #     if values is None:
    #         values = [0, 0, 0, 0]
    #
    #     ## READ CURRENT SRAM SETTINGS
    #     readSRAM = [0x61]
    #     response = self._writeCommand(readSRAM)
    #
    #     ## SET SRAM BASED ON READ SRAM SETTINGS
    #     setSRAM = [0x60]
    #     buf = setSRAM + [0] * 11
    #     buf[2] = response[5]  # Clock Output Divider value
    #     buf[3] = response[6]  # DAC Voltage Reference
    #     buf[4] = 0x00  # Set DAC output value
    #     buf[5] = 0x00  # ADC Voltage Reference
    #     # buf[6+1] = 0x00     #   Setup the interrupt detection mechanism and clear the detection flag
    #     buf[7] = 0x80  # Alter GPIO configuration: alters the current GP designation
    #     #   datasheet says this should be 1, but should actually be 0x80
    #
    #     # SAFETY MEASURE TO PREVENT USB-POWER SUPPLY BURNOUT
    #     values[0] = 0
    #
    #     buf[8] = values[0] << 4 | ioMode[0] << 3 | designation[0] << 1  ## VALUE ALWAYS ZERO
    #     buf[9] = values[1] << 4 | ioMode[1] << 3 | designation[1] << 1  ## RESISTANCE
    #     buf[10] = values[2] << 4 | ioMode[2] << 3 | designation[2] << 1  ## MCP2221
    #     buf[11] = values[3] << 4 | ioMode[3] << 3 | designation[3] << 1  ## LED
    #
    #     self._writeCommand(buf)
    #
    # def disableHighVoltage(self):
    #     self.disable_high_voltage = 1
    #
    # def enableHighVoltage(self):
    #     self.disable_high_voltage = 0
    #
    # def close(self):
    #     if hasattr(self, 'dev'):
    #         self.dev.close()
    #
    # def i2cWrite(self, address, data):
    #     length = len(data)
    #     lowByteLength = length & 0x00FF
    #     highByteLength = length >> 8
    #     buf = [0x90, lowByteLength, highByteLength, address] + data
    #     response = self._writeCommand(buf)
    #     if response[1] == 1:
    #         self.i2cCancel()
    #         response = self._writeCommand(buf)
    #     return response
    #
    # def i2cRead(self, address, length):
    #     lowByteLength = length & 0x00FF
    #     highByteLength = length >> 8
    #
    #     ## Setup for reading
    #     buf = [0x91, lowByteLength, highByteLength, address]
    #     response = self._writeCommand(buf)
    #     while response[1] == 1:
    #         self.i2cCancel()
    #         response = self._writeCommand(buf)
    #
    #     ## i2cRead
    #     i2cRead = [0x40]
    #     response = self._writeCommand(i2cRead)
    #     return response[4:4 + length]
    #
    # def i2cCancel(self):
    #     setParameters = 0x10
    #     cancelCommand = 0x10
    #     buf = [setParameters, 0x00, cancelCommand]
    #     self._writeCommand(buf)
    #     response = self.dev.read(64)
    #
    # def getCurrentAndVoltage(self):
    #     ## CONFIGURE DEVICE FOR 80ms SAMPLING TIME
    #     self.i2cWrite(0x52, [0xB, 0x56])
    #
    #     ## READ CURRENT
    #     self.i2cWrite(0x52, [0xD])
    #     current = self.i2cRead(0x53, 2)
    #
    #     senseHigh = current[0]
    #     senseLow = current[1]
    #     senseHigh = senseHigh & 0x000000FF
    #     if (senseHigh & 0x80) == 0:  ## CHECK IF CURRENT IS POSITIVE (8th bit represents the sign)
    #         currentMeasured = 0.779 * ((senseHigh & 0x7F) * 16 + (senseLow / 16))
    #         if currentMeasured < 2:
    #             currentMeasured = 0
    #     else:  ## NEGATIVE CURRENT
    #         senseHigh = ~senseHigh & 0x000000FF  ## invert bits - more info inside the PAC1710 datasheet.
    #         senseLow = ~senseLow & 0x000000FF + 1  ## invert bits and add 1 - more info inside the PAC1710 datasheet.
    #         currentMeasured = -0.779 * ((senseHigh & 0x7F) * 16 + (senseLow / 16))
    #         if currentMeasured < -10:  ## eliminate bogus readings due to imperfect accuracy
    #             currentMeasured = 0
    #
    #     self.current = currentMeasured
    #
    #     ## READ VOLTAGE
    #     self.i2cWrite(0x52, [0x11])
    #     voltage = self.i2cRead(0x53, 2)
    #
    #     vHi = voltage[0]
    #     vLo = voltage[1]
    #     voltageMeasured = 0.0391 * (4 * vHi + vLo / 64)
    #
    #     self.voltage = voltageMeasured
    #
    # def setVoltage(self, voltage: float = 2.5):
    #     self.targetVoltage = voltage
    #
    #     # voltage to vout
    #     slope = 0.018875363
    #     intercept = -0.168207125
    #     bytes_out = int((voltage - intercept) / slope)
    #
    #     if bytes_out < 20:
    #         bytes_out = 0
    #     if bytes_out > 255:
    #         bytes_out = 255
    #
    #     self.i2cWrite(0x5e, [0x02, bytes_out])  # Wiper lock
    #     self.i2cWrite(0x5e, [0x0F, bytes_out])  # Write protect
    #     self.i2cWrite(0x5e, [0x20, bytes_out])  # Vout
    #
    #     self._setGPIO([0, 1, 1, 1])
    #     # Enable output
    #
    # def turnOff(self):
    #     self.setVoltage(0)
    #     self.i2cWrite(0x52, [0, 0x20, 0])
    #     self._setGPIO([0, 0, 0, 0])
    #
    # def turnOn(self):
    #     self.setVoltage(self.targetVoltage)


if __name__ == "__main__":
    import time
    import numpy as np
    pass

    # p1 = '\\\\?\\hid#vid_04d8&pid_00dd&mi_02#7&100c4b8a&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
    # p2 = '\\\\?\\hid#vid_04d8&pid_00dd&mi_02#7&2e17f400&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
    # device = mcp1663LT(path=p2)
    # device.setVoltage(7*5/64)
    # data = np.zeros((256,2))
    # while True:
    # for i, v in enumerate(np.arange(1/16,5,1/64)):
    #     device.setVoltage(v)
    #     print(i,v)
    #     input()
    # device.getCurrentAndVoltage()
    # device.getCurrentAndVoltage()
    # device.getCurrentAndVoltage()
    # data[i] = [device.vout, device.voltage]
    # print(f"{v:.2f} \t {device.vout} \t {device.voltage:.2f} \t {device.current:.2f}")

    # device.turnOff()
    # np.savetxt("LT.csv", data, delimiter=',', fmt="%s")
    # device.setVoltage(4.1)
    # device.setGPIO([0,0,0,0])
    # device.turnOff()
