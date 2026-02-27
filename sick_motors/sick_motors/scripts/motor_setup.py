"""A script to write a Dynamixel motor's ID"""

import sick_motors.utils.dynamixel_sdk as dynamixel
from sick_motors.utils.dyn_xl430 import XL430W250T


# Initialize port and packet handler
port = dynamixel.PortHandler('/dev/ttyUSB0')
packet = dynamixel.PacketHandler(2.0)  # protocol version 2.0

port.openPort()
port.setBaudRate(57600)


current_id = 1
new_id = 2


# Script

packet.write1ByteTxRx(port, current_id, XL430W250T.ADDRESS.LED, 1)
input(f"Motor is highlighted, press enter to overwrite current id {current_id} with {new_id}")


packet.write1ByteTxRx(port, current_id, XL430W250T.ADDRESS.ID, new_id)
check_id = packet.read1ByteTxRx(port, new_id, XL430W250T.ADDRESS.ID)
packet.write1ByteTxRx(port, new_id, XL430W250T.ADDRESS.LED, 0)
print(f"New ID is {check_id[0]} after writing {new_id}, and the LED should be off")

