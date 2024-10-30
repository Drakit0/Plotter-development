import os
import random
import time
import RPi.GPIO as GPIO
from gpiozero import Button
from plotter_controller import nc_head

def control_menu():
    print("""========== MENU ==========
             
    1. Travel to original (0,0).
    2. Load Gcode file.
    3. Start plotting. (Pulsing GPIO07 while plotting would stop the plotter instantly.)
    4. Set (0,0).
    5. Manual controll.
    6. Release steppers.
    7. Exit.
    
==========================
""")
    
def number_verify(number:str) -> int:
    """Verify that the input is a number"""
    
    egg = 0
    
    while number.isdigit() == False:
        number = input("Please enter a whole positive number: ").replace(" ", "") # Wrong format
        egg += 1
        
        if random.randint(1,10) == 5 or egg == 10:
            print("\nOh boy, this is already hard enough for you to introduce functions that have not been introduced.\n")
            
            if random.randint(1,2) == 2:
                print("McFLY! You bozo! Those boards don't work on water! Unless you've got power!")
            
            egg = 0
            
    return int(number)

def gcode_extract(file_path)-> list[tuple[str,list[tuple[str,float]]]]:
    """Extracts the gcode from a file and returns it as a dictionary.
    Example 1:
    G02 X33.368673 Y196.749027 Z-0.125000 I-1.898421 J0.347936
    returns {\"G2\":[(X,33.36), (Y,196.75), (Z,-0.125), (I,-1.898), (J,0.347)]}

    Example 2:
    G01 X33.303860 Y197.491653 Z-0.125000 F400.000000
    returns {\"G1\":[(X,33.30), (Y,197.49), (Z,-0.125), (F,400.0)]}"""
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    gcode = []

    for line in lines[1:]:
        line = line.split(" ")
        
        gcode.append((line[0].replace("0",""),[(i[0],float(i[1:].replace("(Penetrate)",""))) for i in line[1:]])) # Extracts the gcode and converts it to a tuple
                
    return gcode


if __name__ == "__main__":
    
    GPIO.cleanup()
    
    plotter = nc_head()
    
    # stop_button = Button(7)
    
    working = True
    
    gcode = {}
    
    print("Welcome to the plotter controlling program.\n")
    
    while working:
        
        control_menu()
        choice = input("Please enter the number of the desired option: ").replace(" ", "")
        
        if choice == "1": # Travel to original(0,0).
            plotter.end_travel()
            
        elif choice == "2":
            shared_documents = os.listdir("shared_documents")
            print("Available documents to plot:\n", shared_documents)
            
            file_path = input("Please enter the path of the file with the \".txt\" extension: ").replace(" ", "")

            if file_path in shared_documents:
                gcode = gcode_extract( "shared_documents/"+ file_path)
                print("File loaded successfully.")
                
            else:
                print("Dummy is still on fire controll, doesn't know what to do with the file.")
            
        elif choice == "3":
            if gcode != {}:
                for instruction in gcode:
                    
                    method = instruction[0]
                    directions = [i[0] for i in instruction[1]]
                    quantities = [i[1] for i in instruction[1]]
                    
                    if method == "G": 
                        
                        if len(quantities) == 2: # Fast movement
                            plotter.raise_head()
                            plotter.absolute_move(quantities[0], quantities[1])
                            
                        else: # Return to (0,0)
                            plotter.end_travel()
                    
                    elif method == "G1": # Linear movement
                        
                        if "Z" in directions:
                            if quantities[directions.index("Z")] < 0:
                                plotter.lower_head()
                                
                            else:
                                plotter.raise_head()
                        
                        if "X" in directions and "Y" in directions:
                            plotter.absolute_move(quantities[0], quantities[1])
                            
                    elif method == "G2": # Helix clockwise
                        
                        if "Z" in directions:
                            if quantities[directions.index("Z")] < 0:
                                plotter.lower_head()
                                
                            else:
                                plotter.raise_head()
                        
                        plotter.helix_clockwise(quantities[0], quantities[1], quantities[3], quantities[4])
                        
                    elif method == "G3": # Helix counterclockwise
                        
                        if "Z" in directions:
                            if quantities[directions.index("Z")] < 0:
                                plotter.lower_head()
                                
                            else:
                                plotter.raise_head()
                                
                        plotter.helix_counter(quantities[0], quantities[1], quantities[3], quantities[4])
                        
                    elif method == "G91": # Relative positioning
                        
                        if "Z" in directions:
                            if quantities[directions.index("Z")] < 0:
                                plotter.lower_head()
                                
                            else:
                                plotter.raise_head()
                        
                        if "X" in directions and "Y" in directions:
                            plotter.relative_move(quantities[0], quantities[1])
                            
                    # if stop_button.is_pressed:
                    #     print("Emergency stop activated.")
                    #     plotter.end_travel()
                    #     break
                            
            else:
                print("No file uploaded.")
            
        elif choice == "4": # Set (0,0)
            plotter.__set_pos_x(0)
            plotter.__set_pos_y(0)
            
        elif choice == "5": # Manual control
            plotter.manual_control()
            
        elif choice == "6": # Exit
            plotter.release_steppers()
            
        elif choice == "7": # Exit
            plotter.end_travel()
            
            working = False
            
    print("\n Thankyou for using the plotter controlling program.\n")
    
    GPIO.cleanup()
    
    plotter.release_steppers()