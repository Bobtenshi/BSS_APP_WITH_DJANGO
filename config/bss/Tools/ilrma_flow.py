from .Function.stft_or import stft, istft
from .Function.auxiva import auxiva
from .Function.ilrma import execute_ip_time_varying_gaussian_ilrma as ilrma
#from .Function.projection_back import projection_back
#from .Function.permutation_solver import solve_pp_by_hungarian
import numpy as np
from sklearn.metrics import mean_squared_error as MSE
from scipy.io.wavfile import write


def main_ilrma(setup_progress_func, update_progress_func, itr):
    stft_separate(setup_progress_func, update_progress_func, itr)

def stft_separate(setup_progress_func, update_progress_func, itr):
    fs = 24000
    LOAD_DIR = 'static/audio/mix/mix_signals.npy'
    data = np.load(LOAD_DIR)
    x = np.zeros([data.shape[1], data.shape[0]], dtype="float32")
    for idx in range(data.shape[0]):
        x[:, idx] = data[idx, :]
    # STFT
    fft_size = 4096
    shift_size = 2048
    X, window = stft(x, fft_size, shift_size)
    np.save('static/audio/separate/window.npy', window)


    #ILRMAの基底数
    n_basis=2
    Nk,Lt,n_sources= X.shape

    #ICAの分離フィルタを初期化
    Wica = np.zeros(shape=(Nk, n_sources, n_sources),dtype=np.complex)
    Wica = Wica+np.eye(n_sources)[None,...]
    Wilrma_ip = Wica.copy()

    #ILRMA用
    b = np.ones(shape=(Nk,n_sources,n_basis))
    a = np.random.uniform(size=(n_basis*n_sources*Lt))
    a = np.reshape(a,(n_basis,n_sources,Lt))


    setup_progress_func()
    print("bss start")
    XtoILRMA = np.transpose(X, (2, 0, 1))#マイクロホン数・周波数・フレーム数
    print(XtoILRMA.shape)

    #IP法に基づくILRMA実行コード
    Wilrma_ip, s_ilrma_ip, cost_buff_ilrma_ip = ilrma(XtoILRMA, Wilrma_ip, a, b, update_progress_func,n_iterations=itr)
    Y = projection_back(s_ilrma_ip, Wilrma_ip)

    print(Y.shape)

    estY = np.transpose(Y[0], (1, 2, 0))
    print("bss done")

    #estY, D = projection_back(Y, X[:, :, 0])
    #np.save('static/audio/separate/mix_signals.npy', X)
    #np.save('static/audio/separate/fdica_signals.npy', estY)

    # ISTFT
    z = istft(estY, shift_size, window, fs * 10)
    #esty = istft(estY, shift_size, window, fs * 10)

    for i in range(data.shape[0]):
        write('static/audio/separate/sep' + str(i+1) + '.wav', fs, z[:, i].astype('float32'))


def projection_back(s_hat,W):

    #ステアリングベクトルを推定
    A=np.linalg.pinv(W)
    c_hat=np.einsum('kmi,ikt->mikt',A,s_hat)
    return(c_hat)