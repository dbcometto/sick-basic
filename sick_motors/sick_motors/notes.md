You can send a single motor command using

```bash
ros2 topic pub --once /dyn_command sick_interface/msg/MotorPositionCommand "{header: {stamp: now, frame_id: ''}, motor_id: 2, goal_position: 3000}"
```