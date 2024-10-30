from sshkeyboard import listen_keyboard
import time

def press(key):
    
    if key == "up":
        print("Up")
        
    elif key == "down":
        print("Down")   
    
    elif key == "left":
        print("Left")
        
    elif key == "right":
        print("Right")
        
    elif key == "space":
        print("Space")
        time.sleep(1)
        
    elif key == "enter":
        print("Enter")
        time.sleep(1)
        
            
def not_pressed(key):
    
    if key == "e":
        print("Exiting...")
        exit()


if __name__ == "__main__":

    try:
        while True:
            listen_keyboard(
                on_press = press,
                on_release = not_pressed,
                delay_second_char = 0.001,
                delay_other_chars= 0.001)
            
    except ValueError:
        print("Josua")