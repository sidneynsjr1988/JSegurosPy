from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from .views import UserListCreateAPIView, ChangePasswordView, UserRetrieveUpdateDeleteView

urlpatterns = [
    path('users/', UserListCreateAPIView.as_view(), name="users"),
    path('users/<int:pk>/', UserRetrieveUpdateDeleteView.as_view(),
         name="user_details"),
    path('change_password/', ChangePasswordView.as_view(), name="change_password"),
    path('token/', ObtainAuthToken.as_view(), name="token")
]
