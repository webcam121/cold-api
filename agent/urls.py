"""agent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from agent.apps.accounts.views import (
    AuthenticationTokenView,
    CustomLoginView,
    CustomRegisterView,
    CustomRegisterWithPasswordView, SetUserPasswordView,
    UserUnsubscribeView,
)

admin.site.site_header = "Agent Admin Dashboard"
admin.site.site_title = "Agent Admin"

urlpatterns = [
    path('outbound-call-sessions/', include('agent.apps.call_sessions.urls', namespace='call_sessions')),
    path('admin/', admin.site.urls),
    path('health', include('health_check.urls')),
    path('api/v1/', include('apis.urls', namespace='api')),
    path('api/v1.1/auth/login/', CustomLoginView.as_view()),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', CustomRegisterView.as_view()),
    path('api/v1/auth/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/v1/auth/signup/', CustomRegisterWithPasswordView.as_view()),
    path('api/v1/token/authenticate/', AuthenticationTokenView.as_view()),
    # include routes for Simple JWT’s TokenObtainPairView and TokenRefreshView
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/password_set/', SetUserPasswordView.as_view(), name='set_password'),
    path('api/v1/users/unsubscribe/<str:email>/<str:unsub_token>/', UserUnsubscribeView.as_view(), name='unsubscribe'),

]
