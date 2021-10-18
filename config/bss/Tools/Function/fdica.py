import numpy as np
import tqdm
import time
from .common import projection_back


EPS = 2.2204e-14


def tensor_H(A):
    """Compute Hermitian transpose for tensor."""
    return np.conj(A).swapaxes(-2, -1)


def cost_function(P, R, W, n_freq, n_frame):
    A = np.zeros([n_freq, 1])
    for i in range(n_freq):
        x = np.abs(np.linalg.det(W[:, :, i]))
        x = max(x, 1e-10)
        A[i] = 2 * np.log(x)
    return -n_frame * A.sum() + (P / R + np.log(R)).sum()


def itr_save(Yp, Xp, t1, Y_list, time_list):
    tmp_Y = Yp.transpose([1, 2, 0]).copy()
    tmp_X = Xp.transpose([1, 2, 0]).copy()
    z = projection_back(tmp_Y, tmp_X[:, :, 0])  # (f,m)
    tmp_Y *= np.conj(z[None, :, :])
    t2 = time.time()
    Y_list.append(tmp_Y.transpose([1, 0, 2]).copy())
    time_list.append(t2 - t1)
    return Y_list, time_list


def FDICA(X, itr, update_progress_func):
    """% [inputs]
    %         X: observed multichannel spectrogram (freq. x time frames x channels)
    %       itr: number of iterations (scalar)
    %  drawCost: draw convergence behavior or not (true/false)
    %
    % [outputs]
    %         Y: estimated signals (freq. x time frames x channels)
    %         W: demixing matrix (source x channel x freq.)
    %"""

    n_freq, n_frame, n_src = X.shape
    W = np.zeros([n_freq, n_src, n_src], dtype="complex")
    Y = X.copy()
    for i in range(n_freq):
        W[i, :, :] = np.eye(n_src)

    # (n_freq, n_src, n_frame)
    Xp = np.transpose(X, [0, 2, 1])
    Yp = np.transpose(Y, [0, 2, 1])

    t1 = time.time()
    for it in tqdm.tqdm(range(itr)):
        update_progress_func()
        Yp = W @ Xp
        for m in range(n_src):
            # (n_freq, n_frame)
            rm = np.maximum(abs(Yp[:, m, :]), EPS)

            # (n_freq, n_src, n_src)
            Vk = (Xp / rm[:, None, :]) @ tensor_H(Xp) / n_frame

            # (n_freq, n_src)
            wm = np.linalg.solve(W @ Vk, np.eye(n_src)[None, :, m])

            # (n_freq, 1, 1)
            denom = tensor_H(wm[:, :, None]) @ Vk @ wm[:, :, None]

            W[:, m, :] = wm.conj() / np.sqrt(denom[:, :, 0])

        #if it % save_freq == 0 and it != 0:
            #Y_list, time_list = itr_save(Yp, Xp, t1, Y_list, time_list)

    # PROJECTION BACK
    # (n_frame, n_freq, n_src)
    tmp_Y = Yp.transpose([2, 0, 1]).copy()
    tmp_X = Xp.transpose([2, 0, 1]).copy()

    # (n_freq, n_src)
    z = projection_back(tmp_Y, tmp_X[:, :, 0])
    tmp_Y *= np.conj(z[None, :, :])

    # (n_freq, n_frame, n_src)
    return tmp_Y.transpose([1, 0, 2]), W#, Y_list, time_list