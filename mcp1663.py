import hid, time

class mcp1663:
    voltage = -1
    current = -1
    isBusy = False
    overload = False
    targetVoltage = 2.5
    disable_high_voltage = 1
    is_off = True
    is_on = False

    def __init__(self, devNum=0, path=None, log=False, parent=None):
        """
        :param devNum: (int) Start from zero. The device number as inserted in usb order.
        :param path: (str or utf-8) USB path. When not None, supersedes devNum.
        :param log: bool Creates a log file voltage settings. Currently disabled.
        """
        self.dev = hid.device()
        devices = hid.enumerate(0x04D8, 0x00DD)
        if len(devices) != 0:
            if path is not None:
                if isinstance(path, str):
                    path = path.encode('utf-8')
                self.device_path = path.decode('utf-8')
                for d in devices:
                    if d["path"] == path:
                        self.dev.open_path(d["path"])
            else:
                self.dev.open_path(devices[devNum]["path"])
                self.device_path = devices[devNum]['path'].decode("utf-8")
            self.log = log
        else:
            raise Exception("No USB power supply device detected.")

    def _writeCommand(self, buf):
        self.dev.write([0x00] + buf + [0 for i in range(64 - len(buf))])
        read = self.dev.read(64)
        return read

    def _setGPIO(self, values=None, ioMode=None, designation=None):
        '''values represent the value output for the GPIOs'''

        ## SETUP DEFAULT VALUES
        if designation is None:
            designation = [0, 0, 0, 0]
        if ioMode is None:
            ioMode = [0, 0, 0, 0]
        if values is None:
            values = [0, 0, 0, 0]

        ## READ CURRENT SRAM SETTINGS
        readSRAM = [0x61]
        response = self._writeCommand(readSRAM)

        ## SET SRAM BASED ON READ SRAM SETTINGS
        setSRAM = [0x60]
        buf = setSRAM + [0] * 11
        buf[2] = response[5]  # Clock Output Divider value
        buf[3] = response[6]  # DAC Voltage Reference
        buf[4] = 0x00  # Set DAC output value
        buf[5] = 0x00  # ADC Voltage Reference
        # buf[6+1] = 0x00     #   Setup the interrupt detection mechanism and clear the detection flag
        buf[7] = 0x80  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80

        # SAFETY MEASURE TO PREVENT USB-POWER SUPPLY BURNOUT
        values[0] = 0

        buf[8] = values[0] << 4 | ioMode[0] << 3 | designation[0] << 1  ## VALUE ALWAYS ZERO
        buf[9] = values[1] << 4 | ioMode[1] << 3 | designation[1] << 1  ## RESISTANCE
        buf[10] = values[2] << 4 | ioMode[2] << 3 | designation[2] << 1  ## MCP2221
        buf[11] = values[3] << 4 | ioMode[3] << 3 | designation[3] << 1  ## LED

        self._writeCommand(buf)

    def disableHighVoltage(self):
        self.disable_high_voltage = 1

    def enableHighVoltage(self):
        self.disable_high_voltage = 0

    def close(self):
        if hasattr(self, 'dev'):
            self.dev.close()

    def i2cWrite(self, address, data):
        length = len(data)
        lowByteLength = length & 0x00FF
        highByteLength = length >> 8
        buf = [0x90, lowByteLength, highByteLength, address] + data
        response = self._writeCommand(buf)
        if response[1] == 1:
            print(f"{time.strftime('%D %H:%M:%S')}: i2c write busy")
            time.sleep(0.1)
            # self.i2cCancel()
            # response = self._writeCommand(buf)
        return response

    def i2cRead(self, address, length):
        lowByteLength = length & 0x00FF
        highByteLength = length >> 8

        ## Setup for reading
        buf = [0x91, lowByteLength, highByteLength, address]
        response = self._writeCommand(buf)
        if response[1] == 1:
            print(f"{time.strftime('%D %H:%M:%S')}: i2c read busy")
            time.sleep(0.1)
            # return
            # self.i2cCancel()
            # response = self._writeCommand(buf)

        ## i2cRead
        i2cRead = [0x40]
        response = self._writeCommand(i2cRead)
        return response[4:4 + length]

    def i2cCancel(self):
        setParameters = 0x10
        cancelCommand = 0x10
        buf = [setParameters, 0x00, cancelCommand]
        # response = self._writeCommand(buf)

    def getCurrentAndVoltage(self):
        ## CONFIGURE DEVICE FOR 80ms SAMPLING TIME
        self.i2cWrite(0x52, [0xB, 0x56])

        ## READ CURRENT
        self.i2cWrite(0x52, [0xD])
        current = self.i2cRead(0x53, 2)

        senseHigh = current[0]
        senseLow = current[1]
        senseHigh = senseHigh & 0x000000FF
        if (senseHigh & 0x80) == 0:  ## CHECK IF CURRENT IS POSITIVE (8th bit represents the sign)
            currentMeasured = 0.779 * ((senseHigh & 0x7F) * 16 + (senseLow / 16))
            if currentMeasured < 2:
                currentMeasured = 0
        else:  ## NEGATIVE CURRENT
            senseHigh = ~senseHigh & 0x000000FF  ## invert bits - more info inside the PAC1710 datasheet.
            senseLow = ~senseLow & 0x000000FF + 1  ## invert bits and add 1 - more info inside the PAC1710 datasheet.
            currentMeasured = -0.779 * ((senseHigh & 0x7F) * 16 + (senseLow / 16))
            if currentMeasured < -10:  ## eliminate bogus readings due to imperfect accuracy
                currentMeasured = 0

        self.current = currentMeasured

        ## READ VOLTAGE
        self.i2cWrite(0x52, [0x11])
        voltage = self.i2cRead(0x53, 2)

        vHi = voltage[0]
        vLo = voltage[1]
        voltageMeasured = 0.0391 * (4 * vHi + vLo / 64)

        self.voltage = voltageMeasured

        # if current measured is > 0.1 A and time elapsed is more than 500 ms, report overloading
        # if voltageMeasured > 0:
        #     if (self.targetVoltage/voltageMeasured > 0.89) & (time.time() - self.currentMeasureTime > 0.500):
        #         self.overload = True
        #         print('Overload')
        #     else:
        #         self.overload = False
        #         self.currentMeasureTime = time.time()

        # if self.log:
        #     arr = [[int(time.strftime('%H')), int(time.strftime('%M')), int(time.strftime('%S')), voltageMeasured,
        #             currentMeasured, int(self.overload)]]
        #     f = open(f"{time.strftime('mcp1663_log_%Y%m%d.csv')}", 'ab')
        #     np.savetxt(f, arr, delimiter=",", newline='\n', fmt='%.2f')
        #     f.close()

    # def getVoltage(self):
    #     self.getCurrentAndVoltage()
    #     return self.voltage

    # def getCurrent(self):
    #     self.getCurrentAndVoltage()
    #     return self.current

    def setVoltage(self, voltage: float = 2.5):
        self.getCurrentAndVoltage()
        self.targetVoltage = voltage
        RB1 = 3
        step = 0.195

        # See page 18 of MCP 1663 Booster user guide for more details
        if voltage < 2.5:
            voltage = 2.5
        elif voltage > 25:
            voltage = 25

        if self.disable_high_voltage and voltage > 13:
            voltage = 12.9

        if voltage < 13:
            bit1 = 1
            RT = 52
            # Feedback reference voltage 1.227 V
            RB_tot = RT * 1.227 / (voltage - 1.227)
            result = ((RB_tot - RB1) / step) + (11 / voltage)
        else:
            bit1 = 0
            RT = 470
            RB_tot = RT * 1.227 / (voltage - 1.227)
            result = ((RB_tot - RB1) / step) + (90 / voltage)
        vout = int(round(result))

        self.i2cWrite(0x5e, [0x02, vout])  # Wiper lock
        self.i2cWrite(0x5e, [0x0F, vout])  # Write protect
        self.i2cWrite(0x5e, [0x20, vout])  # Vout

        self._setGPIO([0, bit1, 1, 1])
        # Enable output
        self.getCurrentAndVoltage()
        # if self.voltage/self.targetVoltage > 0.89:
        #     time.sleep(0.5)
        # self.getCurrentAndVoltage()

    def turnOff(self):
        self.i2cWrite(0x52, [0, 0x20, 0])
        self._setGPIO([0, 0, 0, 0])
        self.getCurrentAndVoltage()
        self.is_off = True
        self.is_on = False

    def turnOn(self):
        self.setVoltage(2.5)
        self.getCurrentAndVoltage()
        self.is_off = False
        self.is_on = True




if __name__ == "__main__":
    import time
    import numpy as np
    # p1 = '\\\\?\\hid#vid_04d8&pid_00dd&mi_02#7&100c4b8a&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
    # p2 = '\\\\?\\hid#vid_04d8&pid_00dd&mi_02#7&2e17f400&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
    device = mcp1663()
    for i in np.arange(0,10,0.1):
        device.setVoltage(i)
        time.sleep(0.1)
        device.getCurrentAndVoltage()
        print(f"{i:.2f} \t {device.voltage:.2f} \t {device.current:.2f}")
    device.turnOff()
    # device.setVoltage(4.1)
    # device.setGPIO([0,0,0,0])
    # device.turnOff()