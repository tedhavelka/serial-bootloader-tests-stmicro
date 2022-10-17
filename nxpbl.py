# ======================================================================
#  @project   Python3 based bootloader host work
#
#  @file nxpbl.py   NXP mcuboot bootloader host program
# ======================================================================



# ----------------------------------------------------------------------
# - SECTION - includes
# ----------------------------------------------------------------------

# python3 includes . . .
import serial
import time


# local project includes . . .
from mcuboot_tags import *

import crc16

from mcuboot_packets import *

from mcuboot_command_handling import *

from nxpbl_common import *

from build_command import *

from mcuboot_write_image import *



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
#   (1)  https://www.tutorialspoint.com/increment-and-decrement-operators-in-python
#
#   (2)  https://www.geeksforgeeks.org/print-without-newline-python/
#
#   (3)  https://www.askpython.com/python-modules/python-time-sleep-method 
#
#   (4)  https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.write
#
#   (5)  https://gist.github.com/yptheangel/fcd62ad59a569ace75eb07025b8e9c4f . . . serialPort.write(bytes.fromhex("a5"))
#
#   (6)  https://jimmywongiot.com/2021/03/13/byte-manipulation-on-python-platform/
#
#  Note STM32WL55 flash memory start mapped to 0x08000000, per document:
#   (7)  rm0453-stm32wl5x-advanced-armbased-32bit-mcus-with-subghz-radio-solution-stmicroelectronics.pdf
#
#
# 2022-09-07
#
#   (8)  https://learn.adafruit.com/micropython-basics-loading-modules/import-code
#
#   (9)  https://docs.python.org/3/library/stdtypes.html . . . int.from_bytes(value, byteorder="little")
#
#  (10)  http://dabeaz.blogspot.com/2010/01/few-useful-bytearray-tricks.html
#
#  (11)  https://www.alpharithms.com/python-bytearray-built-in-function-123516/
#
#
# 2022-09-20
#
#  (12)  https://www.digitalocean.com/community/tutorials/read-stdin-python
#
#
# Tangential topics:
#
#  (tan-1)  https://www.techonthenet.com/ascii/chart.php
#
# ----------------------------------------------------------------------
#


# ----------------------------------------------------------------------
# - SECTION - effective constants
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# - SECTION - development defines
# ----------------------------------------------------------------------

DEV_TEST_1__ = 0
DEV_TEST_2__ = 0
DEV_TEST_3__READ_MEMORY     = 1
DEV_TEST_4__ERASE_REGION    = 0
DEV_TEST_5__ERASE_ALL       = 0
DEV_TEST_6__BYTES_FROM_FILE = 0
DEV_TEST_7__READ_FILE       = 0
DEV_TEST_8__WRITE_MEMORY    = 0
DEV_TEST_9__WRITE_IMAGE     = 1

DEV_TEST__CLOSING_MESSAGE   = 1



# ----------------------------------------------------------------------
# - SECTION - globals
# ----------------------------------------------------------------------

serialString = ""                  # Used to hold data coming over UART

latest_byte = 'a'

bootloader_handshake_attempts = 0  # bound loop iterations to finite value

HANDSHAKE_ATTEMPTS_TO_MAKE = 4     # . . . was 20

# NEED TO REVIEW following three variables:
command_to_bootloader = 0
command_get_attempts = 0
COMMAND_GET_ATTEMPTS_TO_MAKE = 2



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
##
## Reference https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.write
##----------------------------------------------------------------------

def send_command_bootloader_nxp(command_as_bytes, send_count):

    command_get_attempts = 0
    bytes_sent = 0

    while ( command_get_attempts < send_count ):
        command_get_attempts += 1
        time.sleep(CHOSEN_DELAY)
        bytes_sent = serialPort.write(command_as_bytes)

    return bytes_sent


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
#  @brief   Routine - first draft - to parse mcuboot response packets
# ----------------------------------------------------------------------

def parse_packet(packet):

#    print("Parser:  got packet of %u bytes to parse," % len(packet))
#    print("  zzzzz")

    if (1):
        print(" ", end=" ")
        for byte in packet:
            print("0x%02x" % int.from_bytes(byte, byteorder='little'), end=" ")
        print()

# - CHECK - for 'ACK' type packet . . .
    if(len(packet) == 2):
        if((int.from_bytes(packet[1], byteorder='little') == MCUBOOT_BOOTLOADER_START_BYTE) and
           (int.from_bytes(packet[0], byteorder='little') == MCUBOOT_FRAMING_PACKET_TYPE__ACK)):
            print("parser - DEV 0912 - packet is 'basic ack' type.")

#    print("  zzzzz")



# ----------------------------------------------------------------------
#  @brief   Routine to display response from MCU bootloader.
#
#  2022-09-12 NEED to review this routine, may be superceded by
#    newer routine(s) in mcuboot_command_handling.py.
# ----------------------------------------------------------------------

def listen_for_mcuboot_response(display_option):

    bootloader_response = []
    response_previous = []

    print("listener routine called to parse response . . .", end=" ")
#    print("LISTENER ROUTINE CALLED TO PARSE RESPONSE . . .", end=" ")
    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        val = serialPort.read()
        bootloader_response.append(val)

# When we detect an MCUBoot start byte then add a white space line for clarity of output:
        if ( val[0] == 0x5a ):
            print()

        if (display_option == DISPLAY_BYTE_PER_LINE):
            print("0x%02x" % val[0], end=" ")
            print(val)
        else:
            print("0x%02x" % val[0], end=" ")

    print()



# ----------------------------------------------------------------------
# - SECTION - main line code
# ----------------------------------------------------------------------

bootloader_handshake_attempts = 0

xmodem_crc16 = 0


print("NXP bootloader client script starting,")

# ----------------------------------------------------------------------
# DEV TEST 1:
# ----------------------------------------------------------------------

# print("bootloader generic response tag from included python file is", end=" ")
# print(hex(MCUBOOT_RESPONSE_TAG__GENERIC))


# ----------------------------------------------------------------------
# DEV TEST 2:
# ----------------------------------------------------------------------

## See NXP document MCUBOOTRM.pdf for xmodem CRC16 variant, this test string and expected 0x31c3 result:
# print("calling crc16 routine as test . . .")
# crc_test_sequence = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39]
# xmodem_crc16 = crc16.calc_crc16_with_carry_in(crc_test_sequence, 0)
#
# print("crc16 xmodem variant routine test gives", end=" ")
# print(hex(xmodem_crc16))



# ----------------------------------------------------------------------
# SEND MCUBOOT PING PACKET 0x5AA6 . . .
# ----------------------------------------------------------------------

if (1):
    cmd = [0x5a, 0xa6]
    print("sending NXP \"ping\" command", end=" ")
    print(cmd, end=" ")
    print(". . .")
    send_command_bootloader_nxp(cmd, 1)

    print("waiting for response . . .")
    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        serialString = serialPort.read()

# When we detect an MCUBoot start byte then add a white space line for clarity of output:
        if ( serialString[0] == 0x5a ):
            print()

# Reference https://stackoverflow.com/questions/61206672/how-to-add-leading-0-to-hexadecimal
        val = serialString[0]
        print("0x%02x" % val, end=" ")
        print(serialString)

    print("\nINFO - response to ping command appears done.\n")


# ----------------------------------------------------------------------
# DEV TEST 3:
# ----------------------------------------------------------------------

if (DEV_TEST_3__READ_MEMORY):
    print("\n\nDEV TEST 3 - test of 'read memory' command underway:")

# STEP 1 - create mcuboot framing packet
    first_packet = framing_packet(MCUBOOT_FRAMING_PACKET_TYPE__COMMAND)

# STEP 2 - create command header
    print("buidling command header and packet . . .")
    command_header = command_packet_header(MCUBOOT_COMMAND_TAG__READ_MEMORY)
    command_header.parameter_count = 2

# STEP 3 - construct list of command parameters (not all commands have parameters)
##
## REF https://www.mathsisfun.com/binary-decimal-hexadecimal-converter.html
##
## $ grep '   [0-9A-F][0-9A-F] ' 48k-read-001.txt > bytes-to-c000.txt
##
#    read_memory_parameters = [0x00000000, 0x00000018]
#    read_memory_parameters = [0x00000000, 0x00000400]
    read_memory_parameters = [0x00000000, 0x0000c000]
    read_memory_parameters = [0x00000000, 0x0000a400]

# STEP 4 - construct command packet starting with header then add parameters
    command = command_packet(command_header)
    command.parameters = read_memory_parameters 
    print("showing command packet:")
    display_command_packet(command)

# STEP 5 - construct complete mcuboot command packet, framing piece plus header plus parameters
# Following routine knows how to take mcuboot framing packet, command packet, and build complete crc'd message:
    command_as_bytes = crc16.calc_len_and_crc_of(first_packet, command_header, command)

    print("\nDEV TEST 3 - read memory command with framing entails %u" % len(command_as_bytes), end=" ")
    print("bytes.")

    display_packet_as_bytes(command_as_bytes)

    print("DEV TEST 3 - sending 'read memory' command . . .")
    send_and_see_command_through(command_as_bytes)



# ----------------------------------------------------------------------
# DEV TEST 4:
# ----------------------------------------------------------------------

if (DEV_TEST_4__ERASE_REGION):
    print("\n\nDEV_TEST_4 - erase region test . . .")
    start_addr = 0x00000000
    byte_count = 0x00000600
    present_command = build_mcuboot_command_packet(MCUBOOT_COMMAND_TAG__FLASH_ERASE_REGION,\
      start_addr, byte_count, None, None, None, None, None)

#    print("erase region command packet holds:")
#    display_packet_as_bytes(present_command)

    print("\n\nDEV_TEST_4 - calling routine to send command . . .")
    send_and_see_command_through(present_command)
    print("\n\nDEV_TEST_4 - back from routine to send erase command,")



# ----------------------------------------------------------------------
# DEV TEST 5:
# ----------------------------------------------------------------------

if (DEV_TEST_5__ERASE_ALL):
    print("\n\nDEV_TEST_5 - erase all flash test . . .")
    present_command = build_mcuboot_command_packet(MCUBOOT_COMMAND_TAG__FLASH_ERASE_ALL,\
      None, None, None, None, None, None, None)

    send_and_see_command_through(present_command)
    print("\n\nDEV_TEST_5 - back from test of 'erase all flash' command,")



# ----------------------------------------------------------------------
# DEV TEST 6:
# ----------------------------------------------------------------------

if (DEV_TEST_6__BYTES_FROM_FILE):

    print("\nDEV TEST 6 - reading file and building byte array:")
    filename = "./notes/41k.bin"
    file_handle = open(filename, 'r')
    array_1 = []

    TEST_COUNT = 24
#    array_1 = append_sixteen_bytes_from_hex_data_file(file_handle)
    array_1 = append_n_bytes_from_hex_data_file(file_handle, TEST_COUNT)

    file_handle.close()
    print("array returned by 1014 file dev work holds:")
#    print(array_1, end="\n")
    show_values_in(array_1)
    


# ----------------------------------------------------------------------
# DEV TEST 7:
# ----------------------------------------------------------------------

if (DEV_TEST_7__READ_FILE):
    print("\nDEV TEST 7 - testing read file routine, will read five lines:")
    read_file_for_firmware('notes/41k.bin')



# ----------------------------------------------------------------------
# DEV TEST 8:
# ----------------------------------------------------------------------

if (DEV_TEST_8__WRITE_MEMORY):

    print("\nDEV TEST 8 - testing write memory command")

# def build_mcuboot_command_packet(command_tag, param_1, param_2, param_3, param_4, param_5, param_6, param_7)
    present_command = build_mcuboot_command_packet(MCUBOOT_COMMAND_TAG__WRITE_MEMORY,\
      0x00000000, 0x00000600, None, None, None, None, None)

# Note the 'write memory' command will itself contain the start address
# and number of bytes of data to write, so no need to parameterize
# these values:

    send_command_with_in_coming_data_phase(present_command, 'notes/blinky.bin')



# ----------------------------------------------------------------------
# DEV TEST 9:  write image
# ----------------------------------------------------------------------

if (DEV_TEST_9__WRITE_IMAGE):
    print("\nDEV TEST 9 - test of write image routines")
    filename = "./notes/41k.bin"
    file_handle = open(filename, 'r')
    write_firmware_image(file_handle, 82, 0)
    file_handle.close()



# ----------------------------------------------------------------------
# END OF DEVELOPMENT TESTS:
# ----------------------------------------------------------------------

if (DEV_TEST__CLOSING_MESSAGE):
    print("INFO: dev tests done.")

    print("\n- STEP - reading serial port once more as a timeout test,")
    print("       ( timeout set to", end=" ")
    print(SERIAL_PORT_READ_TIMEOUT, end=" ")
    print(")")
    serialString = serialPort.read()

    print("")


print("\nNXP bootloader client script done.")
