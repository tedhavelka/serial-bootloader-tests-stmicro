import serial



ONE_NANOSECOND           = 0.000000001
ONE_MICROSECOND          = 0.000001
TEN_MICROSECONDS         = 0.00001
ONE_HUNDRED_MICROSECONDS = 0.0001

#CHOSEN_DELAY = ONE_HUNDRED_MICROSECONDS
#CHOSEN_DELAY = TEN_MICROSECONDS
CHOSEN_DELAY = ONE_NANOSECOND

SERIAL_PORT_READ_TIMEOUT = 0.00004340 # in seconds . . . was 1.0 seconds

DISPLAY_BYTE_PER_LINE = 1
DISPLAY_PACKET_PER_LINE = 2



# 2022-09-15 - trying slower baud rates, started out at 115200 . . .

serialPort = serial.Serial(port = "/dev/ttyUSB0",
#serialPort = serial.Serial(port = "/dev/ttyUSB4",
#                           baudrate=115200,
                           baudrate=38400,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,   # PARITY_EVEN,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=SERIAL_PORT_READ_TIMEOUT,
                           write_timeout=2.0)



NXPBL_RETURN_VALUES__FIRST_ENTRY = 1
NXPBL_ROUTINE_OK                       = NXPBL_RETURN_VALUES__FIRST_ENTRY + 1
COMMAND_PROCESSING_OK                  = NXPBL_ROUTINE_OK + 1
ERROR__COMMAND__UNEXPECTED_PACKET_TYPE = COMMAND_PROCESSING_OK + 1



##----------------------------------------------------------------------
## - SECTION - routines
##----------------------------------------------------------------------


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

        if (type(data[0] is int)):
            i = 0
            for i in range(len(data)):
                print("%02X" % data[i], end=" ")
                if(i > 0):
                    if(((i + 1) % 8) == 0):
                        print(" ", end=" ")
                    if(((i + 1) % 16) == 0):
                        print(" ")

#        if 0: ### type of data[0] seems to test true for both Python type 'int' and 'bytes' - TMH
#        if (type(data[0] is bytes)):
#            i = 0
#            for i in range(len(data)):
#                print("%02X" % int.from_bytes(data[i], "little"), end=" ")
#                if(i > 0):
#                    if(((i + 1) % 8) == 0):
#                        print(" ", end=" ")
#                    if(((i + 1) % 16) == 0):
#                        print(" ")

        else:
            print("--- WARNING! --- list data to show has elements not of type 'int'")

    print("")



## --- EOF ---
