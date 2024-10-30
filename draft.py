from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from gpiozero import Servo
from gpiozero import Button, LED
import time
import RPi.GPIO as GPIO
     

if __name__ == "__main__":
    
    # print((20/4).is_integer())
    
    # print((20/3).is_integer())
    
    # GPIO.cleanup()
    
    kit = MotorKit()
    
    kit.stepper1.release()
    kit.stepper2.release()
    
    # while True:
    #     kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    #     kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    
    # while True:
    #     kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    #     kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)   
    
    button1 = Button(16) # Final de carrera vertical
    button2 = Button(17) # Final de carrera horizontal
    
    led_1 = LED(20)
    led_2 = LED(21)
    # led_1.on()
    # led_2.on()
    # time.sleep(5)
    
    while True:
        if not button1.is_pressed:
            led_1.on()
            
        elif button1.is_pressed: 
            led_1.off()
            
        if not button2.is_pressed:
            led_2.on()
            
        elif button2.is_pressed: 
            led_2.off()
    
    


# PRUEBA PYGCODE
# from pygcode import *

# kit = MotorKit()

# # Función para mover motores según comando Gcode
# def execute_gcode_command(command):
#     if isinstance(command, GCodeCommandLinearMove):
#         # Interpretar movimiento lineal (G0 o G1)
#         if 'Z' in command:
#             # Mover motor Z (extrusor)
#             z_position = float(command.get_param('Z'))
#             # Tu lógica para mover el motor Z aquí
#         else:
#             # Mover motores X e Y (plotter)
#             x_position = float(command.get_param('X'))
#             y_position = float(command.get_param('Y'))
#             # Tu lógica para mover los motores X e Y aquí
#     # Más lógica para otros comandos Gcode si es necesario

# # Ejemplo de lectura de archivo Gcode
# with open('archivo.gcode', 'r') as file:
#     for line in file:
#         cmd = GCodeParser(line.strip())
#         execute_gcode_command(cmd)



# SENSORES

# button1 = Button(16)
# led1 = LED(20)

# button2 = Button(17)
# led2 = LED(21)



# while True:
#     if not button1.is_pressed:
#         led1.on()
        
#     elif button1.is_pressed: 
#         led1.off()
        
#     if not button2.is_pressed:
#         led2.on()
        
#     elif button2.is_pressed: 
#         led2.off()
    










# MOTORES

# kit = MotorKit()
# servo = Servo(14)

# while True:
#     servo.min()
#     time.sleep(0.1)

#     servo.mid()
#     time.sleep(0.1)
    
# St1 BACKWARD, St2 FORWARD arriba
# St1 FORWARD, St2 BACKWARD abajo
# St1 FORWARD, St2 FORWARD izquierda
# St1 BACKWARD, St2 BACKWARD derecha

# kit.stepper1.release()
# kit.stepper2.release()

# while True:
#     kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
#     kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)