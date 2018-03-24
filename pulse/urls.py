"""pulse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from ftp import views as ftp_views

urlpatterns = [
    path('login/', auth_views.login, {'template_name': 'ftp/login.html'}, name='login'),
    path('logout/', auth_views.logout, {'next_page': 'index'}, name='logout'),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='select_analyses'), name="index"),
    path('tests/', ftp_views.select_analyses_view, name='select_analyses'),
    path('tests/lactate/', ftp_views.lactate_threshold_view, name='lactate_analyses'),
    path('tests/success/', ftp_views.analyses_success_view, name='analyses_success'),
    path('download/', ftp_views.download_file_view, name='download_file'),
]
