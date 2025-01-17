from django.urls import path
from .views import SignUpView, login, callback

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', login, name='login'),
    path('callback/', callback, name='callback'),
]
