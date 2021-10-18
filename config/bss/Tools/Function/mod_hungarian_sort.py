from munkres import Munkres
import numpy as np
import glob
import os
from sklearn.metrics import mean_squared_error as MSE
import random
import pandas as pd
import copy
import itertools
import time
#m = Munkres()
#res = m.compute(mat)
# print(res)# output

def full_search(mat):
    nch = mat.shape[0]
    cost = 100
    # 全組み合わせを取得
    per_list = list(itertools.permutations(np.arange(nch)))

    for lists in per_list:
        tmp_cost = 0
        for idx, order in enumerate(lists):
            tmp_cost += mat[idx, order]
        if tmp_cost < cost:
            cost = tmp_cost
            permutation = lists
    return permutation


def calc_sim(freq, ref, target, Y_means, abs_Y, method):
    if method == "CORR":
        # 遅い？
        #ref_Y_mean = Y_means[ref]
        ref_Y_mean = pd.Series(Y_means[ref])
        target_Y = pd.Series(abs_Y[freq, :, target])
        #target_Y = pd.Series(abs_Y[freq, :, target])
        corr = -(target_Y.corr(ref_Y_mean))
        if np.isnan(corr):
            return 0

        return corr

    else:
        print("params:method didn't matting!!")


def hungarian_ps(X, method):
    Y = X[:, :, :].copy()

    freq, time_frame, ch = X.shape
    Hungarian = Munkres()
    change = 1
    epoqh = 0
    process_time = 0

    while change >= 1:  # 変更がなくなるまで繰り返し
        # epoqh in range(100):
        change = 0
        epoqh += 1
        tmp_Y = np.zeros_like(X, dtype=complex)
        abs_Y = np.abs(Y[:, :, :].copy())
        # 現在の平均を計算
        Y_means = []
        for i in range(ch):
            #Y_means.append(pd.Series(np.mean(abs_Y[:,:,i], axis=0)))
            Y_means.append(np.mean(abs_Y[:, :, i], axis=0))

        # 全周波数を走査
        for f in range(freq):
            # こっちのが速い？
            ref_target_Y = copy.deepcopy(Y_means)
            for i in range(ch):
                ref_target_Y.append(abs_Y[f, :, i])
            hungarian_mat_fast = np.corrcoef(np.array(ref_target_Y))[ch:, :ch]

            if method == 'Hungarian':
                # ハンガリアンで解く
                t0 = time.time()
                res_list_Hungarian = Hungarian.compute(-hungarian_mat_fast.T)
                t1 = time.time()
                process_time += t1-t0
                # 並び替え
                for ref, target in res_list_Hungarian:
                    tmp_Y[f, :, ref] = Y[f, :, target].copy()
                    if ref != target:
                        change += 1

        # Yを更新
        Y = tmp_Y.copy()
        #print('epoqh:{}, change:{}'.format(epoqh, change))
        # if change < 3:
        # tft.spectrogram(np.abs(Y[:,:,0]))
        # stft.spectrogram(np.abs(Y[:,:,1]))
    return X, Y, process_time


if __name__ == "__main__":
    SAMPLE_DIR = './Inputs/stft_spec/3/*'
    for f in glob.glob(SAMPLE_DIR):
        # Load file
        print(os.path.split(f))
        data = np.load(f)
        #S = data[0,:,:,:]
        X = data[1, :, :, :]

        X, Y = hungarian_ps(X)
