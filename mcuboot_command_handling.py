
import time

from mcuboot_packets import *

from nxpbl_common import *         # to provide CHOSEN_DELAY and others



# ----------------------------------------------------------------------
# - SECTION - routines
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
#  @brief  This routine sees an mcuboot command through via these steps:
#
#    (1)  send command bytes over UART
#    (2)  capture response byte stream
#    (3)  search for 'ACK' pattern in first two bytes of response,
#           error out if not found
#    (4)  search for generic response, typically eighteen bytes long
#    (5)  calc and check CRC in generic response,
#           error out when CRC incorrect
#    (6)  send an 'ACK'
#
# ----------------------------------------------------------------------

def display_byte_array(packet):
    for byte in packet:
        print("0x%02x" % int.from_bytes(byte, byteorder='little'), end=" ")
    print()



def send_and_see_command_through(cmd):

    bytes_sent = 0
    command_status = 0
    expected_responses_received = 0
    mcuboot_response = []

    time.sleep(CHOSEN_DELAY)
    bytes_sent = serialPort.write(cmd)
    print("seeing command through, just sent", bytes_sent, "bytes")

    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        val = serialPort.read()
        mcuboot_response.append(val)


    print("- DEV 0913 -")
#    display_packet_as_bytes(mcuboot_response)
    display_byte_array(mcuboot_response)
    print("- DEV 0913 -")


    return command_status

