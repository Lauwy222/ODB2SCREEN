import obd
import time
from datetime import datetime
from obd import OBDStatus

# Replace 'COM8' with your specific COM port
port = 'COM9'

# Establish a connection to the OBD-II adapter
connection = obd.OBD(port)

# List of OBD commands to query initially
commands = [
    obd.commands.PIDS_A,
    obd.commands.STATUS,
    obd.commands.FREEZE_DTC,
    obd.commands.FUEL_STATUS,
    obd.commands.ENGINE_LOAD,
    obd.commands.COOLANT_TEMP,
    obd.commands.SHORT_FUEL_TRIM_1,
    obd.commands.LONG_FUEL_TRIM_1,
    obd.commands.SHORT_FUEL_TRIM_2,
    obd.commands.LONG_FUEL_TRIM_2,
    obd.commands.FUEL_PRESSURE,
    obd.commands.INTAKE_PRESSURE,
    obd.commands.RPM,
    obd.commands.SPEED,
    obd.commands.TIMING_ADVANCE,
    obd.commands.INTAKE_TEMP,
    obd.commands.MAF,
    obd.commands.THROTTLE_POS,
    obd.commands.AIR_STATUS,
    obd.commands.O2_SENSORS,
    obd.commands.O2_B1S1,
    obd.commands.O2_B1S2,
    obd.commands.O2_B1S3,
    obd.commands.O2_B1S4,
    obd.commands.O2_B2S1,
    obd.commands.O2_B2S2,
    obd.commands.O2_B2S3,
    obd.commands.O2_B2S4,
    obd.commands.OBD_COMPLIANCE,
    obd.commands.O2_SENSORS_ALT,
    obd.commands.AUX_INPUT_STATUS,
    obd.commands.RUN_TIME,
    obd.commands.PIDS_B,
    # Add more PIDs as needed
]

# Generate a filename with the current date and time
timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
filename = f"obd_check_{timestamp}.txt"


def save_readings_to_file(data, filename):
    """Save the given data to a text file."""
    with open(filename, 'a') as file:
        file.write(data + '\n')


def check_obd_values(connection, commands, duration=60):
    """Check and log OBD-II values, excluding non-responsive PIDs."""
    start_time = time.time()
    responsive_commands = []

    while (time.time() - start_time) < duration:
        readings = f"\nTimestamp: {datetime.now()}"
        for cmd in commands:
            response = connection.query(cmd)
            if not response.is_null():
                readings += f"\n{cmd.name}: {response.value}"
                if cmd not in responsive_commands:
                    responsive_commands.append(cmd)
            else:
                readings += f"\n{cmd.name}: No Data"

        # Print and save readings
        print(readings)
        save_readings_to_file(readings, filename)

        # Update the command list to only include responsive commands
        commands = responsive_commands

        time.sleep(1)  # Pause for 1 second between readings


def boot_cycle_check(connection):
    """Perform a boot cycle check to determine connection status."""
    print("Starting boot cycle check...")

    if connection.status() == OBDStatus.NOT_CONNECTED:
        print("Debug: OBD-II adapter is not connected.")
    elif connection.status() == OBDStatus.ELM_CONNECTED:
        print("Debug: ELM327 adapter is connected, but the car is not.")
    elif connection.status() == OBDStatus.OBD_CONNECTED:
        print("Debug: ELM327 adapter is connected, and the car's OBD port is detected, but ignition is off.")
    elif connection.status() == OBDStatus.CAR_CONNECTED:
        print("Debug: ELM327 adapter and car's OBD-II port are connected, and the ignition is on.")
    else:
        print("Debug: Unknown connection status.")


if __name__ == "__main__":
    boot_cycle_check(connection)

    if connection.status() == OBDStatus.CAR_CONNECTED:
        print(f"Connected to OBD-II adapter on {port}")
        check_obd_values(connection, commands)
    else:
        print(f"Failed to connect to the car's OBD-II system. Current status: {connection.status()}")

    # Close the connection after readings
    connection.close()

    print(f"Readings saved to {filename}")
