"""Lactolyse URL configuration."""
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [  # pylint: disable=invalid-name
    path('', RedirectView.as_view(pattern_name='select_analyses'), name="index"),
    path('tests/', views.select_analyses_view, name='select_analyses'),
    path('tests/lactate/', views.lactate_threshold_view, name='lactate_analyses'),
    path('tests/success/', views.analyses_success_view, name='analyses_success'),
    path(
        'download/lactate_threshold/<int:pk>/',
        views.lactate_threshold_download_view,
        name='download_lactate_threshold'
    ),
]
