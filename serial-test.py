import serial
import time

#
# ----------------------------------------------------------------------
# - SECTION - references
#
#  *  https://www.tutorialspoint.com/increment-and-decrement-operators-in-python
#
#  *  https://www.geeksforgeeks.org/print-without-newline-python/
#
#  *  https://www.askpython.com/python-modules/python-time-sleep-method 
#
#  *  https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.write
#
#  *  https://gist.github.com/yptheangel/fcd62ad59a569ace75eb07025b8e9c4f . . . serialPort.write(bytes.fromhex("a5"))
#
# ----------------------------------------------------------------------
#

# alternate baudrates tested:  115200 - b'\xff' responses
#                                9600 - no response at either delay 1uS, 100uS
#                               38400 - no response at 1uS
#

serialPort = serial.Serial(port = "/dev/ttyUSB0", baudrate=115200,
                           bytesize=serial.EIGHTBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE,
                           timeout=0, write_timeout=2.0)

        
serialString = ""                  # Used to hold data coming over UART

bootloader_handshake_attempts = 0  # bound loop iterations to finite value

HANDSHAKE_ATTEMPTS_TO_MAKE = 20     # . . . was 20

tries = 0


ONE_NANOSECOND           = 0.000000001
ONE_MICROSECOND          = 0.000001
TEN_MICROSECONDS         = 0.00001
ONE_HUNDRED_MICROSECONDS = 0.0001

#CHOSEN_DELAY = ONE_HUNDRED_MICROSECONDS
#CHOSEN_DELAY = TEN_MICROSECONDS
CHOSEN_DELAY = ONE_NANOSECOND



## STMicro ROM based bootloader expects an initial byte holding 0x7F
##  as a sign to commence firmware updating over a serial protocol:
print("Script starting,")
print("writing 0x7f to serial port . . .")
#serialPort.write(0x7f)
serialPort.write(bytes.fromhex("7f"))

#while ( serialPort.in_waiting == 0 ):
##    print(".", end=" ")
#    time.sleep(CHOSEN_DELAY)
#while ( 1 ):
while ( tries < 2^24 ):
    if(serialPort.in_waiting > 0):
        serialString = serialPort.read()
        print(serialString)
    tries += 1

print("\n")
#serialString = serialPort.readline()
#print(serialString)

tries = 0


print("At loop to attempt bootloader handshake several times:")
while ( bootloader_handshake_attempts < HANDSHAKE_ATTEMPTS_TO_MAKE ):
    bootloader_handshake_attempts += 1
    time.sleep(CHOSEN_DELAY)
    serialPort.write(bytes.fromhex("7f"))
    while ( serialPort.in_waiting == 0 ):
#        print(".", end=" ")
        time.sleep(CHOSEN_DELAY)
    serialString = serialPort.readline()
    print(serialString)


print("At original loop designed to read serial port received bytes:")
while(1):

    # Wait until there is data waiting in the serial buffer
    if(serialPort.in_waiting > 0):

        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()

        # Print the contents of the serial data
#        print(serialString.decode('Ascii'))
        print(serialString)


print("script done.")
