# ----------------------------------------------------------------------------
#                                                                            
#    Project: 43389C Box Bot                                 
#    Author:  Canadian Academy Robotics Team
#    Created: 2026/01/18
#    Last updated: 2026/01/18
#    Version: 1.0.0
#    Description: 
#                   
#    Configuration: 
#                   
#                                                                           
# ----------------------------------------------------------------------------

from vex import *

brain = Brain()
controller = Controller()

# ============================================================================ #
#                           MOTOR CONFIGURATION                                #
# ============================================================================ #

# Drive motors 
left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)

# Additional motors 
intake_motor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)

# SmartDrive with GPS
drivetrain = SmartDrive(left_motor, right_motor, gps, 319.19, 320, 280, MM, 1)

# ============================================================================ #
#                          SENSOR CONFIGURATION                                #
# ============================================================================ #

# Color sensor
color_sensor = Optical(Ports.PORT5)

# GPS sensor
gps = Gps(Ports.PORT6)

# ============================================================================ #
#                            GLOBAL VARIABLES                                  #
# ============================================================================ #

myVariable = 0
x_pos = gps.x_position(MM)
y_pos = gps.y_position(MM)

# ============================================================================ #
#                           WHEN STARTED                                       #
# ============================================================================ #

def when_started():
    global myVariable
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Ready to start")
    gps.calibrate()


# ============================================================================ #
#                            AUTONOMOUS                                        #
# ============================================================================ #

def onauton_autonomous_0():
    global myVariable,x_pos,y_pos
    
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Autonomous")
    

    # ===== AUTONOMOUS CODE===== #
    drivetrain.drive_for(FORWARD, 24, INCHES, 50, PERCENT)
    drivetrain.turn_to_heading(90, DEGREES, 30, PERCENT)
    
    if color_sensor.color() == Color.RED:
        brain.screen.print("Red detected!")
    pass


# ============================================================================ #
#                          DRIVER CONTROL                                      #
# ============================================================================ #

def ondriver_drivercontrol_0():
    global myVariable
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Driver Control")
    
    # Set drivetrain velocities
    drivetrain.set_drive_velocity(100, PERCENT)
    drivetrain.set_turn_velocity(100, PERCENT)
    
    while True:
        # ===== DRIVETRAIN CONTROL (Arcade Drive) ===== #
        forward = controller.axis3.position()
        turn = controller.axis1.position()
        
        # Calculate left and right motor speeds
        left_speed = forward + turn
        right_speed = forward - turn
        
        # Deadband to prevent drift
        if abs(left_speed) < 5:
            left_speed = 0
        if abs(right_speed) < 5:
            right_speed = 0
        
        left_motor.spin(FORWARD, left_speed, PERCENT)
        right_motor.spin(FORWARD, right_speed, PERCENT)
        

        if controller.buttonR1.pressing():
             intake_motor.spin(FORWARD, 100, PERCENT)
        elif controller.buttonR2.pressing():
             intake_motor.spin(REVERSE, 100, PERCENT)
        else:
            intake_motor.stop()
        


# ============================================================================ #
#                      COMPETITION CONTROL FUNCTIONS                           #
# ============================================================================ #

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


# ============================================================================ #
#                              MAIN                                            #
# ============================================================================ #

comp = Competition( vexcode_driver_function, vexcode_auton_function )
when_started()
