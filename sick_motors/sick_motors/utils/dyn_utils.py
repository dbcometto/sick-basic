"""Utility functions to use with Dynamixel motors"""

def uint32_to_int32(val):
    """Convert a 32-bit unsigned integer to signed integer"""
    if val > 0x7FFFFFFF:
        val -= 0x100000000
    return val