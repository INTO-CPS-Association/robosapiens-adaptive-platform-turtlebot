from rpio.metamodels.aadl2_IL import *



def HelloWorld_v4():
    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------- MESSAGES ----------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------


    #laserScan message
    ranges = data(name='ranges', dataType="Array")
    angle_increment = data(name= 'angle_increment', dataType="Float_64")
    laser_scan = message(name="LaserScan",featureList=[ranges,angle_increment])

    # rotationAction message
    omega = data(name="omega",dataType="Float_64")
    duration = data(name="duration",dataType="Float_64")
    direction = message(name="Direction",featureList=[omega,duration])

    # new_data Event
    new_data = data(name="new_data",dataType="Boolean")
    new_data_message = message(name="NewDataEvent",featureList=[new_data])
    
    # anomaly Event
    anomaly = data(name="anomaly",dataType="Boolean")
    anomaly_message = message(name="AnomalyEvent",featureList=[anomaly])

    # new_plan Event
    new_plan = data(name="NewPlan",dataType="Boolean")
    new_plan_event = message(name="NewPlanEvent",featureList=[new_plan])

    # legitimate message
    legitimate = data(name="legitimate",dataType="Boolean")
    legitimate_message = message(name="LegitimateMessage",featureList=[legitimate])

    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------- LOGICAL ARCHITECTURE ----------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
    adaptiveSystem = system(name="adaptiveSystem", description="Example adaptive system",messageList=[laser_scan,direction,anomaly_message,new_plan_event])

    #-A- --- managed system ---
    managedSystem = system(name="managedSystem", description="managed system part")

    _laserScan_OUT = outport(name="laser_scan",type="event data", message= laser_scan)
    _direction_IN = inport(name="direction",type="event data", message=direction)

    managedSystem.addFeature(_laserScan_OUT)
    managedSystem.addFeature(_direction_IN)

    #-B- --- managing system ---

    managingSystem = system(name="managingSystem", description="managing system part")

    _laser_scan_IN = inport(name="laser_scan",type="event data", message=laser_scan)
    _direction_OUT = outport(name="direction",type="event data", message=direction)

    managingSystem.addFeature(_laser_scan_IN)
    managingSystem.addFeature(_direction_OUT)

    # connections
    c1 = connection(source=_laserScan_OUT, destination=_laser_scan_IN)
    c2 = connection(source=_direction_OUT, destination=_direction_IN)


    #---------------------COMPONENT LEVEL---------------------------

    #-MONITOR-
    monitor = process(name="Monitor", description="monitor component")

    _laserScan = outport(name="laser_scan",type="data", message=laser_scan)
    _new_data_out = outport(name="new_data",type="event" , message=new_data_message)


    monitor.addFeature(_laserScan)
    monitor.addFeature(_new_data_out)

    monitor_data = thread(name="monitor_data",featureList=[_laserScan, _new_data_out],eventTrigger='Scan')
    monitor.addThread(monitor_data)

    #-ANALYSIS-
    analysis = process(name="Analysis", description="analysis component")

    _laserScan_in = inport(name="laser_scan",type="data", message=laser_scan)
    _anomaly_out = outport(name="anomaly",type="event", message=anomaly_message)

    analysis.addFeature(_laserScan_in)
    analysis.addFeature(_anomaly_out)

    analyse_scan_data = thread(name="analyse_scan_data",featureList=[_laserScan_in,_anomaly_out],eventTrigger='new_data')
    analysis.addThread(analyse_scan_data)


    #-PLAN-
    plan = process(name="Plan", description="plan component")

    #TODO: define input
    _laserScan_in = inport(name="laser_scan",type="data", message=laser_scan)
    _plan_out = outport(name="new_plan",type="event", message=new_plan_event)
    _diraction_out = outport(name="direction",type="data", message=direction)

    plan.addFeature(_laserScan_in)
    plan.addFeature(_plan_out)
    plan.addFeature(_diraction_out)

    planner = thread(name="planner",featureList=[_laserScan_in, _plan_out, _diraction_out],eventTrigger='anomaly')
    plan.addThread(planner)

    #-LEGITIMATE-
    legitimate = process(name="Legitimate", description="legitimate component")
    _plan_l_in = inport(name="new_plan",type="event", message=new_plan_event)
    _legit_out = outport(name= "isLegit",type="event", message=legitimate_message)
    legitimate.addFeature(_plan_l_in)
    legitimate.addFeature(_legit_out)
    legitimize = thread(name="legitimize",featureList=[_plan_l_in,_legit_out],eventTrigger='new_plan')
    legitimate.addThread(legitimize)

    #-EXECUTE-
    execute = process(name="Execute", description="execute component")

    _new_plan_in = inport(name="new_plan",type="event", message=new_plan_event)
    _isLegit = inport(name="isLegit",type="event", message=legitimate_message)
    _directions = inport(name="directions",type="data", message=direction)
    _directions_out = outport(name="/spin_config",type="data event", message=direction)

    execute.addFeature(_new_plan_in)
    execute.addFeature(_isLegit)
    execute.addFeature(_directions)
    execute.addFeature(_directions_out)

    executer = thread(name="executer",featureList=[_new_plan_in,_isLegit,_directions, _directions_out])
    execute.addThread(executer)

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

    # PC PROCESSOR CONNTECTION
    MIPSCapacity = characteristic(name="MIPSCapacity",value=1000.0,dataType="MIPS")
    I1 = port(name="I1",type="event data")
    laptop = processor(name="PC",propertyList=[MIPSCapacity],featureList=[I1],IP="192.168.0.172")
    laptop.runs_rap_backbone= True    #RUNS THE RoboSAPIENS Adaptive Platform backbone


    # # LATTEPANDA PROCESSOR CONNTECTION
    # MIPSCapacity = characteristic(name="MIPSCapacity",value=2000.0,dataType="MIPS")
    # I2 = port(name="I2",type="event data")
    # lattepanda = processor(name="lattepandaD3",propertyList=[MIPSCapacity],featureList=[I2],IP="192.168.0.161")

    # WIFI CONNTECTION
    BandWidthCapacity = characteristic(name="BandWidthCapacity",value=100.0,dataType="Mbytesps")
    Protocol = characteristic(name="Protocol",value="MQTT",dataType="-")
    DataRate = characteristic(name="DataRate",value=100.0,dataType="Mbytesps")
    WriteLatency = characteristic(name="WriteLatency",value=4,dataType="Ms")
    interface = bus(name="interface",propertyList=[BandWidthCapacity,Protocol,DataRate,WriteLatency])

    interface.addConnection(I1)
    # interface.addConnection(I2)

    #-----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------- MAPPING ARCHITECTURE ----------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------

    laptop.addProcessorBinding(process=monitor)
    laptop.addProcessorBinding(process=analysis)
    laptop.addProcessorBinding(process=plan)
    #laptop_xeon1.addProcessorBinding(process=legitimate)
    laptop.addProcessorBinding(process=execute)

    managingSystem.addProcessor(laptop)
    # managingSystem.addProcessor(lattepanda)

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

HelloWorldDesign=HelloWorld_v4()
HelloWorldDesign.object2json(fileName="design.json")


