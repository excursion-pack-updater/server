from django.conf.urls import url

from . import views

app_name = "epu"
urlpatterns = [
    url(r"generated_password/?$", views.generatePassword, name="generatedPassword"),
    url(r"login/(?P<key>[a-zA-Z0-9]+)?$", views.login, name="login"),
    url(r"logout/$", views.logout, name="logout"),
    url(r"pack/(?P<id>[0-9]+)", views.pack, name="pack_detail"),
    url(r"$", views.index, name="index"),
]
