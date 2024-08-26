from django.urls import path
from .views import (
    RegisterView,
    LoginAPIView,
    UserView,
    UpdateUser,
    LogoutAPIView,
    RefreshTokenView,
    VerifyOTP,
    ResetPasswordAPI,
    ChangePasswordAPI,
    # Connect_MT5_Account,
    # Activate_Automation,
    # Get_Broker_ServersAPI,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/", VerifyOTP.as_view(), name="verify"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("forgot-password/", ResetPasswordAPI.as_view(), name="forgot-password"),
    path("change-password/", ChangePasswordAPI.as_view(), name="change-password"),
    path("update-user/", UpdateUser.as_view(), name="update user"),
    path("user/", UserView.as_view(), name="user view"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # path("connect/", Connect_MT5_Account.as_view(), name="connect"),
    # path("automation/", Activate_Automation.as_view(), name="automation"),
    # path("brokers/", Get_Broker_ServersAPI.as_view(), name="brokers-list"),
    # path('sse/', SSE.as_view(), name="SSE"),
]
