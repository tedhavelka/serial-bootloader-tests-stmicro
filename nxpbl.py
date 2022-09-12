import serial
import time


# 2022-09-07
#
#  (8)  https://learn.adafruit.com/micropython-basics-loading-modules/import-code

## Note:  from bootloader_nxp_tags.py we are importing variables used as constants.
#from defines.bootloader_nxp_tags import *
#import bootloader_nxp_tags . . . namespace with bootloader tags as constants not getting shared
from bootloader_nxp_tags import *

import crc16

## Note:  from mcuboot_packets.py we are importing python classes to serve like C structures.
from mcuboot_packets import *


# 2022-09-10 SAT
# working on MCUBoot read memory command,
# MCUBOOTRM.pdf references:
#
#   page 28 . . . protocol of command with "outgoing" data phase, e.g. data from bootloader to host program
#   page 35 . . . 4.6 command packet structure
#   page 48 . . . read memory command, has parameters 'start address' and 'byte count'



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

SERIAL_PORT_READ_TIMEOUT = 1.0 # seconds

serialPort = serial.Serial(port = "/dev/ttyUSB0",
                           baudrate=115200,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,   # PARITY_EVEN,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=SERIAL_PORT_READ_TIMEOUT,
                           write_timeout=2.0)

        
serialString = ""                  # Used to hold data coming over UART

latest_byte = 'a'

bootloader_handshake_attempts = 0  # bound loop iterations to finite value

HANDSHAKE_ATTEMPTS_TO_MAKE = 4     # . . . was 20

#tries = 0

command_to_bootloader = 0
command_get_attempts = 0
COMMAND_GET_ATTEMPTS_TO_MAKE = 2



# ----------------------------------------------------------------------
# - SECTION - constants ( in primary bootloader client script )
# ----------------------------------------------------------------------

ONE_NANOSECOND           = 0.000000001
ONE_MICROSECOND          = 0.000001
TEN_MICROSECONDS         = 0.00001
ONE_HUNDRED_MICROSECONDS = 0.0001

#CHOSEN_DELAY = ONE_HUNDRED_MICROSECONDS
#CHOSEN_DELAY = TEN_MICROSECONDS
CHOSEN_DELAY = ONE_NANOSECOND



# Reference https://www.geeksforgeeks.org/user-defined-data-structures-in-python/


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



# STMicro command definitions:
BOOTLOADER_COMMAND__GET         = 0x00
BOOTLOADER_COMMAND__GET_VERSION = 0x01
BOOTLOADER_COMMAND__GET_ID      = 0x02
BOOTLOADER_COMMAND__READ        = 0x11
BOOTLOADER_COMMAND__GO          = 0x21


# STMicro bootloader related routine:
def command_with_xor(command):
    cmd = [0, 0]
    cmd[0] = command
    cmd[1] = (command ^ 0xFF)
    return bytes(cmd)


# STMicro bootloader related routine:
def send_address_of_memory(address):
    command_get_attempts = 0
    serialPort.write(bytes.fromhex("7f"))
    time.sleep(0.00001)

    print("sending memory address 0x", end="")
    print(address, end=" ")
    print(". . .")

    time.sleep(CHOSEN_DELAY)
    serialPort.write(address)

    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        serialString = serialPort.read()
        print(serialString)

    print("")

    time.sleep(0.00001)


# STMicro bootloader related routine:
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

xmodem_crc16 = 0


print("NXP bootloader client script starting,")

# ----------------------------------------------------------------------
# DEV TEST 1:
# ----------------------------------------------------------------------

print("bootloader generic response tag from included python file is", end=" ")
print(hex(MCUBOOT_RESPONSE_TAG__GENERIC))


# ----------------------------------------------------------------------
# DEV TEST 2:
# ----------------------------------------------------------------------

# See NXP document MCUBOOTRM.pdf for xmodem CRC16 variant, this test string and expected 0x31c3 result:
print("calling crc16 routine as test . . .")
crc_test_sequence = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39]
xmodem_crc16 = crc16.calc_crc16_with_carry_in(crc_test_sequence, 0)

print("crc16 xmodem variant routine test gives", end=" ")
print(hex(xmodem_crc16))


# ----------------------------------------------------------------------
# DEV TEST 4:
# ----------------------------------------------------------------------

first_packet = framing_packet(MCUBOOT_FRAMING_PACKET_TYPE__COMMAND)
print("instantiated a first framinig packet, showing its content . . .")
display_framing_packet(first_packet)

print("buidling command header and packet . . .")
command_header = command_packet_header(MCUBOOT_COMMAND_TAG__READ_MEMORY)
command_header.parameter_count = 2

read_memory_parameters = [0x20000400, 0x00000064]

command = command_packet(command_header)
command.parameters = read_memory_parameters 

print("showing command packet:")
display_command_packet(command)

# Following routine knows how to take mcuboot framing packet, command packet, and build complete crc'd message:
command_as_bytes = crc16.calc_len_and_crc_of(first_packet, command_header, command)

print("DEV TEST 4 - read memory command with framing entails %u" % len(command_as_bytes), end=" ")
print("bytes.")
print("INFO: dev tests done.")



## ---------------------------------------------------------------------
## Note:  STMicro ROM based bootloader expects an initial byte holding
##  0x7F as a sign to commence firmware updating over a serial protocol.

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
        if ( serialString[0] == 0x5a ):
            print()
#        print(hex(serialString[0]), end=" ")
# Reference https://stackoverflow.com/questions/61206672/how-to-add-leading-0-to-hexadecimal
        val = serialString[0]
        print("0x%02x" % val, end=" ")
        print(serialString)

    print("- INFO - response to ping command appears done.")
    print("- STEP - reading serial port once more as a timeout test,")
    print("       ( timeout set to", end=" ")
    print(SERIAL_PORT_READ_TIMEOUT, end=" ")
    print(")")
    serialString = serialPort.read()

    print("")


print("NXP bootloader client script done.")
