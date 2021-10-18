import wave as wave
import pyroomacoustics as pa
import numpy as np
import scipy.signal as sp
import scipy as scipy

#順列計算に使用
import itertools
import time

#IP法による分離フィルタ更新
#x:入力信号( M, Nk, Lt)
#W: 分離フィルタ(Nk,M,M)
#a: アクティビティ(B,M,Lt)
#b: 基底(Nk,M,B)
#n_iterations: 繰り返しステップ数
#return W 分離フィルタ(Nk,M,M) s_hat 出力信号(M,Nk, Lt),cost_buff コスト (T)
def execute_ip_time_varying_gaussian_ilrma(x,W,a,b,update_progress_func,n_iterations=20):

    #マイクロホン数・周波数・フレーム数を取得する
    M=np.shape(x)[0]
    Nk=np.shape(x)[1]
    Lt=np.shape(x)[2]

    cost_buff=[]
    for t in range(n_iterations):

        update_progress_func()
        #音源分離信号を得る
        s_hat=np.einsum('kmn,nkt->mkt',W,x)
        s_power=np.square(np.abs(s_hat))

        #時間周波数分散を更新
        v=np.einsum("bst,ksb->skt",a,b)

        #アクティビティの更新
        a=a*np.sqrt(np.einsum("ksb,skt->bst",b,s_power/np.maximum(v,1.e-18)**2)/np.einsum("ksb,skt->bst",b,1./np.maximum(v,1.e-18)))

        #基底の更新
        b=b*np.sqrt(np.einsum("bst,skt->ksb",a,s_power /np.maximum(v,1.e-18)**2) /np.einsum("bst,skt->ksb",a,1./np.maximum(v,1.e-18)))

        #時間周波数分散を再度更新
        v=np.einsum("bst,ksb->skt",a,b)

        #コスト計算
        cost=np.sum(np.mean(s_power/np.maximum(v,1.e-18)+np.log(v),axis=-1)) -np.sum(2.*np.log(np.abs(np.linalg.det(W)) ))
        cost_buff.append(cost)

        #IP法による更新
        Q=np.einsum('skt,mkt,nkt->tksmn',1./np.maximum(v,1.e-18),x,np.conjugate(x))
        Q=np.average(Q,axis=0)

        for source_index in range(M):
            WQ=np.einsum('kmi,kin->kmn',W,Q[:,source_index,:,:])
            invWQ=np.linalg.pinv(WQ)
            W[:,source_index,:]=np.conjugate(invWQ[:,:,source_index])
            wVw=np.einsum('km,kmn,kn->k',W[:,source_index,:],Q[:,source_index,:,:],np.conjugate(W[:,source_index,:]))
            wVw=np.sqrt(np.abs(wVw))
            W[:,source_index,:]=W[:,source_index,:]/np.maximum(wVw[:,None],1.e-18)


    s_hat=np.einsum('kmn,nkt->mkt',W,x)

    return(W,s_hat,cost_buff)