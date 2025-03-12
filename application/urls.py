from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('ask-manual/', views.ask_manual, name='ask_manual'),
    path('api/login/', views.login, name='login'),
    path('api/register/', views.register, name='register'),
]
