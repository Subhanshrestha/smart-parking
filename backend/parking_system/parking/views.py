
# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PermitType, ParkingLot, ParkingSpot, Event, Session
from .serializers import (
    PermitTypeSerializer,
    ParkingLotSerializer,
    ParkingSpotSerializer,
    EventSerializer,
    SessionSerializer
)


class ParkingLotViewSet(viewsets.ModelViewSet):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer


class ParkingSpotViewSet(viewsets.ModelViewSet):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer


class PermitTypeViewSet(viewsets.ModelViewSet):
    queryset = PermitType.objects.all()
    serializer_class = PermitTypeSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


@api_view(['GET'])
def dashboard_summary(request):
    """Quick summary endpoint for the frontend dashboard."""
    lots = ParkingLot.objects.all()
    data = []
    for lot in lots:
        total = lot.spots.count()
        available = lot.spots.filter(availability=True).count()
        data.append({
            'id': lot.parking_lot_id,
            'name': lot.parking_lot_name,
            'total_spots': total,
            'available_spots': available,
            'occupancy_percent': round((total - available) / total * 100, 1) if total > 0 else 0
        })
    return Response(data)