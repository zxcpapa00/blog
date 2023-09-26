from django.urls import path
from .views import SignUpView, CustomLoginView, profile, PasswordChangeView

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', profile, name='user-profile'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
]

