from vex import *

brain = Brain()
controller = Controller()

left_motor = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)

intake_motor = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
outtake_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
wing_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, False)

color_sensor = Optical(Ports.PORT18)
gps = Gps(Ports.PORT5, 0.0, 0.0, MM, 0)
drivetrain = DriveTrain(left_motor, right_motor, 319.19, 320, 280, MM, 1)

myVariable = 0
x_pos = gps.x_position(MM)
y_pos = gps.y_position(MM)
teamcolor = Color.RED
if teamcolor == Color.RED:
    opponentcolor = Color.BLUE
else:
    opponentcolor = Color.RED

def color_sort():
    global myVariable, opponentcolor, teamcolor
    detected_color = color_sensor.color()
    if detected_color == opponentcolor:
        outtake_motor.spin(FORWARD, 100, PERCENT)
    elif detected_color == teamcolor:
        outtake_motor.spin(REVERSE, 100, PERCENT)
    else:
        outtake_motor.stop()

def color_sort_loop():
    while True:
        color_sort()
        wait(20, MSEC)

def clamp(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value

def normalize_heading(heading):
    heading = heading % 360
    if heading < 0:
        heading += 360
    return heading

def heading_error(target, current):
    return (target - current + 540) % 360 - 180

def turn_to_heading_gps(target_heading, timeout_ms=4000):
    target_heading = normalize_heading(target_heading)
    start_time = brain.timer.time(MSEC)
    while True:
        current_heading = gps.heading()
        error = heading_error(target_heading, current_heading)
        if abs(error) <= 2:
            break
        speed = min(60, max(15, abs(error) * 0.6))
        if error > 0:
            left_motor.spin(FORWARD, speed, PERCENT)
            right_motor.spin(REVERSE, speed, PERCENT)
        else:
            left_motor.spin(REVERSE, speed, PERCENT)
            right_motor.spin(FORWARD, speed, PERCENT)
        if brain.timer.time(MSEC) - start_time > timeout_ms:
            break
        wait(20, MSEC)
    left_motor.stop()
    right_motor.stop()

def when_started():
    global myVariable
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("GPS Calibrating...")
    gps.calibrate()
    while gps.is_calibrating():
        wait(100, MSEC)
    brain.screen.clear_screen()
    wait(1, SECONDS)
    brain.screen.clear_screen()
    brain.screen.print("Ready")

def drive_to_point(target_x, target_y):
    import math
    current_x = gps.x_position(MM)
    current_y = gps.y_position(MM)
    dx = target_x - current_x
    dy = target_y - current_y
    distance = math.sqrt(dx**2 + dy**2)
    if distance < 5:
        return
    target_angle_rad = math.atan2(dx, dy)
    target_heading = math.degrees(target_angle_rad)
    if target_heading < 0:
        target_heading += 360
    turn_to_heading_gps(target_heading)
    drivetrain.drive_for(FORWARD, distance, MM)

def onauton_autonomous_0():
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Autonomous")
    color_sort_task = Thread(color_sort_loop)
    wait(200, MSEC)
    drivetrain.set_drive_velocity(50, PERCENT)
    drivetrain.set_turn_velocity(30, PERCENT)
    start_x = gps.x_position(MM)
    start_y = gps.y_position(MM)
    target_x = start_x + 0
    target_y = start_y + 900
    drive_to_point(target_x, target_y)
    intake_motor.spin(FORWARD, 100, PERCENT)
    brain.screen.print("Auton Complete")
    color_sort_task.stop()

def ondriver_drivercontrol_0():
    global myVariable
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Driver Control")
    drivetrain.set_drive_velocity(100, PERCENT)
    drivetrain.set_turn_velocity(100, PERCENT)
    while True:
        forward = controller.axis3.position()
        turn = controller.axis1.position()
        left_speed = forward + turn
        right_speed = forward - turn
        if abs(left_speed) < 5:
            left_speed = 0
        if abs(right_speed) < 5:
            right_speed = 0
        left_speed = clamp(left_speed, -100, 100)
        right_speed = clamp(right_speed, -100, 100)
        left_motor.spin(FORWARD, left_speed, PERCENT)
        right_motor.spin(FORWARD, right_speed, PERCENT)
        if controller.buttonL2.pressing():
            intake_motor.spin(FORWARD, 100, PERCENT)
        elif controller.buttonL1.pressing():
            intake_motor.spin(REVERSE, 100, PERCENT)
        else:
            intake_motor.stop()
        if controller.buttonR1.pressing():
            outtake_motor.spin(FORWARD, 100, PERCENT)
        elif controller.buttonR2.pressing():
            outtake_motor.spin(REVERSE, 100, PERCENT)
        else:
            color_sort()
        if controller.buttonX.pressing():
            wing_motor.spin(FORWARD, 100, PERCENT)
        elif controller.buttonY.pressing():
            wing_motor.spin(REVERSE, 100, PERCENT)
        else:
            wing_motor.stop()
        wait(20, MSEC)

def vexcode_auton_function():
    auton_task_0 = Thread( onauton_autonomous_0 )
    while( competition.is_autonomous() and competition.is_enabled() ):
        wait( 10, MSEC )
    auton_task_0.stop()

def vexcode_driver_function():
    driver_control_task_0 = Thread( ondriver_drivercontrol_0 )
    while( competition.is_driver_control() and competition.is_enabled() ):
        wait( 10, MSEC )
    driver_control_task_0.stop()

competition = Competition( vexcode_driver_function, vexcode_auton_function )
when_started()
