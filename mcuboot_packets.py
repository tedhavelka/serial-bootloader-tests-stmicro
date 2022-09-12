#
# ----------------------------------------------------------------------
#  @brief  Part of nxpbl.py project, simple python work to
#          exercise and learn about NXP's MCU bootloader built
#          into many NXP 32-bit microcontrollers
#
# @references
#
#   *  MCUBOOTRM.pdf
#
#   *  https://www.geeksforgeeks.org/user-defined-data-structures-in-python/
#
# ----------------------------------------------------------------------
#


from bootloader_nxp_tags import *



COMMAND_HEADER_BYTE_COUNT = 4
SIZE_INT32 = 4



## Define MCUBoot framing packet, command packet, command header,
##  ( later possibly define "response packet", but may not be needed - TMH )

## MCUBOOTRM.pdf section 4.4:

class framing_packet:
    def __init__(self, packet_type):
        self.start_byte = MCUBOOT_BOOTLOADER_START_BYTE
        self.packet_type = packet_type
        self.length_low = 0x00
        self.length_high = 0x00
        self.crc16_low = 0x00
        self.crc16_high = 0x00
# Note a framining packet may wrap a command packet, a response packet, or no packet in a ping response:
        self.payload = None


class command_packet_header:
    def __init__(self, command_tag):
        self.command_or_response_tag = command_tag
        self.flags                   = 0x00 & 0xFF
        self.reserved                = 0x00 & 0xFF
        self.parameter_count         = 0x00 & 0xFF


class command_packet:
    def __init__(self, packet_header):
        self.header = packet_header
# Note command packet parameters for bootloader vary from zero to seven 32-bit integers:
        self.parameters = None



## ---------------------------------------------------------------------
## - SECTION - routines
## ---------------------------------------------------------------------

def display_framing_packet(packet):
    print("present framing packet holds")
    print("start byte:  0x%02x" % packet.start_byte)
    print("packet type: 0x%02x" % packet.packet_type)
    print("length low:  0x%02x" % packet.length_low)
    print("length high: 0x%02x" % packet.length_high)
    print("crc16 low:   0x%02x" % packet.crc16_low)
    print("crc16 high:  0x%02x" % packet.crc16_high)


def display_command_packet(packet):
    print("preset command packet holds")
    print("command or response tag:  0x%02x" % packet.header.command_or_response_tag)
    print("                  flags:  0x%02x" % packet.header.flags)
    print("               reserved:  0x%02x" % packet.header.reserved)
    print("        parameter count:  0x%02x" % packet.header.parameter_count)

    if (packet.parameters != None):
        print("- WIP 0911 - command packet has parameters . . .")
        print("present command carries", end=" ")
        print("%u " % (len(packet.parameters)), end=" ")
        print("parameters.")

        for i in range(len(packet.parameters)):
            print("0x%08X" % packet.parameters[i])




# --- EOF ---
