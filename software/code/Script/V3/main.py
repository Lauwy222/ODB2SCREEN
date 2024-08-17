import obd
import time
from datetime import datetime
from obd import OBDStatus

# Replace 'COM8' with your specific COM port
port = 'COM8'

# Establish a connection to the OBD-II adapter
connection = obd.OBD(port)

# Enable or disable each mode
ENABLE_MODE_01 = True   # Basic car dashboard data.
ENABLE_MODE_02 = False  # Mode 02 commands are the same as mode 01, but are metrics from when the last DTC occurred (the freeze frame).
ENABLE_MODE_03 = False   # Get Diagnostic Trouble Codes
ENABLE_MODE_04 = False  # Be cautious with this; it clears DTCs
ENABLE_MODE_06 = False  # RAW Sensor data: WARNING: mode 06 is experimental. While it passes software tests, it has not been tested on a real vehicle.
ENABLE_MODE_07 = True   # Get DTCs from the current/last driving cycle
ENABLE_MODE_09 = False   # ECU information: WARNING: mode 09 is experimental. While it has been tested on a hardware simulator, only a subset of the supported commands have (00-06) been tested.

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


def check_fault_codes(connection):
    """Check and log Diagnostic Trouble Codes (DTCs)."""
    print("Checking for Diagnostic Trouble Codes (DTCs)...")
    response = connection.query(obd.commands.GET_DTC)

    if not response.is_null():
        dtcs = response.value
        if dtcs:
            dtc_readings = "Diagnostic Trouble Codes Found:"
            for dtc in dtcs:
                dtc_code, dtc_description = dtc
                dtc_readings += f"\n{dtc_code}: {dtc_description if dtc_description else 'No Description Available'}"
            print(dtc_readings)
            save_readings_to_file(dtc_readings, filename)
        else:
            print("No Diagnostic Trouble Codes found.")
            save_readings_to_file("No Diagnostic Trouble Codes found.", filename)
    else:
        print("Failed to retrieve Diagnostic Trouble Codes.")
        save_readings_to_file("Failed to retrieve Diagnostic Trouble Codes.", filename)


def run_mode_01(connection):
    """Run Mode 01 to retrieve live data."""
    commands_mode_01 = [
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
        obd.commands.DISTANCE_W_MIL,
        obd.commands.FUEL_RAIL_PRESSURE_VAC,
        obd.commands.FUEL_RAIL_PRESSURE_DIRECT,
        obd.commands.O2_S1_WR_VOLTAGE,
        obd.commands.O2_S2_WR_VOLTAGE,
        obd.commands.O2_S3_WR_VOLTAGE,
        obd.commands.O2_S4_WR_VOLTAGE,
        obd.commands.O2_S5_WR_VOLTAGE,
        obd.commands.O2_S6_WR_VOLTAGE,
        obd.commands.O2_S7_WR_VOLTAGE,
        obd.commands.O2_S8_WR_VOLTAGE,
        obd.commands.COMMANDED_EGR,
        obd.commands.EGR_ERROR,
        obd.commands.EVAPORATIVE_PURGE,
        obd.commands.FUEL_LEVEL,
        obd.commands.WARMUPS_SINCE_DTC_CLEAR,
        obd.commands.DISTANCE_SINCE_DTC_CLEAR,
        obd.commands.EVAP_VAPOR_PRESSURE,
        obd.commands.BAROMETRIC_PRESSURE,
        obd.commands.O2_S1_WR_CURRENT,
        obd.commands.O2_S2_WR_CURRENT,
        obd.commands.O2_S3_WR_CURRENT,
        obd.commands.O2_S4_WR_CURRENT,
        obd.commands.O2_S5_WR_CURRENT,
        obd.commands.O2_S6_WR_CURRENT,
        obd.commands.O2_S7_WR_CURRENT,
        obd.commands.O2_S8_WR_CURRENT,
        obd.commands.CATALYST_TEMP_B1S1,
        obd.commands.CATALYST_TEMP_B2S1,
        obd.commands.CATALYST_TEMP_B1S2,
        obd.commands.CATALYST_TEMP_B2S2,
        obd.commands.PIDS_C,
        obd.commands.STATUS_DRIVE_CYCLE,
        obd.commands.CONTROL_MODULE_VOLTAGE,
        obd.commands.ABSOLUTE_LOAD,
        obd.commands.COMMANDED_EQUIV_RATIO,
        obd.commands.RELATIVE_THROTTLE_POS,
        obd.commands.AMBIANT_AIR_TEMP,
        obd.commands.THROTTLE_POS_B,
        obd.commands.THROTTLE_POS_C,
        obd.commands.ACCELERATOR_POS_D,
        obd.commands.ACCELERATOR_POS_E,
        obd.commands.ACCELERATOR_POS_F,
        obd.commands.THROTTLE_ACTUATOR,
        obd.commands.RUN_TIME_MIL,
        obd.commands.TIME_SINCE_DTC_CLEARED,
        obd.commands.MAX_MAF,
        obd.commands.FUEL_TYPE,
        obd.commands.ETHANOL_PERCENT,
        obd.commands.EVAP_VAPOR_PRESSURE_ABS,
        obd.commands.EVAP_VAPOR_PRESSURE_ALT,
        obd.commands.SHORT_O2_TRIM_B1,
        obd.commands.LONG_O2_TRIM_B1,
        obd.commands.SHORT_O2_TRIM_B2,
        obd.commands.LONG_O2_TRIM_B2,
        obd.commands.FUEL_RAIL_PRESSURE_ABS,
        obd.commands.RELATIVE_ACCEL_POS,
        obd.commands.HYBRID_BATTERY_REMAINING,
        obd.commands.OIL_TEMP,
        obd.commands.FUEL_INJECT_TIMING,
        obd.commands.FUEL_RATE,
    ]
    check_obd_values(connection, commands_mode_01)


def run_mode_02(connection):
    """Run Mode 02 to retrieve freeze frame data."""
    commands_mode_02 = [
        obd.commands.DTC_PIDS_A,
        obd.commands.DTC_STATUS,
        obd.commands.DTC_FUEL_STATUS,
        obd.commands.DTC_ENGINE_LOAD,
        obd.commands.DTC_COOLANT_TEMP,
        obd.commands.DTC_SHORT_FUEL_TRIM_1,
        obd.commands.DTC_LONG_FUEL_TRIM_1,
        obd.commands.DTC_SHORT_FUEL_TRIM_2,
        obd.commands.DTC_LONG_FUEL_TRIM_2,
        obd.commands.DTC_FUEL_PRESSURE,
        obd.commands.DTC_INTAKE_PRESSURE,
        obd.commands.DTC_RPM,
        obd.commands.DTC_SPEED,
        obd.commands.DTC_TIMING_ADVANCE,
        obd.commands.DTC_INTAKE_TEMP,
        obd.commands.DTC_MAF,
        obd.commands.DTC_THROTTLE_POS,
        obd.commands.DTC_AIR_STATUS,
        obd.commands.DTC_O2_SENSORS,
        obd.commands.DTC_O2_B1S1,
        obd.commands.DTC_O2_B1S2,
        obd.commands.DTC_O2_B1S3,
        obd.commands.DTC_O2_B1S4,
        obd.commands.DTC_O2_B2S1,
        obd.commands.DTC_O2_B2S2,
        obd.commands.DTC_O2_B2S3,
        obd.commands.DTC_O2_B2S4,
        obd.commands.DTC_OBD_COMPLIANCE,
        obd.commands.DTC_O2_SENSORS_ALT,
        obd.commands.DTC_AUX_INPUT_STATUS,
        obd.commands.DTC_RUN_TIME,
        obd.commands.DTC_PIDS_B,
        obd.commands.DTC_DISTANCE_W_MIL,
        obd.commands.DTC_FUEL_RAIL_PRESSURE_VAC,
        obd.commands.DTC_FUEL_RAIL_PRESSURE_DIRECT,
        obd.commands.DTC_O2_S1_WR_VOLTAGE,
        obd.commands.DTC_O2_S2_WR_VOLTAGE,
        obd.commands.DTC_O2_S3_WR_VOLTAGE,
        obd.commands.DTC_O2_S4_WR_VOLTAGE,
        obd.commands.DTC_O2_S5_WR_VOLTAGE,
        obd.commands.DTC_O2_S6_WR_VOLTAGE,
        obd.commands.DTC_O2_S7_WR_VOLTAGE,
        obd.commands.DTC_O2_S8_WR_VOLTAGE,
        obd.commands.DTC_COMMANDED_EGR,
        obd.commands.DTC_EGR_ERROR,
        obd.commands.DTC_EVAPORATIVE_PURGE,
        obd.commands.DTC_FUEL_LEVEL,
        obd.commands.DTC_WARMUPS_SINCE_DTC_CLEAR,
        obd.commands.DTC_DISTANCE_SINCE_DTC_CLEAR,
        obd.commands.DTC_EVAP_VAPOR_PRESSURE,
        obd.commands.DTC_BAROMETRIC_PRESSURE,
        obd.commands.DTC_O2_S1_WR_CURRENT,
        obd.commands.DTC_O2_S2_WR_CURRENT,
        obd.commands.DTC_O2_S3_WR_CURRENT,
        obd.commands.DTC_O2_S4_WR_CURRENT,
        obd.commands.DTC_O2_S5_WR_CURRENT,
        obd.commands.DTC_O2_S6_WR_CURRENT,
        obd.commands.DTC_O2_S7_WR_CURRENT,
        obd.commands.DTC_O2_S8_WR_CURRENT,
        obd.commands.DTC_CATALYST_TEMP_B1S1,
        obd.commands.DTC_CATALYST_TEMP_B2S1,
        obd.commands.DTC_CATALYST_TEMP_B1S2,
        obd.commands.DTC_CATALYST_TEMP_B2S2,
        obd.commands.DTC_PIDS_C,
        obd.commands.DTC_STATUS_DRIVE_CYCLE,
        obd.commands.DTC_CONTROL_MODULE_VOLTAGE,
        obd.commands.DTC_ABSOLUTE_LOAD,
        obd.commands.DTC_COMMANDED_EQUIV_RATIO,
        obd.commands.DTC_RELATIVE_THROTTLE_POS,
        obd.commands.DTC_AMBIANT_AIR_TEMP,
        obd.commands.DTC_THROTTLE_POS_B,
        obd.commands.DTC_THROTTLE_POS_C,
        obd.commands.DTC_ACCELERATOR_POS_D,
        obd.commands.DTC_ACCELERATOR_POS_E,
        obd.commands.DTC_ACCELERATOR_POS_F,
        obd.commands.DTC_THROTTLE_ACTUATOR,
        obd.commands.DTC_RUN_TIME_MIL,
        obd.commands.DTC_TIME_SINCE_DTC_CLEARED,
        obd.commands.DTC_MAX_MAF,
        obd.commands.DTC_FUEL_TYPE,
        obd.commands.DTC_ETHANOL_PERCENT,
        obd.commands.DTC_EVAP_VAPOR_PRESSURE_ABS,
        obd.commands.DTC_EVAP_VAPOR_PRESSURE_ALT,
        obd.commands.DTC_SHORT_O2_TRIM_B1,
        obd.commands.DTC_LONG_O2_TRIM_B1,
        obd.commands.DTC_SHORT_O2_TRIM_B2,
        obd.commands.DTC_LONG_O2_TRIM_B2,
        obd.commands.DTC_FUEL_RAIL_PRESSURE_ABS,
        obd.commands.DTC_RELATIVE_ACCEL_POS,
        obd.commands.DTC_HYBRID_BATTERY_REMAINING,
        obd.commands.DTC_OIL_TEMP,
        obd.commands.DTC_FUEL_INJECT_TIMING,
        obd.commands.DTC_FUEL_RATE,
    ]
    check_obd_values(connection, commands_mode_02)


def run_mode_04(connection):
    """Run Mode 04 to clear DTCs."""
    print("Clearing Diagnostic Trouble Codes (DTCs)...")
    response = connection.query(obd.commands.CLEAR_DTC)
    if response.is_success():
        print("DTCs successfully cleared.")
        save_readings_to_file("DTCs successfully cleared.", filename)
    else:
        print("Failed to clear DTCs.")
        save_readings_to_file("Failed to clear DTCs.", filename)


def run_mode_06(connection):
    """Run Mode 06 to retrieve monitor test results (experimental)."""
    commands_mode_06 = [
        obd.commands.MIDS_A,
        obd.commands.MONITOR_O2_B1S1,
        obd.commands.MONITOR_O2_B1S2,
        obd.commands.MONITOR_O2_B1S3,
        obd.commands.MONITOR_O2_B1S4,
        obd.commands.MONITOR_O2_B2S1,
        obd.commands.MONITOR_O2_B2S2,
        obd.commands.MONITOR_O2_B2S3,
        obd.commands.MONITOR_O2_B2S4,
        obd.commands.MONITOR_CATALYST_B1,
        obd.commands.MONITOR_CATALYST_B2,
        obd.commands.MONITOR_EGR_B1,
        obd.commands.MONITOR_EGR_B2,
        obd.commands.MONITOR_VVT_B1,
        obd.commands.MONITOR_VVT_B2,
        obd.commands.MONITOR_EVAP_150,
        obd.commands.MONITOR_EVAP_090,
        obd.commands.MONITOR_EVAP_040,
        obd.commands.MONITOR_EVAP_020,
        obd.commands.MONITOR_PURGE_FLOW,
        obd.commands.MONITOR_O2_HEATER_B1S1,
        obd.commands.MONITOR_O2_HEATER_B1S2,
        obd.commands.MONITOR_O2_HEATER_B1S3,
        obd.commands.MONITOR_O2_HEATER_B1S4,
        obd.commands.MONITOR_O2_HEATER_B2S1,
        obd.commands.MONITOR_O2_HEATER_B2S2,
        obd.commands.MONITOR_O2_HEATER_B2S3,
        obd.commands.MONITOR_O2_HEATER_B2S4,
        obd.commands.MONITOR_HEATED_CATALYST_B1,
        obd.commands.MONITOR_HEATED_CATALYST_B2,
        obd.commands.MONITOR_SECONDARY_AIR_1,
        obd.commands.MONITOR_SECONDARY_AIR_2,
        obd.commands.MONITOR_SECONDARY_AIR_3,
        obd.commands.MONITOR_SECONDARY_AIR_4,
        obd.commands.MONITOR_FUEL_SYSTEM_B1,
        obd.commands.MONITOR_FUEL_SYSTEM_B2,
        obd.commands.MONITOR_BOOST_PRESSURE_B1,
        obd.commands.MONITOR_BOOST_PRESSURE_B2,
        obd.commands.MONITOR_NOX_ABSORBER_B1,
        obd.commands.MONITOR_NOX_ABSORBER_B2,
        obd.commands.MONITOR_NOX_CATALYST_B1,
        obd.commands.MONITOR_NOX_CATALYST_B2,
        obd.commands.MONITOR_MISFIRE_GENERAL,
        obd.commands.MONITOR_MISFIRE_CYLINDER_1,
        obd.commands.MONITOR_MISFIRE_CYLINDER_2,
        obd.commands.MONITOR_MISFIRE_CYLINDER_3,
        obd.commands.MONITOR_MISFIRE_CYLINDER_4,
        obd.commands.MONITOR_MISFIRE_CYLINDER_5,
        obd.commands.MONITOR_MISFIRE_CYLINDER_6,
        obd.commands.MONITOR_MISFIRE_CYLINDER_7,
        obd.commands.MONITOR_MISFIRE_CYLINDER_8,
        obd.commands.MONITOR_PM_FILTER_B1,
        obd.commands.MONITOR_PM_FILTER_B2,
    ]
    check_obd_values(connection, commands_mode_06)


def run_mode_07(connection):
    """Run Mode 07 to retrieve pending DTCs."""
    print("Checking for pending Diagnostic Trouble Codes (DTCs)...")
    response = connection.query(obd.commands.GET_CURRENT_DTC)
    if not response.is_null():
        dtcs = response.value
        if dtcs:
            dtc_readings = "Pending Diagnostic Trouble Codes Found:"
            for dtc in dtcs:
                dtc_code, dtc_description = dtc
                dtc_readings += f"\n{dtc_code}: {dtc_description if dtc_description else 'No Description Available'}"
            print(dtc_readings)
            save_readings_to_file(dtc_readings, filename)
        else:
            print("No pending Diagnostic Trouble Codes found.")
            save_readings_to_file("No pending Diagnostic Trouble Codes found.", filename)
    else:
        print("Failed to retrieve pending Diagnostic Trouble Codes.")
        save_readings_to_file("Failed to retrieve pending Diagnostic Trouble Codes.", filename)


def run_mode_09(connection):
    """Run Mode 09 to retrieve vehicle information (experimental)."""
    commands_mode_09 = [
        obd.commands.VIN,
        obd.commands.CALIBRATION_ID,
        obd.commands.CVN,
        obd.commands.ECU_NAME,
        # Add more Mode 09 PIDs as needed
    ]
    check_obd_values(connection, commands_mode_09)


if __name__ == "__main__":
    boot_cycle_check(connection)

    if connection.status() == OBDStatus.CAR_CONNECTED:
        if ENABLE_MODE_03:
            check_fault_codes(connection)
        if ENABLE_MODE_01:
            run_mode_01(connection)
        if ENABLE_MODE_02:
            run_mode_02(connection)
        if ENABLE_MODE_04:
            run_mode_04(connection)
        if ENABLE_MODE_06:
            run_mode_06(connection)
        if ENABLE_MODE_07:
            run_mode_07(connection)
        if ENABLE_MODE_09:
            run_mode_09(connection)
    else:
        print(f"Failed to connect to the car's OBD-II system. Current status: {connection.status()}")

    # Close the connection after readings
    connection.close()

    print(f"Readings saved to {filename}")
