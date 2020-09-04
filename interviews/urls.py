"""interviews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('api/login', views.login_view),
    path('api/interviewee', views.interviewee_details),
    path('api/interviewer', views.interviewer_details),
    path('api/interviewertimes', views.interviewer_slot_list),
    path('api/intervieweetimes', views.interviewee_slot_list),
    path('api/interviewtimes', views.interview_details),
    path('api/interviewertimes/update', views.interviewer_open),
    path('api/intervieweetimes/update', views.interviewee_open),
    path('api/changepassword', views.change_password),
    # path('api/resetpassword', views.reset_password),
    # path('api/resetpassword/confirm/<uidb64>/<token>', views.reset_password_confirm, name='password_reset_confirm'),

    # for creating interview times
    path('api/createtimes', views.create_times),

    path('csv/interviewees', views.csv_interviewees),
    path('csv/interviewers', views.csv_interviewers),
]
