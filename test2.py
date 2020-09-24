from mcp1663 import mcp1663
import time

voltages = []
v = 2.5
inc = 1
while v < 12.9 + inc:
    voltages.append(v)
    v += inc
    v = round(v*10)/10
    # input()
    # print(v)
    # dev.setVoltage(v)

device = mcp1663(devNum=0)
# device.dev.set_nonblocking(False)
print(f"{time.strftime('%D %H:%M:%S')}")
# while True:


while True:
    for idx, v in enumerate(voltages):
        for i in range(0,1):
            device.setVoltage(v)
            # device.getCurrentAndVoltage()
            # print(f"READING{i} \t target voltage{v:.2f} \t {device.voltage:.2f} \t {device.current:.2f}")
            # device.close()
            # time.sleep(0.001)
            # input()
        if idx == 0: print(f"{time.strftime('%D %H:%M:%S')}", end="\r")
