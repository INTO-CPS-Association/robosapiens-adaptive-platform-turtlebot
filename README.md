# RoboSapiens Adaptive Platform (Turtlebot Simulator)

This project supports running a complete self-adaptive system for handling LiDAR occulusion anomolies for a Turtlebot4. This includes a self-adaptive MAPLE-K loop implemented using the RoboSapiens Adaptive Platform, Gazebo simulation of the TurtleBot 4.

The repository provides a devcontainer providing all of the services required to run the system.
Opening one of the devcontainers launches the entire project along with all its dependencies (ROS, MQTT, etc.).

## Getting Started

### System Requirements

This repository has been developed and tested primarily on Linux. It depends on Docker to run the images, x11 to display graphical applications, and Visual Studio Code to launch the devcontainers.

You must have [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed to use this option.

### X11 Permissions

In order for the container to launch graphical applications, you grant x11 authentication permissions using the following command:
```bash

xhost +
```
This must be run after every reboot before launching the containers.

### Launching the Full Project

1. **Open the Full DevContainer:**
   You can open the Visual Studio Code devcontainer for the project in order to run the necessary services, and use the development environment for the adaptive loop.
   To do this, first open the folder for the repository in Visual Studio Code.
   It should prompt you to **"Reopen in Container"** or alternatively, you can open the dev container by pressing Ctrl+Shift+P and selecting **"Rebuild and Reopen in Container"**.
   You should select one of the full devcontainer configurations which matches your hardware (e.g., [`.devcontainer/nvidia-full-tb3/devcontainer.json`](.devcontainer/nvidia-full-tb3/devcontainer.json) or [`.devcontainer/mesa-full-tb3/devcontainer.json`](.devcontainer/mesa-full-tb3/devcontainer.json)) in Visual Studio Code (see **Devcontainer Variants**).

3. **Services in the Container:**  
   The devcontainer setup automatically starts all the necessary services for:
   - Simulation (Gazebo)
   - ROS integration
   - MQTT communication
  
   But you will need to launch the self-adaptive loop and trustworthiness checker yourself (see below).

### Running the Self-Adaptive Loop

To launch the self-adaptive loop:

```bash
cd maple-loops/HelloWorld
python3 main.py
```

This will log its progress in `maple-loops/HelloWorld/MAPE_test.log`.

You can also launch a live dashboard showing the current loop stage and LiDAR mask using:

```bash
cd maple-loops/HelloWorld
python3 LiveDashboard.py
```

### Launching the Trustworthiness Checker
The Trustworthiness Checker is available as a separate Docker Compose service.
You can run it independently in a host terminal by running e.g.

```bash
cd docker/
docker compose run --rm trustworthiness-checker /mnt/host_models/maple_seq.lola --input-mqtt-topics stage --output-stdout
```

This example runs the trustworthiness checker on the model `trustworthiness-specs/maple_seq.lola` from the input MQTT topic `stage` (provided by the self-adaptive loop) and outputs verdicts to STDOUT.
You can also change this to output to MQTT topics via the command:

```bash
cd docker/
docker compose run --rm trustworthiness-checker /mnt/host_models/maple_seq.lola --input-mqtt-topics stage --output-mqtt-topics m a p l e maple
```

## Devcontainer Variants
This repository includes several devcontainer variants to support different hardware and simulation configurations:

### RoboSapiens Adaptive Platform -- Full TB4 Gazebo (NVIDIA GPU):

Provides a full development environment for running the TurtleBot 4 simulation using Gazebo on systems with NVIDIA GPUs. It automatically builds and starts all necessary services and installs the required dependencies after container start-up.

### RoboSapiens Adaptive Platform -- Full TB3 Gazebo (NVIDIA GPU):

Tailored for running TB3 (TurtleBot 3) simulations with NVIDIA GPU support. Features similar configurations as the TB4 variant but adapted for TB3 simulation parameters.

### RoboSapiens Adaptive Platform -- Full Gazebo TB4 (MESA):

Designed for systems without NVIDIA GPUs. This variant uses the MESA graphics stack to enable full Gazebo simulation for TurtleBot 4. It still provides all the integrated services to run the adaptive platform.

### RoboSapiens Adaptive Platform -- Full TB3 Gazebo (MESA):

Tailored for running TB3 (TurtleBot 3) simulations with MESA graphics. Features similar configurations as the TB4 variant but adapted for TB3 simulation parameters.

### RoboSapiens Adaptive Platform -- Full Gazebo TB4 (No GPU):

Provides a complete Gazebo simulation environment for TurtleBot 4 for machines without GPU acceleration. It ensures that users without any graphics hardware can still run the full self-adaptive system, but may be painfully slow.

### RoboSapiens Adaptive Platform -- Full TB3 Gazebo (No GPU):

Tailored for running TB3 (TurtleBot 3) simulations with no GPU acceleration. Features similar configurations as the TB4 variant but adapted for TB3 simulation parameters.

### Non-full variants

These variants just run the main devcontainer without any dependencies. They are useful when separately developing new versions of these dependencies, or for running Gazebo locally.

## Devcontainer command line

It is also possible to run the project without Visual Studio code by using the commandline devcontainers tool.
You can install this tool using
```bash

npm install -g @devcontainers/cli
```

Then you can launch the devcontainer using e.g.
```bash

devcontainer up --workspace-folder $(pwd) --config .devcontainer/mesa-full-tb3/devcontainer.json
```
and open a shell in the devcontainer using
```bash

devcontainer exec --workspace-folder $(pwd) --config .devcontainer/mesa-full-tb3/devcontainer.json /bin/bash
```
