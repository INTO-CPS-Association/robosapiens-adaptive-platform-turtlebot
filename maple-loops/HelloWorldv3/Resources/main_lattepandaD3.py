from HelloWorldv3.Realization.ManagingSystem.Nodes.Monitor.Monitor import Monitor
from HelloWorldv3.Realization.ManagingSystem.Nodes.Analysis.Analysis import Analysis
import time

_Monitor = Monitor("../Realization/ManagingSystem/Nodes/Monitor/config.yaml")
_Analysis = Analysis("../Realization/ManagingSystem/Nodes/Analysis/config.yaml")

_Monitor.register_callbacks()
_Analysis.register_callbacks()

_Monitor.start()
_Analysis.start()

try:
    print("Script is running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # Sleep to avoid busy-waiting
except KeyboardInterrupt:
    _Monitor.shutdown()
    _Analysis.shutdown()
    print("\nKeyboard interruption detected. Exiting...")