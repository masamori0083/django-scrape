from django.urls import path
from . import views

app_name = 'scrape'


urlpatterns = [
    # path("", views.index, name="home")
    path("", views.GetData.as_view(), name="home"),
    # url Dispatcher
    path("download/<uuid:uuid>/", views.downloader, name="downloader")
]
