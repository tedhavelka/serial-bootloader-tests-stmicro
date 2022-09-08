import numpy as np

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

#def calc_crc16_with_carry_in(byte_array_to_check, byte_count, crc_from_caller):
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

