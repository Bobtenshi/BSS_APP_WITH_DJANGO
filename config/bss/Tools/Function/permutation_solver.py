import numpy as np
from sklearn.metrics import mean_squared_error as MSE
from.stft_or import stft, istft, whitening,spectrogram
from scipy.io.wavfile import write
from .mod_hungarian_sort import hungarian_ps
from tqdm import tqdm

# export HYDRA_FULL_ERROR=1
# python main.py model.batch_size=1,2,4,8,16 stft.mic_num=1,2,3 -m
# pipenv run mlflow ui

# def solve_pp_by_hungarian(file_num, nch, shift_size, fs, method, subband, PROJECT_ROOT):


def solve_pp_by_hungarian():

    #nch = cfg.stft.mic_num
    #shift_size = cfg.stft.shift_size
    #fs = cfg.stft.fs
    #method = cfg.stft.method

    nch = 2
    shift_size = 2048
    fs = 24000
    method = 'Hungarian'

    # 合計値(total)を設定
    LOAD_DIR = 'static/audio/separate/fdica_signals.npy'
    estY = np.load(LOAD_DIR)
    LOAD_DIR = 'static/audio/separate/window.npy'
    window = np.load(LOAD_DIR)
    #t0 = time.time()

    if np.count_nonzero(np.isnan(estY)) != 0:
        print('{}_data is NAN'.format(np.count_nonzero(np.isnan(estY))))

        for f in range(estY.shape[0]):
            if np.count_nonzero(np.isnan(estY[f, :, :])) != 0:
                for t in range(estY.shape[1]):
                    for ch in range(estY.shape[2]):
                        np.nan_to_num(
                            estY[f, t, ch], nan=np.random.normal(0, 0.1), copy=False)
        #print('{}_data is NAN'.format(np.count_nonzero(np.isnan(estY))))
        np.nan_to_num(estY, nan=np.random.normal(0, 0.1), copy=False)
        print('{}_data is NAN'.format(np.count_nonzero(np.isnan(estY))))

    # パーミュテーション解決
    # estY,Z = H_sort(estY, method, subband)
    estY, Z, process_time = hungarian_ps(estY, method)

    # ISTFT
    z = istft(Z, shift_size, window, fs * 10)
    esty = istft(estY, shift_size, window, fs * 10)

    for i in range(nch):
        write('static/audio/separate/sep' +
              str(i+1) + '.wav', 24000, z[:, i].astype('float32'))
    np.save('static/audio/separate/fdica_z.npy', z)


if __name__ == "__main__":
    main()
