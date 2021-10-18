from django.shortcuts import HttpResponse, render, get_object_or_404
from django.http import HttpResponse
from .Tools.mix_sound import mix
import functools
from .models import Progress
from .Tools.fdica_flow import main_fdica
from .Tools.iva_flow import main_iva
from .const import N_ITR
from django.http import JsonResponse
import json  # 追加した


# Create your views here.
def index(request):
    # hoge = "Hello Django!!"
    # print(hoge)
    # return render(request, "test_ajax_app/test_ajax_app.html", {
    return render(request, "bss/index.html")


def request_mix(request):
    # print('bee_exp/mix')
    # hoge = request.POST.getlist("name_input_text")[0]# 入力した値を取得
    # print("chose audio:{}".format(hoge))
    # pk = request.POST.getlist("pk")  # 入力した値を取得

    SelectedSourcesList = request.POST.getlist("nameSelectedSources")
    print("Selected audio sources:{}".format(SelectedSourcesList))

    txt = mix(request, SelectedSourcesList)  # mixing

    return render(request, "bss/mix_signal.html", {"txt": txt})


#########
#########


def setup(request):
    """進捗管理インスタンスを作成する"""
    progress = Progress.objects.create()
    data = {
        "pk": progress.pk,
        "N_ITR": N_ITR,
    }
    return JsonResponse(data)
    # return HttpResponse([progress.pk, N_ITR])
    # return HttpResponse([progress.pk, 1])


def show_progress(request):
    """時間のかかる関数を実行する"""
    if "progress_pk" in request.GET:
        # progress_pkが指定されている場合の処理
        progress_pk = request.GET.get("progress_pk")
        progress = get_object_or_404(Progress, pk=progress_pk)
        persent = str(int(progress.now / progress.total * 100)) + "%"
        print(f"{persent} is done...")
        return render(request, "bss/progress_bar.html", {"persent": persent})
    else:
        # progress_pkが指定されていない場合の処理
        print("show_progressがおかしい")
        return HttpResponse("エラー")


def make_progress(pk):
    """引数のプライマリーキーに紐づく進捗を進める"""
    progress = get_object_or_404(Progress, pk=pk)
    progress.now += 1
    progress.save()


def setup_progress(pk, n_itr):
    """引数のプライマリーキーに紐づく進捗を進める"""
    progress = get_object_or_404(Progress, pk=pk)
    progress.total = n_itr

    progress.save()


def set_hikisuu(pk):
    """引数を固定する"""
    return functools.partial(make_progress, pk=pk)


def set_model(pk, n_itr):
    """引数を固定する"""
    return functools.partial(setup_progress, pk=pk, n_itr=n_itr)


def request_cycle_bss(request):
    # print("This is bss process.")
    progress_pk = request.GET.get("progress_pk")
    bss_method = request.GET.get("bss_method")
    itr = request.GET.get("itr")
    n_itr = request.GET.get("n_itr")
    # print(f"bss:{bss_method}, itr/n_itr: {itr}/{n_itr}")

    if bss_method == "IVA":

        #print(f"bss:{bss_method}, itr/n_itr: {itr}/{n_itr}")
        if itr == "1":
            set_model(progress_pk, n_itr)
        main_iva(
            # set_model(progress_pk, n_itr),
            set_hikisuu(progress_pk),
            int(itr),
            int(n_itr),
        )

    # progress_pkが指定されている場合の処理
    progress = get_object_or_404(Progress, pk=progress_pk)
    persent = str(int(progress.now / progress.total * 100)) + "%"
    print(f"now:{progress.now}, total: {progress.total}")
    print(f"{persent} is done...")
    # return [render(request, "bss/progress_bar.html", {"persent": persent}),
    # render(request, "bss/bss_result.html", {"bss_method": bss_method})]
    # print(render(request, "bss/progress_bar.html", {"persent": persent}))

    # return render(request, "bss/progress_bar.html", {"persent": persent})

    return render(request, "bss/bss_result.html", {"bss_method": bss_method})
