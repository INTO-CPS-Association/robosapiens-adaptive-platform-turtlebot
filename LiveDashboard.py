import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import time
import threading
import re
from datetime import datetime
import pandas as pd
import base64
import io
from PIL import Image, ImageDraw
import time

# Path to the log file
LOG_FILE = 'MAPE_test.log'

# Shared state for phases
phases = []

# Extract and parse log lines in real-time
def parse_log():
    with open(LOG_FILE, 'r') as f:
        f.seek(0, 2)  # Go to the end of the file
        while True:
            line = f.readline()
            if line:
                timestamp_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)", line)
                monitor_match = re.search(r"Monitor.*INFO - (.*?)", line)
                analysis_match = re.search(r"Analysis.*INFO - (.*?)", line)
                plan_match = re.search(r"Plan.*INFO - (.*?)", line)
                execute_match = re.search(r"Execute.*INFO - (.*?)", line)
                legitimate_match = re.search(r"Legitimate.*INFO - (.*?)", line)  # Placeholder
                trustworthiness_match = re.search(r"Trustworthiness.*INFO - (.*?)", line)  # Placeholder
                mask_match = re.search(r"Analysis.*INFO - (.*?)", line)

                if timestamp_match:
                    timestamp = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S,%f")
                    if monitor_match:
                        phases.append(("Monitor", timestamp))
                    elif analysis_match:
                        phases.append(("Analysis", timestamp))
                    elif plan_match:
                        phases.append(("Plan", timestamp))
                    elif execute_match:
                        phases.append(("Execute", timestamp))
                    elif legitimate_match:
                        phases.append(("Legitimate", timestamp))
                    elif trustworthiness_match:
                        phases.append(("Trustworthiness", timestamp))
            else:
                time.sleep(0.5)



# Start the log parser in a separate thread
log_parser_thread = threading.Thread(target=parse_log, daemon=True)
log_parser_thread.start()

# Dash app
app = dash.Dash(__name__)
app.title = "MAPE-K Dashboard"

# Layout
app.layout = html.Div([
    html.H1("MAPE-K Phases Timeline On PC", style={"textAlign": "center"}),
    dcc.Graph(id="gantt-chart"),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every 1 second
        n_intervals=0
    ),
    html.H1("Probabilistic Lidar Mask:", style={"textAlign": "center"}),
    html.Img(id="dynamic-image", style={"height": "180px", "textAlign": "center"}),
    dcc.Interval(id="image-interval", interval=1000, n_intervals=0)  # Update every second
])

# Callback to update Gantt chart
@app.callback(
    Output("gantt-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_gantt_chart(n_intervals):
    if not phases:
        return go.Figure()

    df = pd.DataFrame(phases, columns=["Phase", "Timestamp"])
    current_time = datetime.now()
    df = df[df["Timestamp"] >= current_time - pd.Timedelta(seconds=10)]

    if df.empty:
        return go.Figure()

    start_time = df["Timestamp"].iloc[0]
    df["Start"] = (df["Timestamp"] - start_time).dt.total_seconds()
    df["Duration"] = df["Start"].diff().fillna(1)

    # Create Gantt chart
    fig = go.Figure()
    phase_colors = {
        "Monitor": "#1f77b4",  # Light blue
        "Analysis": "#2ca02c",  # Bright green
        "Plan": "#ff7f0e",  # Deep orange
        "Execute": "#d62728",  # Rich red
        "Legitimate": "#9467bd",  # Purple
        "Trustworthiness": "#8c564b"  # Brown
    }

    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Duration"]],
            y=[row["Phase"]],
            base=row["Start"] - row["Duration"],
            orientation="h",
            marker=dict(
                color=phase_colors.get(row["Phase"], "#7f7f7f"),  # Default gray fallback
            )
        ))

    fig.update_layout(
        title="MAPE-K Phases Timeline (Last 10 Seconds)",
        xaxis_title="Time (seconds)",
        yaxis_title="Phases",
        barmode="overlay",
        template="plotly",
        showlegend=False,
        plot_bgcolor="rgba(240, 240, 240, 1)"  # Light gray background
    )
    return fig

def generate_image():
    try:
        with open("prob_lidar_mask.png", 'rb') as f:
            image = f.read()
        return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')
    except FileNotFoundError:
        # Fallback image or error message if the file is not found
        return 'data:image/png;base64,' + base64.b64encode(b'').decode('utf-8')  # Empty image as a placeholder

# Callback to update the image
@app.callback(
    Output("dynamic-image", "src"),
    [Input("image-interval", "n_intervals")]
)
def update_image(n):
    return generate_image()

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
