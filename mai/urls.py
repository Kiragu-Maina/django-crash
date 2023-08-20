from django.urls import path
from .views import Home, get_new_crash_point

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path('get-new-crash-point/', get_new_crash_point, name='get_new_crash_point')
]
