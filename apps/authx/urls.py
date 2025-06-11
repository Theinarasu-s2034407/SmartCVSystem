from django.urls import path
from .views import LogoutView, ForgetView, AccountView, SearchView, LoginView, RegisterView

app_name = "authx"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forget/", ForgetView.as_view(), name="forget"),
    path("account/", AccountView.as_view(), name="account"),
    path("search/", SearchView.as_view(), name="search"),
]
