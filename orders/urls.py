from django.urls import URLPattern, path
from orders import views

urlpatterns = [
    # path('hello', views.hello),
    path('', views.dashboard_view)
]