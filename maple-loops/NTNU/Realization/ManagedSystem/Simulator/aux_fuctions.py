import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt


def rot_z(angle):
    return np.array([[np.cos(angle), -np.sin(angle), 0],
                     [np.sin(angle), np.cos(angle), 0],
                     [0, 0, 1]])


def load_data(file, U0):
    df = pd.read_csv(file, usecols=['Time', 'Surge Speed', 'Sway Speed', 'Yaw Rate',
                                         'Heading', 'x', 'y', 'Rudder Angle','Wind Direction',
                                         'Wind Speed'])
    df['Surge Speed'] = df['Surge Speed'] - U0    # variations around the nominal speed U0
    return df


def make_plots(data, eta, nu):
    u = data['Surge Speed']
    v = data['Sway Speed']
    r = data['Yaw Rate']
    x = data['x']
    y = data['y']

    time_array = np.arange(0, len(nu[:, 0]))
    time_array = time_array * 1  # because the dt is 0.1 seconds

    # Comparing the true and predicted trajectory and velocity components
    plt.figure(figsize=(10, 6))
    plot_pos = plt.subplot2grid((3, 6), (0, 0), rowspan=3, colspan=3)
    plot_u = plt.subplot2grid((3, 6), (0, 3), rowspan=1, colspan=3)
    plot_v = plt.subplot2grid((3, 6), (1, 3), rowspan=1, colspan=3)
    plot_r = plt.subplot2grid((3, 6), (2, 3), rowspan=1, colspan=3)

    plot_u.plot(time_array, nu[:, 0], label="predicted")
    plot_u.plot(time_array, u, label="true values")
    plot_u.set_xlabel('Time [s]')
    plot_u.set_ylabel('u [m/s]')
    plot_u.grid()

    plot_v.plot(time_array, nu[:, 1], label="predicted")
    plot_v.plot(time_array, v, label="true values")
    plot_v.set_xlabel('Time [s]')
    plot_v.set_ylabel('v [m/s]')
    plot_v.grid()

    plot_r.plot(time_array, nu[:, 2], label="predicted")
    plot_r.plot(time_array, r, label="true values")
    plot_r.set_xlabel('Time [s]')
    plot_r.set_ylabel('r [rad/s]')
    plot_r.grid()

    plot_pos.plot(eta[:, 1], eta[:, 0], label="predicted")
    plot_pos.plot(y, x, label="true values")
    plot_pos.set_xlabel('y [m] - East')
    plot_pos.set_ylabel('x [m] - North')
    plot_pos.legend()
    plot_pos.grid()

    plt.tight_layout()
    plt.show()


def get_wind_forces(wind_d, wind_speed, heading, Alw, Afw, u, v, delta, Cdlaf_0, Cdlaf_pi, Cdt, sl, Loa):
    # This function calculates the forces on the vessel due to the wind in the x and y direction and the moment around the z axis

    v_rw = v - wind_speed*np.sin(wind_d-heading)
    u_rw = u - wind_speed*np.cos(wind_d-heading)

    gama_w = -math.atan2(v_rw, u_rw)
    Vrw = np.sqrt((u_rw**2)+(v_rw**2))

    if abs(gama_w) <= np.pi / 2:
        CDLAF = Cdlaf_0
    else:
        CDLAF = Cdlaf_pi

    Cdl = CDLAF*Afw/Alw

    denominator = 1 - ((delta/2)*(1-Cdl/Cdt)*((np.sin(2*gama_w))**2))
    Cx = -CDLAF*(np.cos(gama_w))/(denominator)
    Cy = Cdt*(np.sin(gama_w))/(denominator)
    Cn = Cy*((sl/Loa)-(0.18*(gama_w-(np.pi/2))))

    tau = 0.5*1.204* (Vrw**2) * np.array([Cx, Cy, Cn])
    return tau
