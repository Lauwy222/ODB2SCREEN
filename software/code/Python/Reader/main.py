import pandas as pd
import re
import os
import plotly.graph_objs as go
import plotly.io as pio
import plotly.subplots as sp


def read_data_from_txt(file_path):
    """Read and parse the data from the text file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        data = []
        columns = set()

        # Extract data based on the patterns in the files
        current_data = {}
        for line in lines:
            if "Timestamp:" in line:
                if current_data:
                    data.append(current_data)
                current_data = {"Timestamp": line.split("Timestamp:")[1].strip()}
            else:
                match = re.match(r"(.+?):\s(.+)", line)
                if match:
                    pid, value = match.groups()
                    pid = pid.replace("_", " ").strip()  # Replace underscores with spaces
                    current_data[pid] = value.strip()
                    columns.add(pid)

        if current_data:
            data.append(current_data)

        # Convert the data into a DataFrame
        df = pd.DataFrame(data)

        # Ensure that 'Timestamp' is treated as a datetime object
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        else:
            print("Error: 'Timestamp' column not found in data.")
            return None, []

        return df, sorted(list(columns))  # Sort columns alphabetically
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None, []


def select_pids(columns):
    """Allow the user to select which PIDs to enable/disable."""
    print("Available PIDs:")
    for i, pid in enumerate(columns):
        print(f"{i + 1}. {pid}")

    selected_pids = input("Enter the numbers of the PIDs you want to display, separated by commas: ")
    selected_pids = selected_pids.split(",")

    try:
        selected_pids = [columns[int(pid.strip()) - 1] for pid in selected_pids]
        return selected_pids
    except Exception as e:
        print(f"Error selecting PIDs: {e}")
        return []


def scale_pid_values(df, pid):
    """Custom scaling function based on PID characteristics."""
    if "RPM" in pid:
        return df[pid] / 100  # Scale RPM by 1000
    elif "SPEED" in pid:
        return df[pid] / 10  # Scale speed by 10
    elif "TEMP" in pid:
        return df[pid]  # No scaling for temperature
    elif "VOLTAGE" in pid:
        return df[pid]  # No scaling for voltage
    else:
        return df[pid]  # Default: no scaling


def plot_selected_pids(df, selected_pids):
    """Plot the selected PIDs on a scaled graph and display a table of their values."""
    if not selected_pids:
        print("No PIDs selected. Exiting.")
        return

    df.set_index('Timestamp', inplace=True)  # Use Timestamp as the index

    # Define units for each PID (you may need to adjust these according to your data)
    pid_units = {
        'SPEED': 'km/h',
        'RPM': 'RPM',
        'THROTTLE POS': '%',
        'COOLANT TEMP': '°C',
        'BATTERY VOLTAGE': 'V',
        # Add other PIDs and their units here
    }

    traces = []
    for pid in selected_pids:
        unit = pid_units.get(pid, '')  # Get the unit, or an empty string if the unit isn't found
        try:
            df[pid] = pd.to_numeric(df[pid].str.extract(r'(\d+\.?\d*)')[0], errors='coerce')  # Extract numeric values
            df[pid] = df[pid].fillna(0)  # Replace NaN with 0 or another placeholder value
        except Exception as e:
            print(f"Error processing {pid}: {e}")
            df[pid] = 0  # Set to 0 if conversion fails

        scaled_values = scale_pid_values(df, pid)  # Custom scaling based on PID characteristics
        traces.append(go.Scatter(
            x=df.index,
            y=scaled_values,
            mode='lines+markers',
            name=pid,
            hovertemplate=f'%{{customdata:.2f}} {unit}<extra></extra>',  # Show original value and unit in hover text
            customdata=df[pid]  # Store original data for use in hover text
        ))

    # Create a table with all the rows
    table_trace = go.Table(
        header=dict(values=['Timestamp'] + selected_pids,
                    align='left'),
        cells=dict(values=[df.index.strftime('%Y-%m-%d %H:%M:%S')] + [df[col] for col in selected_pids],
                   align='left')
    )

    # Combine the plot and the table into one figure
    fig = sp.make_subplots(rows=2, cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.1,
                           specs=[[{"type": "xy"}], [{"type": "table"}]],
                           subplot_titles=('Selected PIDs Over Time (Scaled)', 'All Data Points'))

    for trace in traces:
        fig.add_trace(trace, row=1, col=1)

    fig.add_trace(table_trace, row=2, col=1)

    fig.update_layout(height=800, showlegend=True)

    # Add a click event to highlight the row in the table
    fig.update_traces(marker=dict(size=10, opacity=0.7),
                      selector=dict(mode='markers+lines'))

    fig.update_layout(clickmode='event+select')

    def update_point(trace, points, state):
        if points.point_inds:
            selected_time = trace.customdata[points.point_inds[0]]
            for i, t in enumerate(df.index.strftime('%Y-%m-%d %H:%M:%S')):
                if t == selected_time:
                    fig.data[-1].cells.values = [
                        [f"<b>{val}</b>" if i == row else val for row, val in enumerate(col)]
                        for col in fig.data[-1].cells.values
                    ]
                    break

    for trace in fig.data[:-1]:  # Exclude the table trace
        trace.on_click(update_point)

    # Display the interactive plot with the table
    pio.show(fig)

    # Display a table of selected PIDs in the console
    print("\nFull Table of Selected PIDs:")
    print(df[selected_pids].to_string(index=True))


def main():
    directory_path = "."  # Replace with the correct directory path where the files are located
    txt_files = sorted([f for f in os.listdir(directory_path) if f.endswith('.txt')])

    for file_name in txt_files:
        file_path = os.path.join(directory_path, file_name)
        print(f"Processing file: {file_name}")
        df, columns = read_data_from_txt(file_path)

        if df is not None and columns:
            selected_pids = select_pids(columns)
            plot_selected_pids(df, selected_pids)
            break  # Remove this break if you want to process and plot data from all files


if __name__ == "__main__":
    main()
