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
import interviews.views as views

from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('api/login', views.LoginView.as_view()),
    path('api/interviewee', views.IntervieweeDetails.as_view()),
    path('api/interviewer', views.InterviewerDetails.as_view()),
    path('api/interviewertimes', views.InterviewerSlotList.as_view()),
    path('api/intervieweetimes', views.IntervieweeSlotList.as_view()),
    path('api/interviewtimes', views.InterviewDetails.as_view()),
    path('api/interviewertimes/update', views.InterviewerOpen.as_view()),
    path('api/intervieweetimes/update', views.IntervieweeOpen.as_view()),
    path('api/changepassword', views.ChangePassword.as_view()),
    # path('api/resetpassword', views.reset_password),
    # path('api/resetpassword/confirm/<uidb64>/<token>', views.reset_password_confirm, name='password_reset_confirm'),

    # for creating interview times
    path('api/createtimes', views.CreateTimes.as_view()),

    path('api/sendemail', views.SendEmail.as_view()),

    path('csv/interviewees', views.CSVInterviewees.as_view()),
    path('csv/interviewers', views.CSVInterviewers.as_view()),
]
