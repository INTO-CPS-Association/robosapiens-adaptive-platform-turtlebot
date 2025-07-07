########################################
# Base Image for TurtleBot3 Simulation #
########################################
FROM ubuntu:22.04 AS base

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=devuser
ARG UID=1000
ARG GID=${UID}

# Install basic apt packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git libcanberra-gtk-module libcanberra-gtk3-module fuse3 libfuse2 libqt5svg5-dev \
    python3-opencv python3-tk python3-pyqt5.qtwebengine mesa-utils\
    gdb gdbserver vim jupyter-notebook python3-jupyter-server sudo ssh zsh tmux\
    neovim curl\
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

RUN mkdir -p /ws/src
WORKDIR /ws

# Create new user and home directory
RUN groupadd --gid $GID $USERNAME \
    && useradd --uid ${GID} --gid ${UID} --create-home ${USERNAME} \
    && mkdir -p /etc/sudoers.d/ \
    && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && mkdir -p /home/${USERNAME} \
    && chown -R ${UID}:${GID} /home/${USERNAME}

# Set the ownership of the overlay workspace to the new user
RUN chown -R ${UID}:${GID} /ws

RUN groupadd fuse \
    && usermod -aG fuse,video ${USERNAME}

# Set the user and source entrypoint in the user's .bashrc file
RUN echo Defaults secure_path = /opt/ros/humble/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin > /etc/sudoers.d/secure_path \
    && chmod 0440 /etc/sudoers.d/secure_path

COPY docker/setup.bash /opt/setup.bash
COPY docker/entrypoint.sh /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]
RUN echo "source /opt/entrypoint.sh" >> /root/.profile
USER ${USERNAME}
RUN curl -LsSf https://astral.sh/uv/0.7.19/install.sh | sh
RUN echo "source /opt/entrypoint.sh" >> /home/${USERNAME}/.bashrc
