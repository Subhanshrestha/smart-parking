from rest_framework import serializers
from .models import PermitType, ParkingLot, ParkingSpot, Event, Session


class PermitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermitType
        fields = '__all__'


class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = '__all__'


class ParkingLotSerializer(serializers.ModelSerializer):
    spots = ParkingSpotSerializer(many=True, read_only=True)
    available_spots = serializers.SerializerMethodField()
    total_spots = serializers.SerializerMethodField()

    class Meta:
        model = ParkingLot
        fields = ['parking_lot_id', 'parking_lot_name', 'occupancy', 'total_spots', 'available_spots', 'spots']

    def get_available_spots(self, obj):
        return obj.spots.filter(availability=True).count()

    def get_total_spots(self, obj):
        return obj.spots.count()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'