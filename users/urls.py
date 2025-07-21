from django.urls import path, include
from .views import *

urlpatterns = [
    path('register-user/', RegisterUserView.as_view()),
    path('login/', LoginUserView.as_view()),
    path('logout/', LogoutUserView.as_view()),
    path('get-access-token/', GetAccessTokenView.as_view())
    
]