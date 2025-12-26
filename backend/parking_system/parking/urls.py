from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'lots', views.ParkingLotViewSet)
router.register(r'spots', views.ParkingSpotViewSet)
router.register(r'permits', views.PermitTypeViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'sessions', views.SessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_summary, name='dashboard-summary'),
]