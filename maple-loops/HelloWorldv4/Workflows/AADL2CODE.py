# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.workflow.tasks import *
from rpio.workflow.executer import Executer_GUI, Executer_headless
# try:
#     with open("Design/design.json", "r") as design_file:
#         design_data = design_file.read()
#         print(f"Design name: {design_file.name}")
# except FileNotFoundError:   
#         print("Design file not found. Please check the path.")
#         design_data = None
# 1 . define the tasks
tasks = {
    #"Check if robosapiensio package is installed": t_check_robosapiensio,
    "Generate custom messages": t_generate_messages,	
    "Generate swc code skeletons": t_generate_swc_skeletons,
    "Generate swc launch files": t_generate_swc_launch,
    "Generate main file": t_generate_main,
    "Generate docker compose files": t_generate_docker,
    "Update robosapiensIO.ini file": t_update_robosapiensIO_ini
}

# 2. Launch the graphical executer
app = Executer_GUI(tasks=tasks,name="AADL2CODE")
app.root.mainloop()

#3. Launch the headless executer
#app = Executer_headless(tasks=tasks)
#app.start_workflow()


