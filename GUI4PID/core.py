from time import sleep
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import serial
import threading

s = None
connected = False
try:
    s = serial.Serial('COM10', 38400, stopbits=serial.STOPBITS_TWO)
    connected = True
except Exception as err:
    print("Failed to connect to EVB5.1: {}".format(err))
read = True

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000, 600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

plot_power_supply = win.addPlot(title="POWER SUPPLY")
plot_rpm = win.addPlot(title="RPM")
curve = plot_rpm.plot(pen='r')
# data = np.random.normal(size=(110, 10000))
data = np.zeros(50)
data[49] = 100
ptr = 0

data0 = np.zeros(50)
data0[49] = 60
data1 = np.zeros(50)
data2 = np.zeros(50)
data_rpm = np.zeros(50)
data_rpm[49] = 60
data_target_rpm = np.zeros(50)
data_target_rpm[49] = 60
data5 = np.zeros(50)

rpm_curve = plot_power_supply.plot(pen='r', name='yellow')
rpm_curve.setData([13] * 50)
target_rpm_curve = plot_power_supply.plot(pen='g', name='yellow')
target_rpm_curve.setData([13] * 50)

# curve0 = plot_rpm.plot(pen='y', name='yellow')
# curve0.setData([1] * 50)
# curve1 = plot_rpm.plot(pen='r', name='yellow')
# curve1.setData([2] * 50)
curve_power_supply_voltage = plot_power_supply.plot(pen='b', name='yellow')
curve_power_supply_voltage.setData([3] * 50)
curve3 = plot_rpm.plot(pen='r', name='yellow')
curve3.setData([4] * 50)
curve4 = plot_rpm.plot(pen='g', name='yellow')
curve4.setData([5] * 50)
# curve5 = plot_rpm.plot(pen='b', name='yellow')
# curve5.setData([6] * 50)

decoding = 'utf-8'


def get_com_port_data():
    """get_com_port_data

    :return:
    """
    if not connected:
        return
    global data0, data1, data2, data_rpm, data_target_rpm, data5, decoding
    while read:
        sleep(.005)
        if s.in_waiting > 6:
            # print("Data buffer exceeded")
            s.read_all()
        elif s.in_waiting < 6:
            # print("Not enough data")
            pass
        else:
            # print("Fetching data..")
            sync_data = ord(s.read())
            if sync_data == 255:

                data5 = np.roll(data5, 1)
                data_target_rpm = np.roll(data_target_rpm, 1)
                data_rpm = np.roll(data_rpm, 1)
                data2 = np.roll(data2, 1)
                data1 = np.roll(data1, 1)
                data0 = np.roll(data0, 1)

                data5[-1] = sync_data
                data_target_rpm[-1] = ord(s.read())
                data_rpm[-1] = ord(s.read())
                data2[-1] = ord(s.read()) / 16
                data1[-1] = ord(s.read())
                data0[-1] = ord(s.read())


read_com_data_thread = threading.Thread(target=get_com_port_data)
read_com_data_thread.start()
# read_com_data_thread.join()


def update():
    global ptr

    curve_power_supply_voltage.setData(data2)
    rpm_curve.setData(data_rpm)
    target_rpm_curve.setData(data_target_rpm)
    curve3.setData(data_rpm)
    curve4.setData(data_target_rpm)
    # curve5.setData(data5)

    if ptr == 0:
        pass
        plot_rpm.enableAutoRange('xy', False)  # stop auto-scaling after the first data set is plotted
        plot_power_supply.enableAutoRange('xy', False)

    ptr += 1


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        read = False
        if connected:
            s.close()
