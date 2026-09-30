# Plotter-development

Python controller for a home-built 2D pen plotter, running on a Raspberry Pi and driven by G-code files.

## Hardware

- Raspberry Pi with an Adafruit Motor HAT (used through `adafruit_motorkit`), two stepper motors on `stepper1` and `stepper2`.
- Hobby servo on GPIO 14 that lifts and lowers the pen (driven through `pigpio`).
- Two limit switches for homing: GPIO 16 (vertical) and GPIO 17 (horizontal).

## How it works

- `plotter_controller.py` holds the `nc_head` class. Both steppers turn together for every move: opposite directions move the head up or down, the same direction moves it left or right. Steps are converted to millimetres with a calibration factor (`scale_x_y` draws test squares so the real distances can be measured and entered).
- Homing (`end_travel`) raises the pen, drives down until the vertical switch opens, then left until the horizontal switch opens, and sets the position to (0, 0).
- G-code support: `G0` fast moves, `G1` linear moves, `G2`/`G3` arcs (approximated by short segments, 0.05 rad steps), `G91` relative moves. The pen goes down when Z is negative and up otherwise.
- `main.py` is the text menu: go to origin, load a G-code file, plot, set (0, 0), manual control, release steppers, exit.
- Manual control uses the arrow keys (move), Space (pen up), Enter (pen down) and E (exit), read over SSH with `sshkeyboard`.
- `file_sender.py` is a small Flask app with an upload page. It accepts `.gcode` files, keeps the lines that start with `G` and saves them in `shared_documents/` as `name_N.txt`, which is where `main.py` looks for files.

## How to run

On the Raspberry Pi, with I2C enabled and the pigpio daemon running:

```
pip install -r requirements.txt
sudo pigpiod
python main.py
```

To send a G-code file to the Pi, start the upload server and open it in a browser:

```
python file_sender.py
```

The upload form in `templates/index.html` posts to `http://127.0.0.1:5000/upload/`, so open the page on the Pi itself or change that address.

## Structure

- `main.py`: menu and G-code interpreter.
- `plotter_controller.py`: motor, servo and limit switch control.
- `file_sender.py`, `templates/`, `static/`: upload server and its page.
- `key_control.py`: test of keyboard reading.
- `draft.py`: test of the limit switches with two LEDs on GPIO 20 and 21.
- `shared_documents/`: G-code files ready to plot (`cat_1.txt`, `engranajes_1.txt`, `engranajes_2.txt`, `gato_cuadrado_1.txt`).
- `static/engranajes.gcode`, `engranajes.svg`: source drawing of the gears example.

## Author

Pablo Tuñón Laguna, 2024. MIT licence.
