from .Function.stft_or import stft, istft
from .Function.auxiva import auxiva
from .Function.projection_back import projection_back

# from .Function.permutation_solver import solve_pp_by_hungarian
import numpy as np
from sklearn.metrics import mean_squared_error as MSE
from scipy.io.wavfile import write
import os
fft_size = 4096
shift_size = 2048
fs = 24000


def main_iva(update_progress_func, itr, n_itr):
    # print(f"itr:{itr}, n_itr:{n_itr}")
    # print(f"itr:{type(itr)}, n_itr:{type(n_itr)}")

    if itr == 1:
        # 初期化
        LOAD_DIR = "static/audio/mix/mix_signals.npy"
        data = np.load(LOAD_DIR)
        x = np.zeros([data.shape[1], data.shape[0]], dtype="float32")
        for idx in range(data.shape[0]):
            x[:, idx] = data[idx, :]



        os.makedirs("static/audio/separate/", exist_ok=True)
        # STFT
        X, window = stft(x, fft_size, shift_size)
        np.save("static/audio/separate/window.npy", window)
        np.save("static/audio/separate/tmp_Y.npy", X)
        np.save("static/audio/separate/X.npy", X)
        # print("STFT done")

    # cycle bss
    stft_separate(update_progress_func, itr, n_itr)

    if itr == n_itr:
        # Bss fas dane.
        # run ISTFT
        estY = np.load("static/audio/separate/tmp_Y.npy")
        window = np.load("static/audio/separate/window.npy")
        z = istft(estY, shift_size, window, fs * 10)
        # esty = istft(estY, shift_size, window, fs * 10)

        for i in range(z.shape[1]):
            write(
                "static/audio/separate/sep" + str(i + 1) + ".wav",
                fs,
                z[:, i].astype("float32"),
            )
        # print("bss done")


def stft_separate(update_progress_func, itr, n_itr):
    S = np.load("static/audio/separate/X.npy")
    X = np.load("static/audio/separate/tmp_Y.npy")
    StoIVA = np.transpose(S, (1, 0, 2))
    XtoIVA = np.transpose(X, (1, 0, 2))
    Y = auxiva(StoIVA, XtoIVA, itr, n_itr, update_progress_func)

    estY = np.transpose(Y, (1, 0, 2))
    np.save("static/audio/separate/tmp_Y.npy", estY)
