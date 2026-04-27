import serial
import time

# Use the new alias we created in the udev rule
port = '/dev/gpsport' 

try:
    ser = serial.Serial(port, baudrate=9600, timeout=1)
    print(f"--- Connected to GPS on {port} ---")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if '$G' in line:
                print(line)
        time.sleep(0.1)

except Exception as e:
    print(f"Error: {e}")
    print("Check if GPS is wired to Pins 8 & 10 and cmdline.txt is edited.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()