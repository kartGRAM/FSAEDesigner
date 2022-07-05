from django.urls import path
from . import views
from . import views_drf as drf
from django.views.generic.base import TemplateView
from django.conf import settings

app_name = 'FSAEDesigner'
urlpatterns = [
    path('', views.Top.as_view(), name='top'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('terms/', TemplateView.as_view(template_name='FSAEDesigner/terms.html'), name="terms"),
    path('user_create/complete/<token>/',
         views.UserCreateComplete, name='user_create_complete'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/confirm/<uidb64>/<token>/',
         views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('email/change/complete/<str:token>/',
         views.EmailChangeComplete, name='email_change_complete'),

    path('api/check_logged_in/', drf.checkLoggedIn, name='check_logged_in'),
    path('api/gd/save_as/', drf.gdSaveAs, name='gd_save_as'),
]

if settings.DEBUG:
    urlpatterns.append(path('react/', views.React, name='react')),
