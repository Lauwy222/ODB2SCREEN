import serial
import time

# Setup serial communication parameters
port = 'COM10'
baudrate = 9600  # Common baud rate, adjust if necessary
timeout = 1  # Timeout for reading data

try:
    # Open the serial port
    ser = serial.Serial(port, baudrate, timeout=timeout)
    print(f"Connected to {port} at {baudrate} baud.")

    # Wait for the device to be ready
    time.sleep(2)

    # Example command to check for the supported PIDs (use a basic OBD-II command)
    command = '0100\r'  # This command asks the OBD-II device which PIDs are supported
    ser.write(command.encode('utf-8'))

    # Wait for and read the response
    response = ser.read(ser.in_waiting or 128).decode('utf-8')
    print(f"Response: {response}")

    # You can loop to read more data or implement further logic here

except serial.SerialException as e:
    print(f"Error connecting to {port}: {e}")

finally:
    # Always close the serial connection
    if ser.is_open:
        ser.close()
    print("Serial connection closed.")
