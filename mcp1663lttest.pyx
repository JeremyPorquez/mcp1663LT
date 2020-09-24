from mcp1663LT import mcp1663LT
import time

cdef str path = "0001:0017:02"
# "0001:000c:02"

print(path)

cdef float inc = 0.5
cdef int data_points = int((5/inc) + 1)
cdef float voltages[5]

cdef float v = 0
cdef int idx = 0
cdef int jdx = 0
print(data_points)
for idx in range(data_points):
    voltages[idx] = v
    print(voltages[idx])
    v += inc
    v = round(v*10)/10

print(f"{time.strftime('%D %H:%M:%S')}")
while True:
    for idx in range(data_points):
        for jdx in range(3):
#         print(f"{voltages[0]}")

            device.setVoltage(v)
        # device.getCurrentAndVoltage()
        # print(f"READING{i} \t target voltage{v:.2f} \t {device.vout} \t {device.voltage:.2f} \t {device.current:.2f}")
            device.close()
            time.sleep(0.005)
        if idx == 0: print(f"{time.strftime('%D %H:%M:%S')}", end="\r")


# cython3 -3 mcp1663lttest.pyx --embed
# gcc mcp1663lttest.c `python3-config --cflags --ldflags` -fPIC -o mcp1663lt