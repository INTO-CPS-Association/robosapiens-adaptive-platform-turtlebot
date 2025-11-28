import lidarocclusion
from Realization.ManagingSystem.Nodes.Legitimate.Legitimate import Legitimate
from Realization.ManagingSystem.Nodes.Monitor.Monitor import Monitor
from Realization.ManagingSystem.Nodes.Analysis.Analysis import Analysis
from Realization.ManagingSystem.Nodes.Plan.Plan import Plan
from Realization.ManagingSystem.Nodes.Execute.Execute import Execute
import time

from Realization.ManagingSystem.Nodes.Trustworthiness.Trustworthiness import Trustworthiness

monitor = Monitor("Realization/ManagingSystem/Nodes/Monitor/config.yaml")
analyse = Analysis("Realization/ManagingSystem/Nodes/Analysis/config.yaml")
plan = Plan("Realization/ManagingSystem/Nodes/Plan/config.yaml")
execute = Execute("Realization/ManagingSystem/Nodes/Execute/config.yaml")
legitimate = Legitimate("Realization/ManagingSystem/Nodes/Legitimate/config.yaml")
trust_c = Trustworthiness("Realization/ManagingSystem/Nodes/Trustworthiness/config.yaml")

monitor.register_callbacks()
analyse.register_callbacks()
plan.register_callbacks()
legitimate.register_callbacks()
execute.register_callbacks()
trust_c.register_callbacks()



monitor.start()
analyse.start()
plan.start()
legitimate.start()
execute.start()
trust_c.start()


try:
    print("Script is running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # Sleep to avoid busy-waiting
except KeyboardInterrupt:
    monitor.shutdown()
    analyse.shutdown()
    plan.shutdown()
    legitimate.shutdown()
    execute.shutdown()
    trust_c.shutdown()
    print("\nKeyboard interruption detected. Exiting...")