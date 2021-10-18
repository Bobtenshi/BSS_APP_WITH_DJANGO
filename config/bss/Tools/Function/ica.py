

import wave as wave
import pyroomacoustics as pa
import numpy as np
import scipy.signal as sp
import scipy as scipy
import matplotlib.pyplot as plt
#順列計算に使用
import itertools as itertools

#コントラスト関数の微分（球対称ラプラス分布を仮定）
#s_hat: 分離信号(M, Nk, Lt)
def phi_laplacian(s_hat):

    norm=np.abs(s_hat)
    phi=s_hat/np.maximum(norm,1.e-18)
    return(phi)

#コントラスト関数（球対称ラプラス分布を仮定）
#s_hat: 分離信号(M, Nk, Lt)
def contrast_laplacian(s_hat):
    norm=2.*np.abs(s_hat)
    return(norm)

#ICAによる分離フィルタ更新
#x:入力信号( M, Nk, Lt) mic, source_num, sample length
#W: 分離フィルタ(Nk,M,M)
#mu: 更新係数
#n_ica_iterations: 繰り返しステップ数
#phi_func: コントラスト関数の微分を与える関数
#contrast_func: コントラスト関数
#is_use_non_holonomic: True (非ホロノミック拘束を用いる） False (用いない）
#return W 分離フィルタ(Nk,M,M) s_hat 出力信号(M,Nk, Lt),cost_buff ICAのコスト (T)
def execute_natural_gradient_ica(x,W,phi_func=phi_laplacian,contrast_func=contrast_laplacian,mu=1.0,n_ica_iterations=20,is_use_non_holonomic=True):

    #マイクロホン数を取得する
    M=np.shape(x)[0]

    cost_buff=[]
    for t in range(n_ica_iterations):
        #音源分離信号を得る
        s_hat=np.einsum('kmn,nkt->mkt',W,x)

        #コントラスト関数を計算
        G=contrast_func(s_hat)

        #コスト計算
        cost=np.sum(np.mean(G,axis=-1))-np.sum(2.*np.log(np.abs(np.linalg.det(W)) ))
        cost_buff.append(cost)

        #コンストラクト関数の微分を取得
        phi=phi_func(s_hat)

        phi_s=np.einsum('mkt,nkt->ktmn',phi,np.conjugate(s_hat))
        phi_s=np.mean(phi_s,axis=1)

        I=np.eye(M,M)
        if is_use_non_holonomic==False:
            deltaW=np.einsum('kmi,kin->kmn',I[None,...]-phi_s,W)
        else:
            mask=(np.ones((M,M))-I)[None,...]
            deltaW=np.einsum('kmi,kin->kmn',np.multiply(mask,-phi_s),W)
        #フィルタを更新する
        W=W+mu*deltaW

    #最後に出力信号を分離
    s_hat=np.einsum('kmn,nkt->mkt',W,x)
    return(W,s_hat,cost_buff)

def makesinsig(freq):
  fs = 16000
  time = 10
  numsamples = time * fs
  x=np.linspace(0, time, numsamples+1) #0≦t≦timeをnumsamples等分
  y=np.sin(2 * np.pi * freq * x)
  #f, t, Y = sp.stft(y, fs)
  #plt.pcolormesh(t, f, np.abs(Y), shading='gouraud')
  #plt.show()
  return y

if __name__ == "__main__":

  s1 = makesinsig(freq=440)
  s2 = makesinsig(freq=1280)

  x1 = 0.8*s1 + 0.2*s2
  x2 = 0.3*s1 + 0.7*s2

  f, t, X = sp.stft(x1, fs = 16000)
  plt.pcolormesh(t, f, np.abs(X), shading='gouraud')
  plt.show()

  execute_natural_gradient_ica()



































