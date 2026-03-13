from enum import IntEnum
from numpy import pi

class XL430W250T():

    POSITIONS_PER_REVOLUTION = 4096
    ANGLE_PER_POSITION = 2*pi/POSITIONS_PER_REVOLUTION
    

    class ADDRESS(IntEnum):
        # ===== EEPROM AREA =====
        MODEL_NUMBER = 0                 # 2 bytes
        MODEL_INFORMATION = 2            # 4 bytes
        FIRMWARE_VERSION = 6             # 1 byte
        ID = 7                           # 1 byte
        BAUD_RATE = 8                    # 1 byte
        RETURN_DELAY_TIME = 9            # 1 byte
        DRIVE_MODE = 10                  # 1 byte
        OPERATING_MODE = 11              # 1 byte
        SECONDARY_ID = 12                # 1 byte
        PROTOCOL_VERSION = 13            # 1 byte
        HOMING_OFFSET = 20               # 4 bytes
        MOVING_THRESHOLD = 24            # 4 bytes
        TEMPERATURE_LIMIT = 31           # 1 byte
        MAX_VOLTAGE_LIMIT = 32           # 2 bytes
        MIN_VOLTAGE_LIMIT = 34           # 2 bytes
        PWM_LIMIT = 36                   # 2 bytes
        CURRENT_LIMIT = 38               # 2 bytes
        VELOCITY_LIMIT = 44              # 4 bytes
        MAX_POSITION_LIMIT = 48          # 4 bytes
        MIN_POSITION_LIMIT = 52          # 4 bytes
        SHUTDOWN = 63                    # 1 byte

        # ===== RAM AREA =====
        TORQUE_ENABLE = 64               # 1 byte
        LED = 65                         # 1 byte
        STATUS_RETURN_LEVEL = 68         # 1 byte
        REGISTERED_INSTRUCTION = 69      # 1 byte
        HARDWARE_ERROR_STATUS = 70       # 1 byte
        VELOCITY_I_GAIN = 76             # 2 bytes
        VELOCITY_P_GAIN = 78             # 2 bytes
        POSITION_D_GAIN = 80             # 2 bytes
        POSITION_I_GAIN = 82             # 2 bytes
        POSITION_P_GAIN = 84             # 2 bytes
        FEEDFORWARD_2ND_GAIN = 88        # 2 bytes
        FEEDFORWARD_1ST_GAIN = 90        # 2 bytes
        BUS_WATCHDOG = 98                # 1 byte
        GOAL_PWM = 100                   # 2 bytes
        GOAL_CURRENT = 102               # 2 bytes
        GOAL_VELOCITY = 104              # 4 bytes
        PROFILE_ACCELERATION = 108       # 4 bytes
        PROFILE_VELOCITY = 112           # 4 bytes
        GOAL_POSITION = 116              # 4 bytes
        REALTIME_TICK = 120              # 2 bytes
        MOVING = 122                     # 1 byte
        MOVING_STATUS = 123              # 1 byte
        PRESENT_PWM = 124                # 2 bytes
        PRESENT_CURRENT = 126            # 2 bytes
        PRESENT_VELOCITY = 128           # 4 bytes
        PRESENT_POSITION = 132           # 4 bytes
        VELOCITY_TRAJECTORY = 136        # 4 bytes
        POSITION_TRAJECTORY = 140        # 4 bytes
        PRESENT_INPUT_VOLTAGE = 144      # 2 bytes
        PRESENT_TEMPERATURE = 146        # 1 byte



    class OPERATING_MODE(IntEnum):
        VELOCITY_CONTROL = 1
        POSITION_CONTROL = 3
        EXTENDED_POSITION_CONTROL = 4
        PWM_CONTROL = 16