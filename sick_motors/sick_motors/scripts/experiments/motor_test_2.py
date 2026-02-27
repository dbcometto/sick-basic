import time
import numpy as np


import sick_motors.utils.dynamixel_sdk as dynamixel
from sick_motors.utils.dyn_xl430 import XL430W250T
import sick_motors.utils.dyn_utils as dyn_utils




def observe(length=2,period=0.5):
    k = int(length/period)
    for i in range(k):
        time.sleep(period)
        position, error, result = packet.read4ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.PRESENT_POSITION)
        position2, error, result = packet.read4ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.PRESENT_POSITION)
        print(f"Position1: {dyn_utils.uint32_to_int32(position)} | Position2: {dyn_utils.uint32_to_int32(position2)}")






# Initialize port and packet handler
port = dynamixel.PortHandler('/dev/ttyUSB0')
packet = dynamixel.PacketHandler(2.0)  # protocol version 2.0

port.openPort()
port.setBaudRate(57600)


dxl_id = 1
dxl_id2 = 2


packet.write1ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.TORQUE_ENABLE, 0)
packet.write1ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.TORQUE_ENABLE, 0)

# Ensure operating mode
packet.write1ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.OPERATING_MODE, XL430W250T.OPERATING_MODE.EXTENDED_POSITION_CONTROL)
packet.write1ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.OPERATING_MODE, XL430W250T.OPERATING_MODE.EXTENDED_POSITION_CONTROL)


# Set controller gains
packet.write2ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.POSITION_P_GAIN, 800)
packet.write2ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.POSITION_I_GAIN, 0)
packet.write2ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.POSITION_D_GAIN, 0)

packet.write2ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.POSITION_P_GAIN, 800)
packet.write2ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.POSITION_I_GAIN, 0)
packet.write2ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.POSITION_D_GAIN, 0)

# Enable torque
packet.write1ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.TORQUE_ENABLE, 1)
packet.write1ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.TORQUE_ENABLE, 1)

# Move motor to position 512
packet.write4ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.GOAL_POSITION, 5000)
packet.write4ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.GOAL_POSITION, 5000)

# Read back current position
observe(2.2,0.05)

# Move motor to position 512
packet.write4ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.GOAL_POSITION, 0)
packet.write4ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.GOAL_POSITION, 0)

# Read back current position
observe(2.2,0.05)
    


packet.write1ByteTxRx(port, dxl_id, XL430W250T.ADDRESS.TORQUE_ENABLE, 0)
packet.write1ByteTxRx(port, dxl_id2, XL430W250T.ADDRESS.TORQUE_ENABLE, 0)




