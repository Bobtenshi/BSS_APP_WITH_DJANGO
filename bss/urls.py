from django.urls import path
from . import views

app_name = "bss"
urlpatterns = [
    path("", views.index, name="index"),
    path("mix/", views.request_mix, name="mix"),
    #path("bss/", views.request_bss, name="bss"),
    path("bss/", views.request_cycle_bss, name="cycle_bss"),
    # model update
    path("setup/", views.setup, name="setup"),
    path("show_progress/", views.show_progress, name="show_progress"),
    # path("do_something/", views.do_something, name="do_something"),
]
