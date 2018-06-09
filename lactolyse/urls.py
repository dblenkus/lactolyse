from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('login/', auth_views.login, {'template_name': 'lactolyse/login.html'}, name='login'),
    path('logout/', auth_views.logout, {'next_page': 'index'}, name='logout'),

    path('', RedirectView.as_view(pattern_name='select_analyses'), name="index"),
    path('tests/', views.select_analyses_view, name='select_analyses'),
    path('tests/lactate/', views.lactate_threshold_view, name='lactate_analyses'),
    path('tests/success/', views.analyses_success_view, name='analyses_success'),
    path('download/', views.download_file_view, name='download_file'),
]
