import sick_motors.utils.dynamixel_sdk as dynamixel  # Uses the modern SDK
import time
import numpy as np

def observe(length=2,period=0.5):
    k = int(length/period)
    for i in range(k):
        time.sleep(period)
        position, error, result = packet.read4ByteTxRx(port, dxl_id, ADDR_PRESENT_POSITION)
        if result != 0:
            print("Read failed")
        else:
            print("Position:", uint32_to_int32(position))

def uint32_to_int32(val):
    """Convert a 32-bit unsigned integer to signed integer"""
    if val > 0x7FFFFFFF:
        val -= 0x100000000
    return val

# Initialize port and packet handler
port = dynamixel.PortHandler('/dev/ttyUSB0')
packet = dynamixel.PacketHandler(2.0)  # protocol version 2.0

port.openPort()
port.setBaudRate(57600)

dxl_id = 1

ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_OPERATING_MODE = 11


ADDR_POSITION_P_GAIN = 84
ADDR_POSITION_I_GAIN = 82
ADDR_POSITION_D_GAIN = 80

MODE_POSITION_CONTROL = 3
MODE_EXTENDED_POSITION_CONTROL = 4
# Ensure operating mode
packet.write1ByteTxRx(port, dxl_id, ADDR_OPERATING_MODE, MODE_EXTENDED_POSITION_CONTROL)


# Set controller gains
packet.write2ByteTxRx(port, dxl_id, ADDR_POSITION_P_GAIN, 800)
packet.write2ByteTxRx(port, dxl_id, ADDR_POSITION_I_GAIN, 0)
packet.write2ByteTxRx(port, dxl_id, ADDR_POSITION_D_GAIN, 0)

# Enable torque
packet.write1ByteTxRx(port, dxl_id, ADDR_TORQUE_ENABLE, 1)

# Move motor to position 512
packet.write4ByteTxRx(port, dxl_id, ADDR_GOAL_POSITION, 5000)

# Read back current position
observe(2.2,0.05)

# Move motor to position 512
packet.write4ByteTxRx(port, dxl_id, ADDR_GOAL_POSITION, 1)

# Read back current position
observe(2.2,0.05)
    

# Enable torque
packet.write1ByteTxRx(port, dxl_id, ADDR_TORQUE_ENABLE, 0)

port.closePort()