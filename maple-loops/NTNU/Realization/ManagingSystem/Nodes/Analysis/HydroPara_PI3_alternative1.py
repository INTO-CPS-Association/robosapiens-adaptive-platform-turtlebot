import numpy as np


def get_X(u, v, r, d, U, L):
    X = np.array((u * U, u ** 2, (u ** 3) / U, v ** 2, (L ** 2) * r ** 2, r * v * L,
                  (U ** 2) * d ** 2, U * u * d ** 2, U * v * d, u * v * d))
    return X


def get_Y(u, v, r, d, U, L):
    Y = np.array((v * U, U * r * L, (v ** 3) / U, (r * L * v ** 2) / U, v * u,
                  r * L * u, (U ** 2) * d, (U ** 2) * d ** 3, u * U * d, d * u ** 2, U * v * d ** 2,
                  d * v ** 2, U ** 2, U * u, u ** 2))
    return Y


def get_N(u, v, r, d, U, L):
    N = np.array((v * U, U * r * L, (v ** 3) / U, (r * L * v ** 2) / U, v * u,
                  r * L * u, (U ** 2) * d, (U ** 2) * d ** 3, u * U * d, d * u ** 2, U * v * d ** 2,
                  d * v ** 2, U ** 2, U * u, u ** 2))
    return N
