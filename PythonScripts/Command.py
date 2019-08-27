import os
myCMD = 'sudo openocd -f ~/openocd-code/tcl/interface/ftdi/olimex-arm-usb-ocd-h.cfg -f ~/openocd-code/rpi.cfg'
os.system(myCMD)