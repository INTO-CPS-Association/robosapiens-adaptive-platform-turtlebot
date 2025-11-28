from rpio.metamodels.aadl2_IL import *



def NTNU():
    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------- MESSAGES ----------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------


    #ShipStatus message
    prediction_model = data(name="ship_prediction_model", dataType="string")
    surge_speed = data(name='surge_speed', dataType="Float_64")
    sway_speed = data(name='sway_speed', dataType="Float_64")
    yaw_rate = data(name= 'yaw_rate', dataType="Float_64")
    heading = data(name= 'heading', dataType="Float_64")
    x = data(name='x', dataType="Array")
    y = data(name='y',dataType="Array")

    ship_status = message(name="ShipStatus",featureList=[prediction_model,surge_speed, sway_speed,yaw_rate, heading, x, y ])

    #weather_condition 
    rudder_angle = data(name='rudder_angle', dataType="Array")
    wind_direction = data(name='wind_direction', dataType="Array")
    wind_speed = data(name='wind_speed', dataType="Array")

    weather_condition = message(name="WeatherCondition", featureList=[rudder_angle, wind_direction, wind_speed])


    # new_data message
    new_data = data(name="new_data",dataType="Boolean")
    new_data_message = message(name="NewData",featureList=[new_data])
    # anomaly message
    anomaly = data(name="anomaly",dataType="Boolean")
    anomaly_message = message(name="AnomalyMessage",featureList=[anomaly])
    #new_plan message
    new_plan = data(name="New_plan",dataType="Boolean")
    new_plan_message = message(name="NewPlanMessage",featureList=[new_plan])

    # legitimate message
    legitimate = data(name="legitimate",dataType="Boolean")
    legitimate_message = message(name="LegitimateMessage",featureList=[legitimate])

    #new_model message
    model_message = message(name="Model",featureList=[prediction_model])

    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------- LOGICAL ARCHITECTURE ----------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
    adaptiveSystem = system(name="adaptiveSystem", description="Example adaptive system",messageList=[ship_status,weather_condition,anomaly_message,new_plan_message, model_message])

    #-A- --- managed system ---
    managedSystem = system(name="managedSystem", description="managed system part")

    _shipStatus_OUT = outport(name="ship_status",type="event data", message= ship_status)
    _weatherCondition_OUT = outport(name="weather_condition",type="event data", message= weather_condition)
    _model_IN = inport(name="new_model",type="event data", message=model_message)

    managedSystem.addFeature(_shipStatus_OUT)
    managedSystem.addFeature(_weatherCondition_OUT)
    managedSystem.addFeature(_model_IN)

    #-B- --- managing system ---

    managingSystem = system(name="managingSystem", description="managing system part")

    _shipStatus_IN = inport(name="ship_status",type="event data", message= ship_status)
    _weatherCondition_IN = inport(name="weather_condition",type="event data", message= weather_condition)
    _model_OUT = outport(name="new_model",type="event data", message=model_message)

    managingSystem.addFeature(_shipStatus_IN)
    managingSystem.addFeature(_weatherCondition_IN)
    managingSystem.addFeature(_model_OUT)

    # connections
    c1 = connection(source=_shipStatus_OUT, destination=_shipStatus_IN)
    c2 = connection(source=_weatherCondition_OUT, destination=_weatherCondition_IN)
    c3 = connection(source=_model_OUT, destination=_model_IN)


    #---------------------COMPONENT LEVEL---------------------------

    #-MONITOR-
    monitor = process(name="Monitor", description="monitor component")

    # Wrtite on Knowledge
    _ship_status = outport(name="ship_status",type="data", message=ship_status)
    _weather_condition= outport(name="weather_condition",type="data", message=weather_condition)

    # Output event
    _new_data_out = outport(name="new_data",type="event" , message=new_data_message)


    monitor.addFeature(_ship_status)
    monitor.addFeature(_weather_condition)
    monitor.addFeature(_new_data_out)

    monitor_ship = thread(name="monitor_ship",featureList=[_ship_status, _new_data_out], eventTrigger='ship_status')
    monitor_weather = thread(name="monitor_weather",featureList=[_weather_condition], eventTrigger='weather_condition')
    monitor.addThread(monitor_ship)
    monitor.addThread(monitor_weather)

    #-ANALYSIS-
    analysis = process(name="Analysis", description="analysis component")

    # Read from Knowledge 
    _ship_status_in = inport(name="ShipStatus",type="data", message=ship_status)
    _weather_condition_in = inport(name="WeatherCondition",type="data", message=weather_condition)

    # Output Event
    _anomaly_out = outport(name="anomaly",type="event", message=anomaly_message)

    analysis.addFeature(_ship_status_in)
    analysis.addFeature(_weather_condition_in)
    analysis.addFeature(_anomaly_out)

    analyse_trajectory_prediction = thread(name="analyse_trajectory_prediction",featureList=[_ship_status_in,_weather_condition_in ,_anomaly_out],eventTrigger='new_data')
    analysis.addThread(analyse_trajectory_prediction)


    #-PLAN-
    plan = process(name="Plan", description="plan component")

    #TODO: define input

    _plan_out = outport(name="new_plan",type="event", message=new_plan_message)
    _model_out = outport(name="Model",type="data", message=model_message)

    plan.addFeature(_ship_status_in)
    plan.addFeature(_plan_out)
    plan.addFeature(_model_out)

    planner = thread(name="planner",featureList=[_ship_status_in,_plan_out, _model_out],eventTrigger='anomaly')
    plan.addThread(planner)

    #-LEGITIMATE-
    legitimate = process(name="Legitimate", description="legitimate component")

    #-EXECUTE-
    execute = process(name="Execute", description="execute component")

    _isLegit = inport(name="isLegit",type="event data", message=legitimate_message)
    _model = inport(name="Model",type="data", message=model_message)
    _model_out = outport(name="new_model",type="event", message=model_message)

    execute.addFeature(_isLegit)
    execute.addFeature(_model)
    execute.addFeature(_model_out)

    executer = thread(name="executer",featureList=[_isLegit,_model, _model_out], eventTrigger="new_plan")
    execute.addThread(executer)

    # #-KNOWLEDGE-
    # knowledge = process(name="knowledge", description="knowledge component")
    #
    # _weatherConditions = port(name="weatherConditions",type="event data", message=weatherConditions)
    # _shipPose = port(name="shipPose",type="event data", message=shipPose)
    # _shipAction = port(name="shipAction",type="event data", message=shipAction)
    # _pathEstimate = port(name="pathEstimate",type="event data", message=predictedPath)
    # _pathAnomaly = port(name="pathAnomaly",type="event data", message=AnomalyMessage)
    # _plan = port(name="plan",type="event data", message=predictedPath)
    # _isLegit = port(name="isLegit",type="event data", message=legitimateMessage)

    # knowledge.addFeature(_weatherConditions)
    # knowledge.addFeature(_shipPose)
    # knowledge.addFeature(_shipAction)
    # knowledge.addFeature(_pathEstimate)
    # knowledge.addFeature(_pathAnomaly)
    # knowledge.addFeature(_plan)
    # knowledge.addFeature(_isLegit)

    managingSystem.addProcess(monitor)
    managingSystem.addProcess(analysis)
    managingSystem.addProcess(plan)
    managingSystem.addProcess(legitimate)
    managingSystem.addProcess(execute)
    # managingSystem.addProcess(knowledge)

    #---------------------SYSTEM LEVEL---------------------------
    adaptiveSystem.addSystem(managingSystem)
    adaptiveSystem.addSystem(managedSystem)


    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------- PHYSICAL ARCHITECTURE ---------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------

    # XEON PROCESSOR CONNTECTION
    MIPSCapacity = characteristic(name="MIPSCapacity",value=1000.0,dataType="MIPS")
    I1 = port(name="I1",type="event data")
    laptop_xeon1 = processor(name="xeon1",propertyList=[MIPSCapacity],featureList=[I1],IP="localhost")
    laptop_xeon1.runs_rap_backbone = True  # RUNS THE RoboSAPIENS Adaptive Platform backbone
    #laptop_xeon2 = processor(name="xeon2", propertyList=[MIPSCapacity], featureList=[I1])


    # XEON PROCESSOR CONNTECTION
    MIPSCapacity = characteristic(name="MIPSCapacity",value=2000.0,dataType="MIPS")
    I2 = port(name="I2",type="event data")
    RPI = processor(name="Raspberry Pi 4B",propertyList=[MIPSCapacity],featureList=[I2])

    # WIFI CONNTECTION
    BandWidthCapacity = characteristic(name="BandWidthCapacity",value=100.0,dataType="Mbytesps")
    Protocol = characteristic(name="Protocol",value="MQTT",dataType="-")
    DataRate = characteristic(name="DataRate",value=100.0,dataType="Mbytesps")
    WriteLatency = characteristic(name="WriteLatency",value=4,dataType="Ms")
    interface = bus(name="interface",propertyList=[BandWidthCapacity,Protocol,DataRate,WriteLatency])

    interface.addConnection(I1)
    interface.addConnection(I2)

    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------- MAPPING ARCHITECTURE ----------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------

    laptop_xeon1.addProcessorBinding(process=monitor)
    laptop_xeon1.addProcessorBinding(process=analysis)
    laptop_xeon1.addProcessorBinding(process=plan)
    #laptop_xeon1.addProcessorBinding(process=legitimate)
    laptop_xeon1.addProcessorBinding(process=execute)

    managingSystem.addProcessor(laptop_xeon1)
    #managingSystem.addProcessor(laptop_xeon2)
    managedSystem.addProcessor(RPI)

    # -----------------------------------------------------------------------------------------------------------------------
    # --------------------------------------- NODE IMPLEMENTATION ----------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------
    monitor.formalism = "python"
    analysis.formalism = "python"
    plan.formalism = "python"
    legitimate.formalism = "python"
    execute.formalism = "python"

    monitor.containerization = True
    analysis.containerization = True
    plan.containerization = True
    legitimate.containerization = True
    execute.containerization = True


    return adaptiveSystem

NTNUDesign=NTNU()
NTNUDesign.object2json(fileName="design.json")



