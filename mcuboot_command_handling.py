
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
        if (int.from_bytes(byte, byteorder='little') == MCUBOOT_BOOTLOADER_START_BYTE):
            print()
        print("0x%02x" % int.from_bytes(byte, byteorder='little'), end=" ")
    print()



def check_for_ack(packet):

#    print("checking for ACK, packet byte zero holds %u" % int.from_bytes(packet[0], byteorder='little'))
#    print("packet byte one holds %u" % int.from_bytes(packet[1], byteorder='little'))
#    print("python interprets int(MCUBOOT_BOOTLOADER_START_BYTE) as %u" % int(MCUBOOT_BOOTLOADER_START_BYTE))
#    print("python interprets int(MCUBOOT_FRAMING_PACKET_TYPE__ACK) as %u" % int(MCUBOOT_FRAMING_PACKET_TYPE__ACK))

    if (int.from_bytes(packet[0], byteorder='little') == int(MCUBOOT_BOOTLOADER_START_BYTE) and
        int.from_bytes(packet[1], byteorder='little') == int(MCUBOOT_FRAMING_PACKET_TYPE__ACK)):
        return 1
    else:
        return 0



def check_for_response(packet):
    print("stub 0913")
    return 0



def send_and_see_command_through(cmd):

    bytes_sent = 0
    command_status = 0
    expected_acks_received = 0
    expected_responses_received = 0

    mcuboot_response = []
    ack_found = 0
    response_found = 0

    time.sleep(CHOSEN_DELAY)
    bytes_sent = serialPort.write(cmd)
    print("seeing command through, just sent", bytes_sent, "bytes")

#
# - mcuboot response reading section
#
    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        val = serialPort.read()
        mcuboot_response.append(val)

        if(len(mcuboot_response) == 2):
            ack_found = check_for_ack(mcuboot_response)

        if(len(mcuboot_response) == 18):
            response_found = check_for_response(mcuboot_response)

        if(ack_found):
            print("received ACK packet!")
            expected_acks_received += 1
            display_byte_array(mcuboot_response)
            mcuboot_response = []
            ack_found = 0

        if(response_found):
            print("received response packet . . .")
            expected_responses_received += 1
            response_found = 0

    print("response: ", end=" ")
    display_byte_array(mcuboot_response)
#    print("- DEV 0913 -")



# construct mcuboot ACK packet:
    cmd = [0x5a, 0xa1]

    time.sleep(0.1)
# send ACK:
    print("- DEV 0913 - sending ACK to bootloader . . .")
    bytes_sent = serialPort.write(cmd)

    print("- DEV 0913 - sent %u bytes," % bytes_sent)
    print("- DEV 0913 - waiting for response . . .")
    while ( serialPort.in_waiting == 0 ):
        time.sleep(CHOSEN_DELAY)

    while ( serialPort.in_waiting > 0 ):
        val = serialPort.read()
        mcuboot_response.append(val)


    print("response: ", end=" ")
    display_byte_array(mcuboot_response)


    return command_status

