import serial
import time
import sys
import tty
import termios

# --- Connect to Arduino ---
try:
    arduino = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset
    print("Arduino connected on /dev/ttyUSB0")
except Exception as e:
    print(f"Cannot connect to Arduino: {e}")
    sys.exit()

def send_command(cmd):
    arduino.write((cmd + '\n').encode())
    print(f"Sent: {cmd}")

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

print("\n--- Motor Keyboard Control ---")
print("Arrow UP    = Forward")
print("Arrow DOWN  = Backward")
print("Arrow LEFT  = Turn Left")
print("Arrow RIGHT = Turn Right")
print("SPACE       = Stop")
print("Q           = Quit")
print("------------------------------\n")

try:
    while True:
        key = get_key()

        if key == '\x1b[A':    # Up arrow
            send_command('F')
        elif key == '\x1b[B':  # Down arrow
            send_command('B')
        elif key == '\x1b[D':  # Left arrow
            send_command('L')
        elif key == '\x1b[C':  # Right arrow
            send_command('R')
        elif key == ' ':       # Space
            send_command('S')
        elif key in ('q', 'Q'):
            send_command('S')
            print("Stopped")
            break

except KeyboardInterrupt:
    send_command('S')
    print("\nStopped")

finally:
    arduino.close()