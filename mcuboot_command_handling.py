


# ----------------------------------------------------------------------
#  @brief  This routine sees an mcuboot command through via these steps:
#
#    (1)  send command bytes over UART
#    (2)  capture response byte stream
#    (3)  search for 'ACK' pattern in first two bytes of response,
#           error out if not found
#    (4)  search for generic response, typically eighteen bytes long
#    (5)  calc and check CRC in generic response,
#           error out when CRC incorrect
#    (6)  send an 'ACK'
#
# ----------------------------------------------------------------------

def to_see_command_through(cmd):

    bytes_sent = 0
    command_status = 0
    expected_responses_received = 0

    time.sleep(CHOSEN_DELAY)
    bytes_sent = serialPort.write(cmd)
    print("seeing command through, just sent", bytes_sent, "bytes")

#    while(expected_responses_received == 0):
#        listen_for_response(...)


    return command_status

