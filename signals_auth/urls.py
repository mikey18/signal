from django.urls import path
from .views import (RegisterView,
                    LoginAPIView,
                    UserView,
                    UpdateUser,
                    LogoutAPIView,
                    Connect_MT5_Account,
                    Activate_Automation,
                    Get_Broker_ServersAPI)

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/',LoginAPIView.as_view(),name="login"),
    path('update-user/',UpdateUser.as_view(),name="update user"),
    path('user/',UserView.as_view(),name="login"),
    path('connect/', Connect_MT5_Account.as_view(), name="connect"),
    path('automation/', Activate_Automation.as_view(), name="automation"),
    path('brokers/', Get_Broker_ServersAPI.as_view(), name='brokers-list'),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    # path('sse/', SSE.as_view(), name="SSE"),
]