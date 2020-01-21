#
# This file is part of GreatFET
#

from enum import IntEnum

import bitstruct

class ChipStatus_State(IntEnum):
    IDLE             = 0b00
    RX               = 0b001
    TX               = 0b010
    FSTXON           = 0b011
    CALIBRATE        = 0b100
    SETTLING         = 0b101
    RXFIFO_OVERFLOW  = 0b110
    TXFIFO_UNDERFLOW = 0b111

class ChipId(IntEnum):
    CC1110 = 0x01
    CC2430 = 0x85
    CC2431 = 0x89
    CC2510 = 0x81
    CC2511 = 0x91

def decode_chip_status_byte(status):
    chip_ready, state, fifo_bytes_available = bitstruct.unpack('u1u3u4', status)
    return chip_ready, state, fifo_bytes_available
