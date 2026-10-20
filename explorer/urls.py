from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("render/", views.render_fractal, name="render"),
    path("data/", views.fractal_data, name="data"),
]
