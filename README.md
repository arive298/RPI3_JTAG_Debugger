# RPI3_JTAG_Debugger
Tutorial on how to setup your Raspberry Pi 3 for Remote Debugging using a JTAG adapter and OpenOCD running on Ubuntu16.04

## 1)	Hardware used:
-Jtag Adapter: OLIMEX ARM-USB-OCD-H
-RaspberryPi3 model B with Raspbian Linux distro already installed
-Jumper wires and A-to-B-USB cable(Printer’s cable)
-PC with Linux Ubuntu installed
-UART usb cable(Optional)

## 2)	Wire connections between Raspberry Pi 3 and JTAG adapter:
![PIN Setup Guide](https://user-images.githubusercontent.com/32407701/63525134-2c2c0b80-c4cb-11e9-96f6-ecc47c8aff89.jpg)
Note: For TDI you can use GPIO 26 with ALT4 mode instead, but you would need to modify the code on the next step. Also, triple check wire connections

## 3)	Raspberry Pi Setup
Login into the raspberry pi and compile and run the JtagEnabler.cpp file. This file must be compile everytime you restart the RPI.
```
g++ -o JtagEnabler JtagEnabler.cpp
sudo ./JtagEnabler
```
### Optional
Modify the /etc/profile file so that the JtagEnabler runs automatically every boot up.
Open the profile file as root and add the command at the end that runs the JtagEnabler. 
```
sudo nano /etc/profile
```
Line to add at the end(Remember to add the correct path to the file):
```
sudo /<Path_To_JtagEnabler>/JtagEnabler
```

## 4)	Ubuntu Linux development station setup 
Update the machine and install the necessary tools 
```
cd ~
sudo apt-get update
sudo apt-get install libtool automake build-essential libtool pkg-config libusb-1.0.0-dev 
```
Download openocd and configure it for ftdi and the correct cable connection. In this case is ft2232.
```
git clone https://git.code.sf.net/p/openocd/code openocd
cd openocd
./bootstrap
./configure --enable-ftdi --enable-ft2232_ftd2xx 
```
Finally build it and install it.
```
make 
sudo make install 
```
Add raspberry Pi configuration file for openocd. This file is already provided in the repo.
```
gedit rpi3.cfg
```
Add the following contents
```
# Script from
# https://www.suse.com/c/debugging-raspberry-pi-3-with-jtag/
# with minor adaptions.

transport select jtag

# we need to enable srst even though we don't connect it
reset_config trst_and_srst

adapter_khz 1000
jtag_ntrst_delay 500

if { [info exists CHIPNAME] } {
  set _CHIPNAME $CHIPNAME
} else {
  set _CHIPNAME rpi3
}

#
# Main DAP
#
if { [info exists DAP_TAPID] } {
   set _DAP_TAPID $DAP_TAPID
} else {
   set _DAP_TAPID 0x4ba00477
}

jtag newtap $_CHIPNAME tap -irlen 4 -ircapture 0x1 -irmask 0xf -expected-id $_DAP_TAPID -enable
dap create $_CHIPNAME.dap -chain-position $_CHIPNAME.tap

set _TARGETNAME $_CHIPNAME.core
set _CTINAME $_CHIPNAME.cti

set DBGBASE {0x80010000 0x80012000 0x80014000 0x80016000}
set CTIBASE {0x80018000 0x80019000 0x8001a000 0x8001b000}
set _cores 4

for { set _core 0 } { $_core < $_cores } { incr _core } {

    cti create $_CTINAME.$_core -dap $_CHIPNAME.dap -ap-num 0 \
        -ctibase [lindex $CTIBASE $_core]

    target create $_TARGETNAME$_core aarch64 \
        -dap $_CHIPNAME.dap -coreid $_core \
        -dbgbase [lindex $DBGBASE $_core] -cti $_CTINAME.$_core

    $_TARGETNAME$_core configure -event reset-assert-post "aarch64 dbginit"
    $_TARGETNAME$_core configure -event gdb-attach { halt }
}
```
Install drivers for OLIMEX-ARM-USB-OCD-H JTAG adapter
```
sudo apt-get install libftdi-dev libftdi1
```
Create a file /etc/udev/rules.d/olimex-arm-usb-ocd-h.rules 
```
sudo gedit /etc/udev/rules.d/olimex-arm-usb-ocd-h.rules 
```
Put this single line in the file
```
SUBSYSTEM=="usb", ACTION=="add", ATTRS{idProduct}=="002b", ATTRS{idVendor}=="15ba", MODE="664", GROUP="plugdev"
```
## 5)	Run the system
Now that everything is setup, connect the usb cable from JTAG adapter to the Linux PC with the raspberry pi on and run the following command to start openocd:
```
sudo openocd -f ~/openocd/tcl/interface/ftdi/olimex-arm-usb-ocd-h.cfg -f ~/openocd/rpi3.cfg 
```
Now openocd is listening for a telnet connection on port 4444 or you can use GDB on port 3333.
•	For TELNET connection run the following command.(This is for running OpenOCD commands only)
```
telnet localhost 4444
```
•	For GDB run the following command:
```
gdb
target remote :3333
```


