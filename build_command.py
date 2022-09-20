

from mcuboot_packets import *



#-----------------------------------------------------------------------
#
# @brief  Routine to build an NXP mcuboot command with up to four
#         parameters.  We'll need to amend this to support up to seven
#         parameters per MCUBOOTRM.pdf.
#
#-----------------------------------------------------------------------

def build_mcuboot_command_packet(command_tag, param_1, param_2, param_3, param_4):

# STEP 1 - create mcuboot framing packet
    framing_pkt = framing_packet(MCUBOOT_FRAMING_PACKET_TYPE__COMMAND)
    print("instantiated a first framing packet . . .")
#    display_framing_packet(first_packet)

# STEP 2 - create command header
    print("building command header and packet . . .")
    command_header = command_packet_header(command_tag)
    command_header.parameter_count = 2

# STEP 3 - construct list of command parameters (not all commands have parameters)
    command_params = [param_1, param_2]

# STEP 4 - construct command packet starting with header then add parameters
    command = command_packet(command_header)
    command.parameters = command_params
    print("showing command packet:")
    display_command_packet(command)

# STEP 5 - construct complete mcuboot command packet, framing piece plus header plus parameters
# Following routine knows how to take mcuboot framing packet, command packet, and build complete crc'd message:
    command_as_bytes = crc16.calc_len_and_crc_of(framing_pkt, command_header, command)

    print("0919 - read memory command with framing entails %u" % len(command_as_bytes), end=" ")
    print("bytes.")

    display_packet_as_bytes(command_as_bytes)

    return command_as_bytes
