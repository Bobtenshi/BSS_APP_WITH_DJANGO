import random
from scipy.io.wavfile import write
import itertools
import copy
from scipy.io.wavfile import read, write
import numpy as np
#import pyroomacoustics as pra
#import librosa


def test():
    print("test_import")


def mix(request, selectedSourcesList):
    # inputs:
    #   -selectedSourcesList: e.g. ["1", "2"]
    #
    #
    #
    #

    if len(selectedSourcesList) == 2:
        # make_revarb_sounds(selectedSourcesList)
        return (
            "audio"
            + selectedSourcesList[0]
            + " and audio"
            + selectedSourcesList[1]
            + " are mixed."
        )
    else:
        return "ERRORE: Please select 2 sources."


def make_room(nch, rt60, room_dim):
    e_absorption, max_order = pra.inverse_sabine(rt60, room_dim)
    room = pra.ShoeBox(
        room_dim,
        fs=24000,
        materials=pra.Material(e_absorption),
        max_order=3,
        ray_tracing=True,
        air_absorption=True,
    )
    # レイトレーシングをアクティブにする
    # room.set_ray_tracing()
    # マイクの座標を与える

    mic_locs = np.array([4.0, 1.2, 1.2], dtype=float)
    for i in range(nch - 1):
        mic_locs = np.c_[mic_locs, [4.0 + (i + 1) * 0.06, 1.2, 1.2]]
    # room にマイクを追加します
    room.add_microphone_array(mic_locs)
    return room


def choice_sounds_pos(nch, room_dim):

    pos_list = []
    x_range = room_dim[0] / nch
    for i in range(nch):
        sound_x_pos = np.arange(x_range * i + 0.5, x_range * (i + 1) - 0.5, 0.2)
        sound_y_pos = np.arange(2, 5, 0.5)
        sound_z_pos = np.arange(1, 2, 0.2)
        room_glids = list(itertools.product(sound_x_pos, sound_y_pos, sound_z_pos))
        pos_list.append(random.sample(room_glids, 1))

    return pos_list


def make_revarb_sounds(selectedSourcesList):
    # 残響時間と部屋の寸法
    rt60 = 0.45  # seconds
    room_dim = [9.0, 6.0, 3.5]
    nch = 2
    # fs = 24000

    # wavファイルを読み込んで配置してみます
    dry_signal_list = []
    delay = []
    # choice_list = random.sample(list(range(100)), nch)
    # choice_list = [audio1, audio2]

    # 各音声信号（単体）を選択
    for m in selectedSourcesList:
        fs, signal = read("static/audio/original/speech" + str(m) + ".wav")
        dry_signal_list.append(signal)
        delay.append(random.uniform(0, 1.5))
        # dry_signal_list.append(signal / 32768.0)

    # 音源位置の範囲指定　グリッド配置
    sounds_pos_list = choice_sounds_pos(nch, room_dim)
    # 各音声信号（単体）をシミュレーション　SDR評価用
    ref_signals = []
    for i in range(nch):
        # 部屋を作成
        room = make_room(nch, rt60, room_dim)
        # 音源配置
        room.add_source(
            np.array(sounds_pos_list[i]).reshape([-1]),
            signal=dry_signal_list[i],
            delay=delay[i],
        )

        # シミュレーション音源を生成
        room.simulate()
        ref_signals.append(room.mic_array.signals[:, : fs * 10])

    # mixture
    mix_signals = copy.deepcopy(ref_signals[nch - 1])
    for i in range(nch):
        mix_signals += ref_signals[i]

    # show in html
    for i in range(nch):
        write(
            "static/audio/mix/mix" + str(i) + ".wav",
            fs,
            mix_signals[i, :].astype("float32"),
        )

    # for bss
    np.save("static/audio/mix/ref_signals.npy", ref_signals)
    np.save("static/audio/mix/mix_signals.npy", mix_signals)
