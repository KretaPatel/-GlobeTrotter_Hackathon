from rest_framework import serializers
from .models import City, Activity, Trip, TripStop, ItineraryItem, TripExpense, SavedDestination


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    city_name = serializers.ReadOnlyField(source='city.name')

    class Meta:
        model = Activity
        fields = '__all__'


class ItineraryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryItem
        fields = '__all__'


class TripStopSerializer(serializers.ModelSerializer):
    city_details = CitySerializer(source='city', read_only=True)
    itinerary_items = ItineraryItemSerializer(many=True, read_only=True)

    class Meta:
        model = TripStop
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    stops = TripStopSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()
    destination_count = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ('user', 'share_token', 'created_at', 'updated_at')

    def get_destination_count(self, obj):
        return obj.stops.count()

    def get_total_cost(self, obj):
        itinerary_cost = sum(
            item.cost
            for stop in obj.stops.all()
            for item in stop.itinerary_items.all()
        )
        expense_cost = sum(e.amount for e in obj.expenses.all())
        return float(itinerary_cost + expense_cost)


class TripExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripExpense
        fields = '__all__'
