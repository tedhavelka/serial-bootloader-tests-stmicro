# ======================================================================
#  @project   Python3 based bootloader host work
#
#  @file mcuboot_command_handling.py
# ======================================================================



# ----------------------------------------------------------------------
# - SECTION - includes
# ----------------------------------------------------------------------

import time

from mcuboot_packets import *

from nxpbl_common import *         # to provide CHOSEN_DELAY and others

from build_command import *



# ----------------------------------------------------------------------
# - SECTION - effective constants
# ----------------------------------------------------------------------

DIAG__SHOW_DATA_TYPE_IN_ROUTINE__DISPLAY_BYTE_ARRAY = 0

DIAG_0921 = 1

# 2022-10-04 Tuesday . . .
COUNT_OF_DATA_BLOCKS_TO_SEND__DEV_1004 = 1



# ----------------------------------------------------------------------
# - SECTION - routines for development
# ----------------------------------------------------------------------

def read_file_for_firmware(filename):

# https://www.pythontutorial.net/python-basics/python-read-text-file/

    file_handle = open(filename, 'r')
    i = 0

    while (i < 5):
        i += 1
        line = file_handle.readline()
        print(line, end="")

    file_handle.close()



def test_data_payload(no_16_byte_lines):

    if (no_16_byte_lines > 65536):
        no_16_byte_lines = 65536
        print("- WARNING - test_data_payload() capping payload at %u bytes" % (16 * 65536))

    line_of_data = [0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff]
    test_data = []
    i = 0
    while ( i < no_16_byte_lines ):
        i += 1
        test_data.extend(line_of_data)

    if (1):
        print("0921 - routine test_data_payload constructed payload of %u bytes" % len(test_data))

    return test_data



# ----------------------------------------------------------------------
# - SECTION - routines
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
#        print("DEV - parsing length from:", mcuboot_response[3], mcuboot_response[2])
        arriving_packet_length = ( (int.from_bytes(mcuboot_response[2], "little"))
                                + ((int.from_bytes(mcuboot_response[3], "little")) << 8) )
        arriving_packet_length += LENGTH_MCUBOOT_FRAMING_PACKET
        return arriving_packet_length



def show_memory_values_in(mcuboot_response):
#{

    if(len(mcuboot_response) <= LENGTH_MCUBOOT_FRAMING_PACKET):
        print("WARNING - mcuboot packet too short to hold data!")
        print("WARNING + script may be calling this routine too soon or at wrong time.")
        return

#    if ((int.from_bytes(mcuboot_response[1], "little")) == 0xa5):
    if ((int.from_bytes(mcuboot_response[1], "little")) == MCUBOOT_FRAMING_PACKET_TYPE__DATA):
        print("show-memory-values routine received an outgoing phase data packet.")
    else:
        print("WARNING - show-memory-values routine received packet of type %02x." % (int.from_bytes(mcuboot_response[1], "little")))
        print("WARNING + not an mcuboot outgoing data phase packet,")
        print("WARNING + returning early . . .")
        return

    print("")

    if (1):
        i = 0
        for i in range(len(mcuboot_response) - LENGTH_MCUBOOT_FRAMING_PACKET):
            print("%02X" % (int.from_bytes(mcuboot_response[i + LENGTH_MCUBOOT_FRAMING_PACKET], "little")), end=" ")
            if(i > 0):
                if(((i + 1) % 8) == 0):
                    print(" ", end=" ")
                if(((i + 1) % 16) == 0):
                    print(" ")

    print("")

#}



# ----------------------------------------------------------------------
#  @brief  This routine displays data of python3 type <class 'bytes'>
#          and type <list> in hex format, sixteen values per line.
#
#  @note   Seemingly a lot of syntax hoops to jump through to get
#          list objects printable in a traditional hex dump format!
# ----------------------------------------------------------------------

def show_values_in(data):

    passed_data_of_type__class_bytes = 0
    passed_data_of_type__list        = 0

    if (type(data) is bytes):
        print("INFO 0922 - local test show we received data of type 'class bytes'")
        passed_data_of_type__class_bytes = 1

    if (type(data) is list):
        print("INFO 1004 - passed data is of type 'list'")
        passed_data_of_type__list = 1

    if (passed_data_of_type__class_bytes):
        i = 0
        for i in range(len(data)):
            print("%02X" % data[i], end=" ")
            if(i > 0):
                if(((i + 1) % 8) == 0):
                    print(" ", end=" ")
                if(((i + 1) % 16) == 0):
                    print(" ")

    if (passed_data_of_type__list):
        print("- INFO 1004 - passed data is of python type 'list',")
        print("- INFO 1004 - this list has %u elements," % len(data))
        count_data_elements = len(data)
#        print("- INFO 1004 - first element:")
#        print(data[0])
        i = 0
        while ( i < count_data_elements ):
            print("%02X" % int.from_bytes(data[i], "little"), end=" ")
            i += 1

    print("")



# ----------------------------------------------------------------------
#
#  @brief  This routine to support NXP mcuboot in-coming data phase
#          commands.  See MCUBOOTRM.pdf page 27 of 169.
#
#  @note   An mcuboot command with an "incoming data phase" from the
#          bootloader's perspective entails two generic response
#          packets.  As of 2022-09-20 this routine only finishes after
#          two generic response packets are received.
#
#  @implementation  This routine carries out a series of listening
#          for bytes steps, each time parsing those bytes for specific
#          mcuboot response packets.  These steps include:
#
#          (1) send command
#
#            (2) listen for ACK and initial response ( 0xA4 packet, MCUBOOTRM.pdf page 54 )
#
#
#          (3) send ACK and first data packet
#
#            (4) listen for ACK
#
#            (5) send next data packet
#
#            -- while data remains to send repeat steps 4 and 5 --
#
#
#          (6) listen for ACK and final response
#
#            (7) send ACK
#
#
#          The indented numbered steps are steps we perform when we
#          see expected responses from the bootloader.  When expected
#          responses are missing this routine exits early and returns
#          a failure status.
#
# ----------------------------------------------------------------------

def send_command_with_in_coming_data_phase(cmd, file_holding_data):
#{

# --- VAR BEGIN ---

    bytes_sent = 0

# client side variable to return success / failure status
    command_status = COMMAND_PROCESSING_OK

#    expected_acks_received = 0     # NEED to review this variable
#    expected_responses_received = 0 # NEED to review this variable

    mcuboot_response = []
    ack_found = 0                  # . . . used like a Boolean flag
    response_found = 0             # . . . used like a Boolean flag

# Used to detect various lengths of response packets from mcuboot bootloader
    response_length = 0
    response_length_detected = 0
    response_type = 0
    response_type_detected = 0

# Successful in-going and out-going data phase commands entail two
# generic response packets from the bootloader, one is last bl response:
    ack_count = 0
    generic_response_count = 0

# flags:
    initial_response_received = 0          # steps 1 and 2
    final_generic_response_received = 0    # steps 6 and 7
    ack_just_sent = 0
    yet_looking = 1
    responses_ok = 0

    local_diag_enabled = 1

# --- VAR END ---


    print("\n- DEV 0921 - in-coming data phase command starting,")
#    print("- DEV 0921 - opening data file . . .")
#    file_handle = open(file_holding_data,'r')

    if ( cmd[COMMAND_TAG_BYTEWISE_POSITIVE_OFFSET] == MCUBOOT_COMMAND_TAG__WRITE_MEMORY ):
        count_bytes_to_send = ( cmd[17] << 24 ) + ( cmd[16] << 16 ) + ( cmd[15] <<  8 ) + ( cmd[14] <<  0 )
        print("- DEV TEST 8 - write memory command has data payload of %u bytes," % count_bytes_to_send)


# (1) send command packet:

    time.sleep(CHOSEN_DELAY)
    print("- DEV 0921 - sending command ", cmd, ". . .")
    bytes_sent = serialPort.write(cmd)
    if (DIAG_0921):
        print("- DEV 0921 - in-coming data phase command routine just sent", bytes_sent, "bytes")
        print("    sent:", end=" ")
        display_byte_array(cmd)


# ----------------------------------------------------------------------
# - mcuboot response reading section               . . . in-coming data
# ----------------------------------------------------------------------

# (2) listen for ACK and initial response:

#   {
    while ((initial_response_received == 0) and (yet_looking == 1)):

        while ( serialPort.in_waiting == 0 ):
            time.sleep(CHOSEN_DELAY)
#       {
        while ( serialPort.in_waiting > 0 ):
            val = serialPort.read()
            mcuboot_response.append(val)


## ----------------------------------------------------------------------
##  STEP - detect packet types . . .                . . . in-coming data
## ----------------------------------------------------------------------

            if(len(mcuboot_response) == 2):
                ack_found = check_for_ack(mcuboot_response)

# Determine non-ACK packet length by readings its bytes three and four:

            if(len(mcuboot_response) == 4):
                response_length = parse_for_length_in(mcuboot_response)
#                print("present response to be", response_length, "bytes long,")
                response_length_detected = 1

# Detect packets longer than an ACK, longer than two bytes:

            if(response_length_detected):
                if(len(mcuboot_response) == response_length):
# When we find response note that, and note its type . . .
                    response_found = 1
                    response_type = int.from_bytes(mcuboot_response[1], "little")
#                    print("arriving response is of type 0x%02x" % response_type)
                    response_length_detected = 0


## ----------------------------------------------------------------------
##  STEP - respond to packet types . . .            . . . in-coming data
## ----------------------------------------------------------------------

            if(ack_found):
                ack_count += 1
                print("received:", end=" ")
                display_byte_array(mcuboot_response)
                mcuboot_response = []
                ack_found = 0

            if(response_found):
                print("received:", end=" ")
                display_byte_array(mcuboot_response)
                mcuboot_response = []
                response_found = 0

#       } // end WHILE construct to store bootloader responses


## ----------------------------------------------------------------------
##  STEP - respond to packet types . . .
## ----------------------------------------------------------------------

#  Assure bootloader responses valid and in correct order:

# MCUBOOTRM.pdf says this first response is generic but practice shows it
# arrives with a packet tag of type 'command' with value 0xA4:

        print("ack_count = %u" % ack_count, end=" ")
        print("generic_response_count = %u" % generic_response_count)

        if(response_type == MCUBOOT_FRAMING_PACKET_TYPE__COMMAND):
            if ((ack_count == 1) and (generic_response_count == 0)):
                generic_response_count += 1
                initial_response_received = 1
# We should only expect an initial response with command tag as packet type,
# immediately following an ACK, so other packets types received or
# different order of packets means we are done looking and have error to
# report:
        else:
            yet_looking = 0
            command_status = ERROR__COMMAND__UNEXPECTED_PACKET_TYPE
            if (DIAG_0921):
                print("- WARNING - got response packet type 0x%02x" % response_type, end=" ")
                print("expected 0x%02x" % MCUBOOT_FRAMING_PACKET_TYPE__COMMAND)


#   } // end WHILE construct to receive first ACK and first generic response

    bytes_sent = serialPort.write(ACK)
    if (bytes_sent == len(ACK)):
        print("    sent:", end=" ")
        display_byte_array(ACK)

    print("- DEV 0921 - out of loop for steps 1 and 2, command_status = %u" % command_status)
    print("( COMMAND_PROCESSING_OK = %u )" % COMMAND_PROCESSING_OK)



# ----------------------------------------------------------------------
#  Command transaction steps 3, 4 and 5 . . .
# ----------------------------------------------------------------------

#   {
    if (command_status == COMMAND_PROCESSING_OK):

        blocks_sent = 0
        data_remaining_to_send = count_bytes_to_send
        print("command indicates %u bytes to send," % count_bytes_to_send)

# (3) send ACK and first data packet

#       {
        while (data_remaining_to_send):

            data = test_data_payload(32)
            data_pkt = build_mcuboot_data_packet(data)

            print("- DEV TEST 8 - data packet contains:")
            show_values_in(bytes(data_pkt))

            bytes_sent = serialPort.write(data_pkt)
            print("- DEV TEST 8 - sent data packet of %u bytes," % bytes_sent)
            data_remaining_to_send -= 512
            blocks_sent += 1

            while ( serialPort.in_waiting == 0 ):
                time.sleep(CHOSEN_DELAY)

#           {
            while ( serialPort.in_waiting > 0 ):
                val = serialPort.read()
                mcuboot_response.append(val)

## ----------------------------------------------------------------------
##  STEP - detect packet types . . .                . . . in-coming data
## ----------------------------------------------------------------------

                if(len(mcuboot_response) == 2):
                    ack_found = check_for_ack(mcuboot_response)

## ----------------------------------------------------------------------
##  STEP - respond to packet types . . .            . . . in-coming data
## ----------------------------------------------------------------------

                if(ack_found):
                    ack_count += 1
                    print("received:", end=" ")
                    display_byte_array(mcuboot_response)
                    mcuboot_response = []
                    ack_found = 0

# Very simplistic catching of unexpectedly long packets:

                if(len(mcuboot_response) == 2):
                    print("- WARNING - received packet longer than expected ACK!")
                    print("- exiting 'command_with_incoming_data_phase' early . . .")
                    command_status = ERROR__COMMAND__UNEXPECTED_PACKET_TYPE

#           } // end WHILE loop to watch for ACK after each data block sent

#       } // end WHILE loop to support repeated data send, ACK return events

#   } // end IF construct to check transaction good so far



### IN-PROGRESS steps 6 and 7 will appear here . . .

    print("- DEV TEST 8 - at steps 6 and 7 mcuboot packet holds:")
    show_values_in(mcuboot_response)

    if (command_status == COMMAND_PROCESSING_OK):
        print("- DEV 1004 - made it to steps 6 and 7 stub code,")
        print("- DEV 1004 - in prior block sent %u blocks of 512 bytes of data" % blocks_sent)



    print("command of type in-coming data phase handling done.")

    return command_status

#}






# ----------------------------------------------------------------------
#
#  @brief  This routine carries out an mcuboot command via these steps:
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

# ----------------------------------------------------------------------
#  'See command through' version 1
#
#  @note  This routine designed to carry out an mcuboot command of
#         type out-going data phase, where data comes out of the
#         bootloader to the host or client program interacting with it.
# ----------------------------------------------------------------------

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

# - DEV 1008 -
    flash_page_count = 0

# --- VAR END ---


    time.sleep(CHOSEN_DELAY)
    bytes_sent = serialPort.write(cmd)
    print("seeing command through, just sent", bytes_sent, "bytes")
    print("    sent:", end=" ")
    display_byte_array(cmd)


# ----------------------------------------------------------------------
# - mcuboot response reading section
# ----------------------------------------------------------------------

    COUNT_GENERIC_RESPONSES_EXPECTED_FOR_OUT_GOING_DATA_PHASE = 2
    COUNT_GENERIC_RESPONSES_EXPECTED_FOR_NO_DATA_PHASE        = 1
#    COMMAND_TAG_BYTEWISE_POSITIVE_OFFSET = 6

    count_generic_reponses_expected = COUNT_GENERIC_RESPONSES_EXPECTED_FOR_OUT_GOING_DATA_PHASE
#    final_generic_response_not_received = 1
    final_generic_response_received = 0
    ack_just_sent = 0


    if (cmd[COMMAND_TAG_BYTEWISE_POSITIVE_OFFSET] == MCUBOOT_COMMAND_TAG__FLASH_ERASE_REGION ):
        count_generic_reponses_expected = COUNT_GENERIC_RESPONSES_EXPECTED_FOR_NO_DATA_PHASE

    print("'see command through' routine expecting %u generic responses," % count_generic_reponses_expected)


#   {
    while (final_generic_response_received == 0):

        while ( serialPort.in_waiting == 0 ):
            time.sleep(CHOSEN_DELAY)

#       {
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

#            if(generic_response_count >= 2):
            if(generic_response_count >= count_generic_reponses_expected):
                final_generic_response_received = 1


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
# - DEV 1008 -
                    flash_page_count += 1
                    print("memory values in latest response, flash page %u:" % flash_page_count)
                    show_memory_values_in(mcuboot_response)

                mcuboot_response = []
                response_found = 0
                ack_just_sent = 0

#       } // end WHILE construct to build mcuboot responses for parsing


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

#   } // end python while construct - while(final_generic_response_not_received)

###        show_memory_contents(memory_values)


# NEED to capture mcuboot command status value from final generic response packet - TMH
    return command_status




## --- EOF ---
