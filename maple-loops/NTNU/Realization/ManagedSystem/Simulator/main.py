import ship_maneuvering_model
import HydroPara_PI3_alternative1 as HydroPara_PI3
from aux_fuctions import *
import os


def main():
    model= getattr(ship_maneuvering_model, "ShipModel_M1")()
    model_1= getattr(ship_maneuvering_model, "ShipModel_M1")()
    model_2= getattr(ship_maneuvering_model,'ShipModel_M2')()
    model_7= getattr(ship_maneuvering_model,'ShipModel_M7')()
    model_12= getattr(ship_maneuvering_model,'ShipModel_M12')()


    verification_data = "Manuevering_Data_K_SIM\\No_Wind"
    dir_list = [os.path.join(verification_data, file) for file in os.listdir(verification_data)]

    # Testing model
    for file in dir_list:
        print(file)

        data = load_data(file, model.U0)
        data = data.shift(-30)

        # Make the trajectory prediction based on the initial conditions, rudder angle, wind direction and speed collected from the simulator
        eta, nu = model.predict(HydroPara_PI3, data['Surge Speed'][0], data['Sway Speed'][0], data['Yaw Rate'][0],
                                data['Heading'][0], data['x'][0], data['y'][0], data['Rudder Angle'],
                                data['Wind Direction'], data['Wind Speed'])
        eta2, nu2 = model_7.predict(HydroPara_PI3, data['Surge Speed'][0], data['Sway Speed'][0], data['Yaw Rate'][0],
                        data['Heading'][0], data['x'][0], data['y'][0], data['Rudder Angle'],
                        data['Wind Direction'], data['Wind Speed'])
        # make_plots()
        plt.plot(data['x'], data["y"] , label = "true values", color = "blue")
        plt.plot(eta[:,0], eta[:,1], label = "predicted_M1", color = "green")
        plt.plot(eta2[:,0], eta2[:,1], label = "predicted_M2", color = "red")
        plt.show()


if __name__ == "__main__":
    main()

