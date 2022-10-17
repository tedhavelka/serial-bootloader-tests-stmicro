# ----------------------------------------------------------------------
#  @project   Python3 based bootloader host work
#
#  @file      build_command.py
# ----------------------------------------------------------------------



from mcuboot_packets import *



#-----------------------------------------------------------------------
#
# @brief  Routine to build an NXP mcuboot command with up to four
#         parameters.  We'll need to amend this to support up to seven
#         parameters per MCUBOOTRM.pdf.
#
#-----------------------------------------------------------------------

def build_mcuboot_command_packet(command_tag, param_1, param_2, param_3, param_4, param_5, param_6, param_7):

# STEP 1 - create mcuboot framing packet
    framing_pkt = framing_packet(MCUBOOT_FRAMING_PACKET_TYPE__COMMAND)
    print("instantiated a first framing packet . . .")
#    display_framing_packet(first_packet)

# STEP 2 - create command header
    print("building command header and packet . . .")
    command_header = command_packet_header(command_tag)
    command_header.parameter_count = 2

# STEP 3 - construct list of command parameters (not all commands have parameters)
    if (param_1 == None):
        if ():
            print("NOTE - mcuboot command 'erase all flash' has no parameters.")
        else:
            print("NOTE - command given by command tag %u has no parameters." % command_tag)
    elif ((param_2 != None) and (param_3 == None)):
        command_params = [param_1, param_2]
        command.parameters = command_params
    elif (param_7 != None):
            print("DEV NOTE - got a parameter number 7 from caller!")


# STEP 4 - construct command packet starting with header then add parameters
    command = command_packet(command_header)
##    command.parameters = command_params
#    print("showing command packet:")
#    display_command_packet(command)

# STEP 5 - construct complete mcuboot command packet, framing piece plus header plus parameters
# Following routine knows how to take mcuboot framing packet, command packet, and build complete crc'd message:
    command_as_bytes = crc16.calc_len_and_crc_of(framing_pkt, command_header, command)

    if (1):
        print("- DEV - showing constructed command as human readable bytes:")
        display_packet_as_bytes(command_as_bytes)

    return command_as_bytes



def build_mcuboot_data_packet(data):

    framing_pkt = framing_packet(MCUBOOT_FRAMING_PACKET_TYPE__DATA)

    data_packet_as_bytes = crc16.calc_len_and_crc_of_data_pkt(framing_pkt, data)

    return data_packet_as_bytes





# --- EOF ---
