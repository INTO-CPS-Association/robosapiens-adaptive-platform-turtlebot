from rpio.transformations.transformations import swc2code_py,message2code_py
from HelloWorld.Design.HelloWorld_AADLIL import *

#-------------------------------------------------------------------------------------------------------
# !! THESE COMMANDS NORMALLY ARE CALLED FROM THE RPIO CLI, FOR TESTING PURPOSE, A PYTHON FILE IS USED !!
#-------------------------------------------------------------------------------------------------------

# 1. GENERATE AADL FROM ROBOARCH (NOT IMPLEMENTED YET)

# 2. GENERATE AADL INTERMEDIATE LANGUAGE FROM AADL (NOT IMPLEMENTED YET)

# 2. LOAD THE AADL INTERMEDUATE LANGUAGE (MOCKUP)
design = HelloWorld()

# 3. GENERATE CUSTOM MESSAGES FROM AADL INTERMEDIATE LANGUAGE
try:
    message2code_py(system=design, path="ManagingSystem/Messages")
    message2code_py(system=design, path="ManagedSystem/Messages")
except:
    print("Failed to generate the messages")

# 4. GENERATE SWC CODE FROM AADL INTERMEDIATE LANGUAGE
try:
    swc2code_py(system=design,path="Nodes")
except:
    print("Failed to generate the software components")

