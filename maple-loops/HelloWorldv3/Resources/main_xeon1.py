from HelloWorldv3.Realization.ManagingSystem.Nodes.Plan.Plan import Plan
from HelloWorldv3.Realization.ManagingSystem.Nodes.Execute.Execute import Execute
import time

_Plan = Plan("../Realization/ManagingSystem/Nodes/Plan/config.yaml")
_Execute = Execute("../Realization/ManagingSystem/Nodes/Execute/config.yaml")

_Plan.register_callbacks()
_Execute.register_callbacks()

_Plan.start()
_Execute.start()

try:
    print("Script is running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # Sleep to avoid busy-waiting
except KeyboardInterrupt:
    _Plan.shutdown()
    _Execute.shutdown()
    print("\nKeyboard interruption detected. Exiting...")