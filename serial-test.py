import serial
import time

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
# ----------------------------------------------------------------------
#

# alternate baudrates tested:  115200 - b'\xff' responses
#                                9600 - no response at either delay 1uS, 100uS
#                               38400 - no response at 1uS
#

serialPort = serial.Serial(port = "/dev/ttyUSB0",
                           baudrate=115200,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_EVEN,
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




# ----------------------------------------------------------------------
# - SECTION - routines
# ----------------------------------------------------------------------

# Example code from reference (6) jimmywongiot.com:

# def serial_command(cmd):
#     serial_cmd = cmd + '\r'
#     return bytes(serial_cmd.encode())


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

def send_bootloader_cmd(command_as_bytes, send_count):

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
#    return serialString


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

## STMicro ROM based bootloader expects an initial byte holding 0x7F
##  as a sign to commence firmware updating over a serial protocol:
print("Script starting,")


print("At loop to attempt bootloader handshake several times:")
while ( bootloader_handshake_attempts < HANDSHAKE_ATTEMPTS_TO_MAKE ):
    bootloader_handshake_attempts += 1
    time.sleep(CHOSEN_DELAY)
    serialPort.write(bytes.fromhex("7f"))
    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)
    serialString = serialPort.readline()
    print(serialString)

bootloader_handshake_attempts = 0



BOOTLOADER_COMMAND__GET         = 0x00
BOOTLOADER_COMMAND__GET_VERSION = 0x01
BOOTLOADER_COMMAND__GET_ID      = 0x02
BOOTLOADER_COMMAND__READ        = 0x11
BOOTLOADER_COMMAND__GO          = 0x21

## def send_bootloader_cmd(command_as_bytes, send_count):
send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__GET_VERSION), 1)

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

if (1):
    print("sending read command . . .")
    send_bootloader_cmd(command_with_xor(BOOTLOADER_COMMAND__READ), 1)

    address_with_checksum = memory_address_with_crc(0x08000000)

    print("sending address to start of flash . . .")
    send_address_of_memory(address_with_checksum)




#print("At original loop designed to read serial port received bytes:")
#while(1):
#
#    # Wait until there is data waiting in the serial buffer
#    if(serialPort.in_waiting > 0):
#
#        # Read data out of the buffer until a carraige return / new line is found
#        serialString = serialPort.readline()
#
#        # Print the contents of the serial data
#        print(serialString)


print("script done.")
