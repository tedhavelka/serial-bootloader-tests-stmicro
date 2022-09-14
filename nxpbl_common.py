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



serialPort = serial.Serial(port = "/dev/ttyUSB0",
                           baudrate=115200,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,   # PARITY_EVEN,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=SERIAL_PORT_READ_TIMEOUT,
                           write_timeout=2.0)



