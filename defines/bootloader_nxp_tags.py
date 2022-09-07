## @brief This file part of NXP bootloader testing script named nxpbl.py
##
## Reference https://docs.python.org/3/tutorial/modules.html



NXP_COMMAND_TAG__FLASH_ERASE_ALL      = 0x00
NXP_COMMAND_TAG__FLASH_ERASE_REGION   = 0x01
#NXP_COMMAND_TAG__

NXP_RESPONSE_TAG__GENERIC             = 0xA0
NXP_RESPONSE_TAG__GET_PROPERTY        = 0xA0
NXP_RESPONSE_TAG__READ_MEMORY         = 0xA3
NXP_RESPONSE_TAG__FLASH_READ_ONCE     = 0xAF
NXP_RESPONSE_TAG__FLASH_READ_RESOURCE = 0xB0



def function_as_placeholder():
    print("trivial function for included python file holding NXP bootloader constants.")

