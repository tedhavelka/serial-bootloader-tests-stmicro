
import time

from mcuboot_packets import *

from nxpbl_common import *         # to provide CHOSEN_DELAY and others



DIAG__SHOW_DATA_TYPE_IN_ROUTINE__DISPLAY_BYTE_ARRAY = 0



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

    count_start_bytes_detected = 0

    for j in range(len(packet)):

        if(packet[j] == 0x5a):
            count_start_bytes_detected += 1

        if((packet[j] == 0x5a) and (count_start_bytes_detected > 1)):
            print()

#        if(len(packet) > 2):
        if(isinstance(packet[j], int)):
            print("%02x" % packet[j], end=" ")

        elif(isinstance(packet[j], bytes)):
            int_val = int.from_bytes(bytes(packet[j]), "little")
            print("%02x" % int_val, end=" ")

        else:
            print(packet[j], end=" ")


# Reference https://www.freecodecamp.org/news/python-print-type-of-variable-how-to-get-var-type/
    if(DIAG__SHOW_DATA_TYPE_IN_ROUTINE__DISPLAY_BYTE_ARRAY):
        print("\nDEV 0914 - parameter 'packet' is of type", type(packet))
        print("DEV 0914 - parameter 'packet[0]' is of type", type(packet[0]))

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



# ----------------------------------------------------------------------
# @brief  Initially this routine is a stub, always returning effectively
#         the value 'true'.  We'll add to it such that we check also
#         for mcuboot response integrity, by calculating its checksum
#         and comparing that with the checksum which arrived as part
#         of the response packet.
# ----------------------------------------------------------------------

def check_for_response(packet):
#    print("stub 0913")
    return 1



def send_and_see_command_through(cmd):

    bytes_sent = 0
    command_status = 0
    expected_acks_received = 0
    expected_responses_received = 0

    mcuboot_response = []
    ack_found = 0
    response_found = 0

    ack = []
    ack.append(0x5a)
    ack.append(0xa1)


    time.sleep(CHOSEN_DELAY)
    bytes_sent = serialPort.write(cmd)
    print("seeing command through, just sent", bytes_sent, "bytes")
    print("    sent:", end=" ")
    display_byte_array(cmd)

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

# NEED to improve following IF test to handle packets which are not 18 bytes long - TMH
        if(len(mcuboot_response) == 18):
            response_found = check_for_response(mcuboot_response)

        if(ack_found):
            expected_acks_received += 1
            if(0):
                print("received ACK packet!")
            else:
                print("received:", end=" ")
                display_byte_array(mcuboot_response)
            mcuboot_response = []
            ack_found = 0

        if(response_found):
            expected_responses_received += 1
#            print("received response packet . . .")
            print("received:", end=" ")
            display_byte_array(mcuboot_response)
            mcuboot_response = []
            response_found = 0


# construct mcuboot ACK packet:
#    x = '5aa1'
#    cmd[0] = 0x5a, cmd[1] = 0xa1 . . . python syntax error 'cannot assign to literal'
# Reference https://www.w3resource.com/python/python-bytes.php#bliterals
#    cmd = bytes.fromhex(x)
#    print("DEV 0914-b - parameter 'cmd' is of type", type(cmd))
#    ack = mcuboot_ack_packet()
#    print("DEV 0914-b - class instance 'ack' is of type", type(ack))
#    print("DEV 0914-b - global variable 'ACK' is of type", type(ACK))


    time.sleep(0.1)
#    display_byte_array(ACK)
    bytes_sent = serialPort.write(ACK)
    if(bytes_sent == 2):
        print("    sent:", end=" ")
        display_byte_array(ACK)
    else:
        print("WARNING - sent something shorter or longer than ACK packet!")

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
#            print("received ACK packet!")
            print("received:", end=" ")
            expected_acks_received += 1
            display_byte_array(mcuboot_response)
            mcuboot_response = []
            ack_found = 0

        if(response_found):
#            print("received response packet . . .")
            print("received:", end=" ")
            expected_responses_received += 1
            display_byte_array(mcuboot_response)
            mcuboot_response = []
            response_found = 0




    return command_status

