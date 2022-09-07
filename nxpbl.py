import serial
import time

# from defines.bootloader_nxp_tags import function_as_placeholder
#import bootloader_nxp_defines
#from bootloader_nxp_tags import NXP_RESPONSE_TAG__*
from defines.bootloader_nxp_tags import *



#
# ----------------------------------------------------------------------
#
# - SECTION - references
#
#  (1)  https://www.tutorialspoint.com/increment-and-decrement-operators-in-python
#
#  (2)  https://www.geeksforgeeks.org/print-without-newline-python/
#
#  (3)  https://www.askpython.com/python-modules/python-time-sleep-method 
#
#  (4)  https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.write
#
#  (5)  https://gist.github.com/yptheangel/fcd62ad59a569ace75eb07025b8e9c4f . . . serialPort.write(bytes.fromhex("a5"))
#
#  (6)  https://jimmywongiot.com/2021/03/13/byte-manipulation-on-python-platform/
#
#  Note STM32WL55 flash memory start mapped to 0x08000000, per document:
#  (7)  rm0453-stm32wl5x-advanced-armbased-32bit-mcus-with-subghz-radio-solution-stmicroelectronics.pdf
#
#
# 2022-09-07
#
#  (8)  https://learn.adafruit.com/micropython-basics-loading-modules/import-code
#
#
#
# Tangential topics:
#
#  (tan-1)  https://www.techonthenet.com/ascii/chart.php
#
# ----------------------------------------------------------------------
#

# alternate baudrates tested:  115200 - b'\xff' responses
#                                9600 - no response at either delay 1uS, 100uS
#                               38400 - no response at 1uS
#

serialPort = serial.Serial(port = "/dev/ttyUSB0",
                           baudrate=115200,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,   # PARITY_EVEN,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=0,
                           write_timeout=2.0)

        
serialString = ""                  # Used to hold data coming over UART

latest_byte = 'a'

bootloader_handshake_attempts = 0  # bound loop iterations to finite value

HANDSHAKE_ATTEMPTS_TO_MAKE = 4     # . . . was 20

#tries = 0

command_to_bootloader = 0
command_get_attempts = 0
COMMAND_GET_ATTEMPTS_TO_MAKE = 2



ONE_NANOSECOND           = 0.000000001
ONE_MICROSECOND          = 0.000001
TEN_MICROSECONDS         = 0.00001
ONE_HUNDRED_MICROSECONDS = 0.0001

#CHOSEN_DELAY = ONE_HUNDRED_MICROSECONDS
#CHOSEN_DELAY = TEN_MICROSECONDS
CHOSEN_DELAY = ONE_NANOSECOND

NXP_BOOTLOADER_START_BYTE = 0x5a



# ----------------------------------------------------------------------
# - SECTION - python data structures
#
# Reference https://www.geeksforgeeks.org/user-defined-data-structures-in-python/
# ----------------------------------------------------------------------

class framing_packet:
    def __init__(self, packet_type):
        self.start_byte = NXP_BOOTLOADER_START_BYTE
        self.packet_type = packet_type
        self.length_low = 0x00
        self.length_high = 0x00
        self.crc16_low = 0x00
        self.crc16_high = 0x00
        self.packet = None


class command_packet_header:
    def __init__(self, command_tag):
        self.command_or_response_tag = command_tag
        self.flags = None
        self.reserved = 0x00
        self.parameter_count = 0


class command_packet:
    def __init__(self, packet_header):
        self.header = packet_header





# ----------------------------------------------------------------------
# - SECTION - routines
# ----------------------------------------------------------------------

# Example code from reference (6) jimmywongiot.com:

# def serial_command(cmd):
#     serial_cmd = cmd + '\r'
#     return bytes(serial_cmd.encode())


##----------------------------------------------------------------------
##
## @brief:  this routine expects
##
##   *  an array of bytes
##   *  an integer value
##
## @note We would consider taking commands as single quoted strings,
##   however STMicro ROM based bootloader command set entails values
##   outside the traditional ASCII range.
##
##----------------------------------------------------------------------

def send_command_bootloader_stmicro(command_as_bytes, send_count):

    command_get_attempts = 0
    serialPort.write(bytes.fromhex("7f"))
    time.sleep(0.00001)

    print("sending", end=" ")
    print(command_as_bytes, end=" ")
    print("to bootloader . . .")

    while ( command_get_attempts < send_count ):
        command_get_attempts += 1
        time.sleep(CHOSEN_DELAY)
        serialPort.write(command_as_bytes)

        while ( serialPort.in_waiting == 0 ):
            time.sleep(CHOSEN_DELAY)

        while ( serialPort.in_waiting > 0 ):
            serialString = serialPort.read()
            print(serialString)

        print("")

    time.sleep(0.00001)



##----------------------------------------------------------------------
## @brief Routine to send command byte string to NXP bootloader
##----------------------------------------------------------------------

def send_command_bootloader_nxp(command_as_bytes, send_count):

    command_get_attempts = 0

    while ( command_get_attempts < send_count ):
        command_get_attempts += 1
        time.sleep(CHOSEN_DELAY)
        serialPort.write(command_as_bytes)




def command_with_xor(command):
    cmd = [0, 0]
    cmd[0] = command
    cmd[1] = (command ^ 0xFF)
    return bytes(cmd)


def send_address_of_memory(address):
    command_get_attempts = 0
    serialPort.write(bytes.fromhex("7f"))
    time.sleep(0.00001)

    print("sending memory address 0x", end="")
    print(address, end=" ")
    print(". . .")

#    while ( command_get_attempts < send_count ):
#        command_get_attempts += 1
    time.sleep(CHOSEN_DELAY)
    serialPort.write(address)

    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        serialString = serialPort.read()
        print(serialString)

    print("")

    time.sleep(0.00001)


def memory_address_with_crc(address):
    bytes_for_address = [0, 0, 0, 0, 0]
    bytes_for_address[0] = (( address >> 24 ) & 0xff )
    bytes_for_address[1] = (( address >> 16 ) & 0xff )
    bytes_for_address[2] = (( address >> 8 ) & 0xff )
    bytes_for_address[3] = (( address >> 0 ) & 0xff )
    bytes_for_address[4] = (bytes_for_address[0] ^ bytes_for_address[1] ^ bytes_for_address[2] ^ bytes_for_address[3]) & 0xff
    return bytes_for_address



# ----------------------------------------------------------------------
# - SECTION - main line code
# ----------------------------------------------------------------------

bootloader_handshake_attempts = 0

BOOTLOADER_COMMAND__GET         = 0x00
BOOTLOADER_COMMAND__GET_VERSION = 0x01
BOOTLOADER_COMMAND__GET_ID      = 0x02
BOOTLOADER_COMMAND__READ        = 0x11
BOOTLOADER_COMMAND__GO          = 0x21



## STMicro ROM based bootloader expects an initial byte holding 0x7F
##  as a sign to commence firmware updating over a serial protocol:
print("NXP bootloader client script starting,")
print("bootloader generic response tag from included python file is", end=" ")
print(hex(NXP_RESPONSE_TAG__GENERIC))



if (0):
    send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__GET),         1)

#latest_byte = send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__GET_ID), 1)
#print("latest byte received is ", end=" ")
#print(latest_byte)
#latest_byte = send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__GET_ID), 1)
#print("latest byte received is ", end=" ")
#print(latest_byte)

if (0):
    send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__GET_ID), 1)

#latest_byte = send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__READ), 1)
#print("latest byte received is ", end=" ")
#print(latest_byte)
#latest_byte = send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__READ), 1)
#print("latest byte received is ", end=" ")
#print(latest_byte)

if (0):
    print("sending read command . . .")
    send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__READ), 1)

    address_with_checksum = memory_address_with_crc(0x08000000)

    print("sending address to start of flash . . .")
    send_address_of_memory(address_with_checksum)



# def send_command_bootloader_nxp(command_as_bytes, send_count):
if (1):
    cmd = [0x5a, 0xa6]
    print("sending NXP \"ping\" command", end=" ")
    print(cmd, end=" ")
    print(". . .")
    send_command_bootloader_nxp(cmd, 2)

    print("waiting for response . . .")
    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        serialString = serialPort.read()
        print(serialString)

#    time.sleep(CHOSEN_DELAY)
    received_chars = 0
#    while ( received_chars < 9 ):
    if (1): # . . . avoid need to change below indent while exploring need for while construct at this indent - TMH
#        received_chars += 1

        while ( serialPort.in_waiting == 0 ):
            time.sleep(CHOSEN_DELAY)

        while ( serialPort.in_waiting > 0 ):
            serialString = serialPort.read()
            print(hex(serialString[0]), end=" ")
            print(serialString)
            if (0):
                print("received character count at", end=" ")
                print(received_chars)

        time.sleep(CHOSEN_DELAY)



    print("")


print("NXP bootloader client script done.")
