import time
import math
import numpy as np
import RPi.GPIO as GPIO
from gpiozero import Servo
from gpiozero import Button, LED
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from gpiozero.pins.pigpio import PiGPIOFactory
from sshkeyboard import listen_keyboard, stop_listening


class nc_head:
    
    def __init__(self):
        
        pigpio = PiGPIOFactory() # sudo pigpiod - Start the daemon
                
        kit = MotorKit()
        
        self.st1 = kit.stepper1
        self.st2 = kit.stepper2
        
        self.st1.release()
        self.st2.release()
        
        time.sleep(1)
        
        self.servo = Servo(14, pin_factory=pigpio)
        self.button1 = Button(16)
        self.button2 = Button(17)
        
        self.end_travel()
        self.release_steppers()
        self.__calibrate_scales()
        
    def __get_pos_x(self) -> int:
        return self.pos_x
    
    def __get_pos_y(self) -> int:
        return self.pos_y
    
    def __set_pos_x(self, x: int):
        self.pos_x = x
        
    def __set_pos_y(self, y: int):
        self.pos_y = y

    def end_travel(self):
        """Plotter raises the pen and travels to the origin of coordinates, stops and resets the position."""
        
        self.raise_head()
        
        # St1 FORWARD, St2 BACKWARD abajo
        # St1 FORWARD, St2 FORWARD izquierda
        
        st1 = self.st1
        st2 = self.st2
        
        self.release_steppers()
        
        down = False
        left = False
        
        button1 = self.button1 # Final de carrera vertical
        button2 = self.button2 # Final de carrera horizontal
                
        while not down:
            st1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            st2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                    
            if not button1.is_pressed:
                down = True
                
        print("Reached vertical endstop.")    
        
        while not left:
            st1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            st2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                    
            if not button2.is_pressed:
                left = True
            
        print("Reached horizontal endstop.")
                
        self.__set_pos_x(0)
        self.__set_pos_y(0)
        
    def __calibrate_scales(self, x_double = 20, y_double = 20, x_micro = 12, y_micro = 13, scale = "mm"):
        """Calibrate the scales of the plotter in either mm or inches.
Adjust the number of steps in case of a not perfect calibration."""

        x_double_steps = 100
        y_double_steps = 100
        
        x_micro_steps = 1000
        y_micro_steps = 1000
        
        while abs(x_double-y_double) >= 0.01:
            if x_double > y_double:
                y_double += y_double/y_double_steps
                y_double_steps += 1
                
            else:
                x_double += x_double/x_double_steps
                x_double_steps += 1
        
        self.x_double = x_double/x_double_steps
        self.y_double = y_double/y_double_steps
        
        while abs(x_micro-y_micro) >= 0.01:
            if x_micro > y_micro:
                y_micro += y_micro/y_micro_steps
                y_micro_steps += 1
                
            else:
                x_micro += x_micro/x_micro_steps
                x_micro_steps += 1
        
        self.x_micro = x_micro/x_micro_steps
        self.y_micro = y_micro/y_micro_steps
        
        self.scale = scale
        
    def scale_x_y(self):
        """With a given formula, calculate the scale of the plotter."""
        
        self.raise_head()
        self.move_right(200,"D")
        self.lower_head()
        
        time.sleep(1)
        
        # Double Square
        self.move_right(100, "D")
        self.move_up(100, "D")
        self.move_left(100, "D")
        self.move_down(100, "D")
        
        time.sleep(1)
        
        self.raise_head()
        self.move_right(200,"D")
        self.lower_head()
        
        time.sleep(1)
        
        # Micro square
        self.move_right(1000, "M")
        self.move_up(1000, "M")
        self.move_left(1000, "M")
        self.move_down(1000, "M")
        
        time.sleep(1)
        
        self.end_travel()
        
        scale = ["mm", "inch"]
        scale_used = ""
        
        while scale_used not in scale: # Parameters for calibration
            scale_used = input("Enter the scale used (mm or inch): ").lower().replace(" ", "")
        
        x_double = input(f"Enter the x-axis distance in {scale_used} for the double step: ")
        y_double = input(f"Enter the y-axis distance in {scale_used} for the double step: ")
        
        x_micro = input(f"Enter the x-axis distance in {scale_used} for the microstep: ")
        y_micro = input(f"Enter the y-axis distance in {scale_used} for the microstep: ")
        
        self.__calibrate_scales(int(x_double), int(y_double), int(x_micro), int(y_micro), scale_used) 
        
    def __calculate_steps(self, x:int, y:int) -> tuple[int, int]:
        """Calculate the number of steps needed to move the plotter a certain distance."""
        
        return (int(x/self.x_double), int(y/self.y_double))
        
    def release_steppers(self):
        self.st1.release()
        self.st2.release()
        
    def raise_head(self):        
        self.servo.value = -0.8
        
    def lower_head(self):        
        self.servo.value = 0.2
        
    def absolute_move(self, x: int, y: int):
        """Plotter moves to the absolute position (x, y)."""
        
        pos_x = self.__get_pos_x()
        pos_y = self.__get_pos_y()
        
        dx, dy = self.__calculate_steps(x-pos_x, y-pos_y)
        
        if dx > 0:
            self.move_right(dx, "D")
            
        elif dx < 0:
            self.move_left(-dx, "D")
            
        if dy > 0:
            self.move_up(dy, "D")
            
        elif dy < 0:
            self.move_down(-dy, "D")
            
        self.__set_pos_x(x)
        self.__set_pos_y(y)
        
    def relative_move(self, rel_x: int, rel_y: int):
        """Plotter moves to the relative position (rel_x, rel_y)."""
        
        pos_x = self.__get_pos_x()
        pos_y = self.__get_pos_y()
        
        x = pos_x + rel_x
        y = pos_y + rel_y
        
        self.absolute_move(x, y)
        
    def move_up(self, steps: int, type:str): # Up steps
        """Move the plotter up by the number of steps."""
        
        st1 = self.st1
        st2 = self.st2
        
        if type == "D":
            type = stepper.DOUBLE   
            
        elif type == "M":
            type = stepper.MICROSTEP    
        
        for _ in range(steps):
            st1.onestep(direction=stepper.BACKWARD, style=type)
            st2.onestep(direction=stepper.FORWARD, style=type)
                        
    def move_down(self, steps: int, type:str): # Down steps
        """Move the plotter down by the number of steps."""
        
        st1 = self.st1
        st2 = self.st2
        
        if type == "D":
            type = stepper.DOUBLE
            
        elif type == "M":
            type = stepper.MICROSTEP
        
        for _ in range(steps):
            st1.onestep(direction=stepper.FORWARD, style=type)
            st2.onestep(direction=stepper.BACKWARD, style=type)
                        
    def move_left(self, steps: int, type:str): # Left steps
        """Move the plotter to the left by the number of steps."""
        
        st1 = self.st1
        st2 = self.st2
        
        if type == "D":
            type = stepper.DOUBLE
            
        elif type == "M":
            type = stepper.MICROSTEP
        
        for _ in range(steps):
            st1.onestep(direction=stepper.FORWARD, style=type)
            st2.onestep(direction=stepper.FORWARD, style=type)
                        
    def move_right(self, steps: int, type:str): # Right steps
        """Move the plotter to the right by the number of steps."""
        
        st1 = self.st1
        st2 = self.st2
        
        if type == "D": 
            type = stepper.DOUBLE
            
        elif type == "M":
            type = stepper.MICROSTEP
        
        for _ in range(steps): 
            st1.onestep(direction=stepper.BACKWARD, style=type)
            st2.onestep(direction=stepper.BACKWARD, style=type)
                    
    def helix_clockwise(self, x: int, y: int, i: int, j: int):
        """Moves the plotter along a helical clockwise path"""
        
        # Center and radio of the helix
        cx = x + i
        cy = y + j
        r = math.sqrt(i**2 + j**2)
        
        # Start and end angles of the arc
        theta1 = math.atan2(-j, -i)
        theta2 = math.atan2(y - cy, x - cx)
        if theta2 < theta1:
            theta2 += 2*math.pi
       
        increment = 0.05
        arc_points = []
        
        for theta in np.arange(theta1, theta2, increment): # Generate points along the arc
            Px = cx + r * math.cos(theta)
            Py = cy + r * math.sin(theta)
            arc_points.append((Px, Py))
        
        for point in arc_points: # Move plotter to pos
            self.absolute_move(point[0], point[1])
            
    def helix_counter(self, x: int, y: int, i: int, j: int):
        """Moves the plotter along a helical counter clockwise path"""
                
        # Center and radio of the helix
        cx = x + i
        cy = y + j
        r = math.sqrt(i**2 + j**2)
        
        # Start and end angles of the arc
        theta1 = math.atan2(-j, -i)
        theta2 = math.atan2(y - cy, x - cx)
        if theta2 > theta1:
            theta2 -= 2*math.pi
        
        increment = 0.05  
        
        arc_points = []
        
        for theta in np.arange(theta1, theta2, increment): # Generate points along the arc
            px = cx + r * math.cos(theta)
            py = cy + r * math.sin(theta)
            arc_points.append((px, py))
        
        for point in arc_points: # Move plotter to pos
            self.absolute_move(point[0], point[1])
            
    def __press(self, key):
        
        if key == "up":
            self.move_up(5, "D")
            self.__set_pos_y(self.__get_pos_y() + 4*self.y_double)
            
        elif key == "down":
            self.move_down(5, "D")
            self.__set_pos_y(self.__get_pos_y() - 4*self.y_double)
            
        elif key == "left":
            self.move_left(5, "D")
            self.__set_pos_x(self.__get_pos_x() - 4*self.x_double)
            
        elif key == "right":
            self.move_right(5, "D")
            self.__set_pos_x(self.__get_pos_x() + 4*self.x_double)
            
        elif key == "space":
            self.raise_head()
            
        elif key == "enter":
            self.lower_head()
            
        print("key pressed: ", key)
            
    def __not_pressed(self, key):
        
        if key == "e":
            
            self.__set_pos_x(int(self.__get_pos_x()))
            self.__set_pos_y(int(self.__get_pos_y()))
            stop_listening()
            
    def manual_control(self):
        """Positionates the plotter and the height of the pen manually."""
        
        print("""
============== MANUAL CONTROL ==============

    Arrow Up: Move up
    Arrow Down: Move down
    Arrow Left: Move left
    Arrow Right: Move right
    Space: Raise pen
    Enter: Lower pen
    E: Exit manual mode
    
============================================""")
        
        listen_keyboard(
            on_press = self.__press,
            on_release = self.__not_pressed,
            delay_second_char = 0.001, # Long press detection
            delay_other_chars= 0.001)
            
        print("Exiting manual control mode...\n")
        
if __name__ == "__main__":
    plotter = nc_head()
    plotter.scale_x_y()