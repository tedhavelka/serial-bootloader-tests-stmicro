
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

#def check_for_response(packet):
#    print("stub 0913")
#    return 1


def parse_for_length_in(mcuboot_response):

    arriving_packet_length = 0

    if(len(mcuboot_response) < OFFSET_LAST_FRAMING_HEADER_BYTE_INDICATING_PACKET_LENGTH):
        print("WARNING - packet fragment too small to parse for packet length!")
        return 0
    else:
        print("DEV - parsing length from:", mcuboot_response[3], mcuboot_response[2])
#        arriving_packet_length = ( (int(bytes(mcuboot_response[3])) << 8) + (int(bytes(mcuboot_response[2]))) )
        arriving_packet_length = ( (int.from_bytes(mcuboot_response[2], "little"))
                                + ((int.from_bytes(mcuboot_response[3], "little")) << 8) )
        arriving_packet_length += LENGTH_MCUBOOT_FRAMING_PACKET
        return arriving_packet_length



def show_memory_values_in(mcuboot_response):

    if(len(mcuboot_response) <= LENGTH_MCUBOOT_FRAMING_PACKET):
        print("WARNING - mcuboot packet too short to hold data!")
        print("WARNING + script may be calling this routine too soon or at wrong time.")
        return

    if ((int.from_bytes(mcuboot_response[1], "little")) == 0xa5):
        print("show-memory-values routine received an outgoing phase data packet.")
    else:
        print("WARNING - show-memory-values routine received packet of type %02x." % (int.from_bytes(mcuboot_response[1], "little")))
        print("WARNING + not an mcuboot outgoing data phase packet,")
        print("WARNING + returning early . . .")
        return

    print("zzzzzz")

# Here outermost IF construct used to test for response tag type:
    if (1):
        i = 0
        for i in range(len(mcuboot_response) - LENGTH_MCUBOOT_FRAMING_PACKET):
            print("%02X" % (int.from_bytes(mcuboot_response[i + LENGTH_MCUBOOT_FRAMING_PACKET], "little")), end=" ")
            if(i > 0):
                if(((i + 1) % 8) == 0):
                    print(" ", end=" ")
                if(((i + 1) % 16) == 0):
                    print(" ")

    print("zzzzzz")



def send_and_see_command_through(cmd):

# --- VAR BEGIN ---

    bytes_sent = 0
    command_status = 0
    expected_acks_received = 0     # NEED to review this variable
    expected_responses_received = 0 # NEED to review this variable

    mcuboot_response = []
    ack_found = 0
    response_found = 0

#    ack = []
#    ack.append(0x5a)
#    ack.append(0xa1)

# Used to detect various lengths of response packets from mcuboot bootloader
    response_length = 0
    response_length_detected = 0
    response_type = 0
    response_type_detected = 0

# To receive second generic response in memory read command signifies all data sent to host
    generic_response_count = 0

# --- VAR END ---


    time.sleep(CHOSEN_DELAY)
    bytes_sent = serialPort.write(cmd)
    print("seeing command through, just sent", bytes_sent, "bytes")
    print("    sent:", end=" ")
    display_byte_array(cmd)


# ----------------------------------------------------------------------
# - mcuboot response reading section
# ----------------------------------------------------------------------

    final_generic_response_not_received = 1
    ack_just_sent = 0

    while (final_generic_response_not_received == 1):

        while ( serialPort.in_waiting == 0 ):
            time.sleep(CHOSEN_DELAY)

        while ( serialPort.in_waiting > 0 ):
            val = serialPort.read()
            mcuboot_response.append(val)


## ----------------------------------------------------------------------
##  STEP - detect packet types . . .
## ----------------------------------------------------------------------

            if(len(mcuboot_response) == 2):
                ack_found = check_for_ack(mcuboot_response)

# NEED to improve following IF test to handle packets which are not 18 bytes long - TMH
#            if(len(mcuboot_response) == 18):
#                response_found = check_for_response(mcuboot_response)

            if(len(mcuboot_response) == 4):
                response_length = parse_for_length_in(mcuboot_response)
                print("present response to be", response_length, "bytes long,")
                response_length_detected = 1

            if(response_length_detected):
                if(len(mcuboot_response) == response_length):
                    response_found = 1
                    response_type = int.from_bytes(mcuboot_response[1], "little")
                    print("arriving response is of type 0x%02x" % response_type)

                    response_length_detected = 0


## ----------------------------------------------------------------------
##  STEP - track multi-packet events
## ----------------------------------------------------------------------

            if(response_type == 0xa4):
                generic_response_count += 1
                response_type = 0

            if(generic_response_count >= 2):
                final_generic_response_not_received = 0


## ----------------------------------------------------------------------
##  STEP - respond to packet types . . .
## ----------------------------------------------------------------------

            if(ack_found):
                expected_acks_received += 1
                if(0):
                    print("received ACK packet!")
                else:
                    print("received:", end=" ")
                    display_byte_array(mcuboot_response)
                mcuboot_response = []
                ack_found = 0
                ack_just_sent = 0

            if(response_found):
                expected_responses_received += 1
                print("received:", end=" ")
                display_byte_array(mcuboot_response)

                if(response_type == 0xa5):
                    print("memory values in latest response:")
                    show_memory_values_in(mcuboot_response)

                mcuboot_response = []
                response_found = 0
                ack_just_sent = 0


# send ACK following response packets:
        if(not ack_just_sent):
#        if(1):
            ack_just_sent = 1
            bytes_sent = serialPort.write(ACK)
            if(bytes_sent == len(ACK)):
                print("    sent:", end=" ")
                display_byte_array(ACK)
            else:
                print("WARNING - failed to send normal two bytes of ACK packet!")

#   end python while construct - while(final_generic_response_not_received)

###        show_memory_contents(memory_values)


# NEED to capture mcuboot command status value from final generic response packet - TMH
    return command_status




