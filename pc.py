from mcp1663LT import mcp1663LT
import time
from threading import Thread

""" Timeout function

https://dreamix.eu/blog/webothers/timeout-function-in-python-3 

"""

import signal
from contextlib import contextmanager


@contextmanager
def timeout(t):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(t)

    try:
        yield
    except TimeoutError:
        print(TimeoutError)
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError

""" End Timeout Function"""



device = mcp1663LT(path="0002:001c:02")

voltages = []
v = 0
inc = 0.5
while v < 5 + inc:
    voltages.append(v)
    v += inc
    v = round(v*10)/10


my_time = time.time()
print(f"{time.strftime('%D %H:%M:%S')}")

continueRunning = True

while True:
    for idx, v in enumerate(voltages):
        with timeout(10):
            for i in range(0,10):
                device.setVoltage(v)
                # device.getCurrentAndVoltage()
                # print(f"READING{i} \t target voltage{v:.2f} \t {device.vout} \t {device.voltage:.2f} \t {device.current:.2f}")
                time.sleep(0.005)
            my_time = time.time()
            if idx == 0: print(f"{time.strftime('%D %H:%M:%S')}", end="\r")
        # todo: if timeout.. figure something out to reinit dev

# myThread = Thread(target=run)
# myThread.daemon = True
# myThread.start()

list(map(lambda x: int(x,16), "0002:001c:02".split(":"))) # [2,28,2] --> [bus, dev, ?]

def toThreeDigits(x):
    while len(x) < 3:
        x = f"0{x}"
    return x

def getDeviceAddress(path):
    bus, dev, unk = list(map(toThreeDigits, list(map(lambda x: str(int(x,16)), path.split(":")))))
    return bus, dev

bus, dev = getDeviceAddress("0002:001c:02")

send_reset('/dev/bus/usb/%s/%s' % (bus, dev))


