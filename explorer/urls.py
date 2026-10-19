from django.urls import path

from . import views

urlpatterns = [
    path("render/", views.render_fractal, name="render"),
]
