#
# ----------------------------------------------------------------------
#  @brief  Part of nxpbl.py project, simple python work to
#          exercise and learn about NXP's MCU bootloader built
#          into many NXP 32-bit microcontrollers
# ----------------------------------------------------------------------
#

import numpy as np

from mcuboot_packets import *



## ---------------------------------------------------------------------
##  @brief Following routine calculates sixteen bit CRC per xmodem
##         variant definition, as described in NXP's MCUBOOTRM.pdf
##         document.
##
##  @note  Due to NXP's bootloader firmware embedding CRC in middle
##         of message or data packets, this routine designed to take
##         an arbitrary starting point value for CRC.  First time called
##         most callers will want to send zero, '0' in as value in
##         final parameter.
##
##  @ref   https://docs.python.org/3/tutorial/controlflow.html
## ---------------------------------------------------------------------

def calc_crc16_with_carry_in(byte_array_to_check, crc_from_caller):

    crc = int(crc_from_caller)
    j = 0                        # local loop index
    temp = 0

    for j in range(len(byte_array_to_check)):  # we may not need byte_count in parameter list - TMH

        i = 0
        byte = byte_array_to_check[j]
        crc ^= ((byte_array_to_check[j]) << 8)

        for i in range(8):

#            print(byte_array_to_check[j], end=" temp: ")
#            print(temp, end=" crc: ")
#            print(crc)
            temp = crc << 1
#            print("- DEV - about to xor present crc with value %d" % ((byte_array_to_check[j]) << 8) )
            if (crc & 0x8000):
                temp ^= 0x1021

            crc = temp

    crc &= 0xFFFF                  # this routine a 16-bit CRC calculator so mask answer to 16 bits.
    print("returning 0x%04x" % crc)
    return crc



def bytes_of_framing_packet(framing_packet):
    bytes = [0, 0, 0, 0]
    bytes[0] = framing_packet.start_byte
    bytes[1] = framing_packet.packet_type
    bytes[2] = framing_packet.length_low
    bytes[3] = framing_packet.length_high

# Note we skip returning the crc bytes per MCUBOOTRM.pdf, section 4.4 page 33
#    bytes[3] = framing_packet.crc16_low
#    bytes[3] = framing_packet.crc16_high
    return bytes



def bytes_of_command_packet(command_hdr, command_pkt):

    bytes = [0, 0, 0, 0]
    bytes[0] = command_hdr.command_or_response_tag
    bytes[1] = command_hdr.flags
    bytes[2] = command_hdr.reserved
    bytes[3] = command_hdr.parameter_count

    if (len(command_pkt.parameters) > 0):
        print("routine 'bytes_of_command_packet' finds %u" % len(command_pkt.parameters), end=" ")
        print("parameters with present command.")

        for i in range(len(command_pkt.parameters)):
            bytes.append((command_pkt.parameters[i] & 0x000000ff))
            bytes.append((command_pkt.parameters[i] & 0x0000ff00) >> 8)
            bytes.append((command_pkt.parameters[i] & 0x00ff0000) >> 16)
            bytes.append((command_pkt.parameters[i] & 0xff000000) >> 24)
    else:
        print("INFO - encountered command packet with no parameters.")

    return bytes



def calc_len_and_crc_of(framing_pkt, command_hdr, command_pkt):

    command_length = COMMAND_HEADER_BYTE_COUNT + (SIZE_INT32 * len(command_pkt.parameters))
    framing_pkt.length_low = command_length & 0x00FF
    framing_pkt.length_high = command_length & 0xFF00

    framing_bytes = bytes_of_framing_packet(framing_pkt)
    command_bytes = bytes_of_command_packet(command_hdr, command_pkt)

    crc_framing = calc_crc16_with_carry_in(framing_bytes, 0)

    crc_command = calc_crc16_with_carry_in(command_bytes, crc_framing)

    print("present command has length %u" % command_length, end=" ")
    print("bytes,")
    print("present framing and command packets give crc of 0x%04x" % crc_command, end=" ")
    print("bytes.")

## WIP - building up to assign command length and packet CRC to framing packet



# --- EOF ---
