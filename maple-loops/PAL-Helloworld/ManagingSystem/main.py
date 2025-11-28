from Nodes.Legitimate.Legitimate import Legitimate
from Nodes.Monitor.Monitor import Monitor
from Nodes.Analysis.Analysis import Analysis
from Nodes.Plan.Plan import Plan
from Nodes.Execute.Execute import Execute
import time

from Nodes.Trustworthiness.Trustworthiness import Trustworthiness

monitor = Monitor("Nodes/Monitor/config.yaml")
analyse = Analysis("Nodes/Analysis/config.yaml")
plan = Plan("Nodes/Plan/config.yaml")
execute = Execute("Nodes/Execute/config.yaml")
legitimate = Legitimate("Nodes/Legitimate/config.yaml")
trust_c = Trustworthiness("Nodes/Trustworthiness/config.yaml")

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