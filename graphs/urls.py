from django.urls import path, register_converter
from . import views
from .converters import DateConverter

register_converter(DateConverter, 'date')

urlpatterns = [
    path('', views.index, name="index"),
    path('graphics/<str:typegraph>/<int:year>/<int:month>/', views.graphPage, name="general-page"),

]
