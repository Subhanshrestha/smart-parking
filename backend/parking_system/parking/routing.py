from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/parking/', consumers.ParkingConsumer.as_asgi()),
]
