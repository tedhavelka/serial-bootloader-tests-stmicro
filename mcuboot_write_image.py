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


## - STEP - build, send command, look for initial ACK from bootloader:

    byte_count_to_flash = ( count_pages_to_flash_requested * SIZE_FLASH_PAGE )
    bytes_sent = 0

    present_command = build_mcuboot_command_packet(MCUBOOT_COMMAND_TAG__WRITE_MEMORY,\
      0x00000000, byte_count_to_flash, None, None, None, None, None)

    time.sleep(CHOSEN_DELAY)
    print("- DEV 0921 - sending command ", present_command, ". . .")
    bytes_sent = serialPort.write(present_command)
    if (DIAG_0921):
        print("- DEV 0921 - in-coming data phase command routine just sent", bytes_sent, "bytes")
        print("    sent:", end=" ")
        display_byte_array(present_command)



    count_pages_flashed = 0

    while ( count_pages_flashed < count_pages_to_flash_requested ):
        print("- DEV 1017 - STUB BLOCK FOR DATA WRITING WHILE LOOP")
        count_pages_flashed = count_pages_to_flash_requested


    print("")
