from django.urls import path
from . import views
from django.views.generic.base import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

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

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
