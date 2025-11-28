from HelloWorldv4.Realization.ManagingSystem.Nodes.Monitor.Monitor import Monitor
from HelloWorldv4.Realization.ManagingSystem.Nodes.Analysis.Analysis import Analysis
from HelloWorldv4.Realization.ManagingSystem.Nodes.Plan.Plan import Plan
from HelloWorldv4.Realization.ManagingSystem.Nodes.Execute.Execute import Execute
import time

_Monitor = Monitor("../Realization/ManagingSystem/Nodes/Monitor/config.yaml")
_Analysis = Analysis("../Realization/ManagingSystem/Nodes/Analysis/config.yaml")
_Plan = Plan("../Realization/ManagingSystem/Nodes/Plan/config.yaml")
_Execute = Execute("../Realization/ManagingSystem/Nodes/Execute/config.yaml")

_Monitor.register_callbacks()
_Analysis.register_callbacks()
_Plan.register_callbacks()
_Execute.register_callbacks()

_Monitor.start()
_Analysis.start()
_Plan.start()
_Execute.start()

try:
    print("Script is running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # Sleep to avoid busy-waiting
except KeyboardInterrupt:
    _Monitor.shutdown()
    _Analysis.shutdown()
    _Plan.shutdown()
    _Execute.shutdown()
    print("\nKeyboard interruption detected. Exiting...")