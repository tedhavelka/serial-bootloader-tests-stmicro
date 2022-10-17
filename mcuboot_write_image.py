# ----------------------------------------------------------------------
#  @project   Python3 based bootloader host work
#
#  @file      mcuboot_write_image.py
# ----------------------------------------------------------------------



from nxpbl_common import *

from mcuboot_command_handling import *



## ---------------------------------------------------------------------
## - SECTION - defines
## ---------------------------------------------------------------------

ONE_KB = 1024
ONE_KB_DATA = ONE_KB


## ---------------------------------------------------------------------
## - SECTION - flash page sizes
## ---------------------------------------------------------------------

# For now, define part and part family flash page sizes here.
#
# NOTE - with NXP LPC55xxx family microcontrollers only in mind, measured
#  in bytes:
SIZE_FLASH_PAGE_OF_LPC55S69 = 512




SIZE_FLASH_PAGE = SIZE_FLASH_PAGE_OF_LPC55S69



COUNT_FLASH_PAGES_IN_ONE_KB_DATA = (ONE_KB_DATA / SIZE_FLASH_PAGE)

# Intermediate value used to figure max flash pages supported:
COUNT_FLASH_PAGES_IN_ONE_MB_DATA = ((ONE_KB * ONE_KB) / SIZE_FLASH_PAGE)

# Arbitrary, as of 2022-10-17 support up to 3MB firmware images per
#  above defined NXP flash page size:
MAX_COUNT_FLASH_PAGES_SUPPORTED = (3 * COUNT_FLASH_PAGES_IN_ONE_MB_DATA)




## ---------------------------------------------------------------------
## - SECTION - routines
## ---------------------------------------------------------------------

def write_firmware_image(file_handle, count_pages_to_flash_requested, options):

    if ( file_handle != None ):
        print("- DEV 1017 - caller sends non-null file handle,")
    else:
        print("- DEV 1017 - WARNING got null file handle!")

    print("- DEV 1017 - ready to support image write size up to %u flash pages," % MAX_COUNT_FLASH_PAGES_SUPPORTED)
    print("- DEV 1017 - caller wants to flash %u pages of data," % count_pages_to_flash_requested)
    print("- NOTE 1017 - start FLASH address fixed at zero, alt starting addrs not yet implemented.")



# --- VAR LOCAL BEGIN ---

    byte_count_to_flash = ( count_pages_to_flash_requested * SIZE_FLASH_PAGE )
    bytes_sent = 0

# Direct from Python serial port object
    val = 0

    mcuboot_response = []
    initial_response_received = 0
    ack_found = 0
    response_found = 0

# Successful in-going and out-going data phase commands entail two
# generic response packets from the bootloader, one is last bl response:
    ack_count = 0 
    generic_response_count = 0

# Used to detect various lengths of response packets from mcuboot bootloader
    response_length = 0 
    response_length_detected = 0 
    response_type = 0 
    response_type_detected = 0 

# flags:
    initial_response_received = 0          # steps 1 and 2
    final_generic_response_received = 0    # steps 6 and 7
    ack_just_sent = 0 
    yet_looking = 1 
    responses_ok = 0 

# client side variable to return success / failure status
    command_status = COMMAND_PROCESSING_OK

    local_diag_enabled = 1

# --- VAR LOCAL END ---


## - STEP - build, send command, look for initial ACK from bootloader:

    present_command = build_mcuboot_command_packet(MCUBOOT_COMMAND_TAG__WRITE_MEMORY,\
      0x00000000, byte_count_to_flash, None, None, None, None, None)

    time.sleep(CHOSEN_DELAY)
#    print("- DEV 0921 - sending command ", present_command, ". . .")
    bytes_sent = serialPort.write(present_command)
#    if (DIAG_0921):
#        print("- DEV 0921 - in-coming data phase command routine just sent", bytes_sent, "bytes")
#        print("    sent:", end=" ")
#        display_byte_array(present_command)

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

    print("- DEV 1017 - sending ACK prior to first data packet to write to flash . . .")
    bytes_sent = serialPort.write(ACK)
    if (bytes_sent == len(ACK)):
        print("    sent:", end=" ")
        display_byte_array(ACK)

    print("- DEV 1017 - out of loop for steps 1 and 2, command_status = %u" % command_status)
    print("( COMMAND_PROCESSING_OK = %u )" % COMMAND_PROCESSING_OK)




    if ( command_status == COMMAND_PROCESSING_OK ):
#   {

# ----------------------------------------------------------------------
# - STEP - write data packets per page of flash to be written
# ----------------------------------------------------------------------

# --- VAR LOCAL_2 BEGIN ---

        count_pages_flashed = 0
        array_1 = []
        present_data_packet = []

# --- VAR LOCAL_2 END ---


        while ( count_pages_flashed < count_pages_to_flash_requested ):
#       {
#            print("- DEV 1017 - STUB BLOCK FOR DATA WRITING WHILE LOOP")
#            count_pages_flashed = count_pages_to_flash_requested

### example call:  array_1 = append_n_bytes_from_hex_data_file(file_handle, TEST_COUNT)
            array_1 = append_n_bytes_from_hex_data_file(file_handle, SIZE_FLASH_PAGE)
            present_data_packet = build_mcuboot_data_packet(array_1)
            bytes_sent = serialPort.write(present_data_packet)
            if 1:
                print("just sent %u bytes in data packet," % len(present_data_packet))
                display_byte_array(present_data_packet)

# NEED TO IMPROVE error checking logic in following IF construct:
            if (bytes_sent > 0):
#                count_pages_flashed += 1
                command_status = COMMAND_PROCESSING_OK
            else:
                print("- WARNING - expected to send bytes but sent none, kicking out early . . .")
                count_pages_flashed = count_pages_to_flash_requested
                command_status = ERROR__COMMAND__TOO_FEW_BYTES_SENT

#            count_pages_flashed = count_pages_to_flash_requested


# (n) listen for ACK

            if ( command_status == COMMAND_PROCESSING_OK ):
#           {
                while ((initial_response_received == 0) and (yet_looking == 1)):
#               {
                    while ( serialPort.in_waiting == 0 ):
                        time.sleep(CHOSEN_DELAY)

                    while ( serialPort.in_waiting > 0 ):
                        val = serialPort.read()
                        mcuboot_response.append(val)

                    if(len(mcuboot_response) == 2):
                        ack_found = check_for_ack(mcuboot_response)

                    if( ack_found ):
                        count_pages_flashed += 1
                    else:
                        command_status = ERROR__COMMAND__UNEXPECTED_PACKET_TYPE

#               } end construct to look for ACK after each data packet sent to bootloader

#           } end construct to continue command handling after data sent to bootloader

#       } end WHILE construct to send data packets per page FLASH to write

#   }

    print("")




## --- EOF ---
