import serial

try:
    ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)
    print("Reading GPS on /dev/ttyS0... Ctrl+C to stop\n")
    while True:
        try:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$GNRMC') or line.startswith('$GPRMC'):
                print(line)
        except:
            pass

except Exception as e:
    print(f"Error: {e}")