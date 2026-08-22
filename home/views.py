from .serializers import (
    CitySerializer, ActivitySerializer, TripSerializer,
    TripStopSerializer, ItineraryItemSerializer, TripExpenseSerializer
)
from .models import City, Activity, Trip, TripStop, ItineraryItem, TripExpense, SavedDestination
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count
from django.shortcuts import render


def index(request):
    return render(request, "home/index.html")


# 2. Dashboard / Home Screen View


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        recent_trips = Trip.objects.filter(
            user=user).order_by('-start_date')[:3]
        popular_cities = City.objects.order_by('-popularity_score')[:6]
        total_trips = Trip.objects.filter(user=user).count()

        return Response({
            "welcome_message": f"Welcome back, {user.first_name or user.username}!",
            "summary": {"total_trips": total_trips},
            "recent_trips": TripSerializer(recent_trips, many=True).data,
            "recommended_destinations": CitySerializer(popular_cities, many=True).data,
        })

# 3 & 4. Trip CRUD (Create, List, Update, Delete)


class TripViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TripSerializer

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 5. Itinerary Builder (Stops & Day items)


class TripStopViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TripStopSerializer

    def get_queryset(self):
        return TripStop.objects.filter(trip__user=self.request.user)


class ItineraryItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ItineraryItemSerializer

    def get_queryset(self):
        return ItineraryItem.objects.filter(stop__trip__user=self.request.user)

# 7. City Search & Discovery


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        qs = City.objects.all()
        search = self.request.query_params.get('search')
        region = self.request.query_params.get('region')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(
                country__icontains=search)
        if region:
            qs = qs.filter(region__iexact=region)
        return qs.order_by('-popularity_score')

# 8. Activity Search & Discovery


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = Activity.objects.all()
        city_id = self.request.query_params.get('city_id')
        category = self.request.query_params.get('category')
        max_cost = self.request.query_params.get('max_cost')
        if city_id:
            qs = qs.filter(city_id=city_id)
        if category:
            qs = qs.filter(category=category)
        if max_cost:
            qs = qs.filter(cost__lte=max_cost)
        return qs

# 9. Trip Budget & Financial Breakdown


class TripBudgetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        breakdown = {
            'transport': 0.0,
            'stay': 0.0,
            'activities': 0.0,
            'meals': 0.0,
            'other': 0.0,
        }
        # Aggregate from itinerary items
        for stop in trip.stops.all():
            for item in stop.itinerary_items.all():
                cat = item.category if item.category in breakdown else 'other'
                breakdown[cat] += float(item.cost)

        # Aggregate from explicit expenses
        for exp in trip.expenses.all():
            cat = exp.category if exp.category in breakdown else 'other'
            breakdown[cat] += float(exp.amount)

        total_spent = sum(breakdown.values())
        days = max((trip.end_date - trip.start_date).days, 1)

        return Response({
            "budget_limit": float(trip.budget_limit),
            "total_spent": total_spent,
            "remaining_budget": float(trip.budget_limit) - total_spent,
            "average_cost_per_day": round(total_spent / days, 2),
            "is_overbudget": total_spent > float(trip.budget_limit),
            "breakdown": breakdown
        })

# 11. Shared / Public Itinerary & Clone ("Copy Trip")


class SharedTripView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, share_token):
        trip = get_object_or_404(Trip, share_token=share_token, is_public=True)
        return Response(TripSerializer(trip).data)


class CloneTripView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, share_token):
        original = get_object_or_404(
            Trip, share_token=share_token, is_public=True)
        # Duplicate trip
        cloned_trip = Trip.objects.create(
            user=request.user,
            name=f"Copy of {original.name}",
            description=original.description,
            start_date=original.start_date,
            end_date=original.end_date,
            budget_limit=original.budget_limit,
            cover_photo=original.cover_photo,
            is_public=False
        )
        # Duplicate stops & activities
        for stop in original.stops.all():
            new_stop = TripStop.objects.create(
                trip=cloned_trip,
                city=stop.city,
                arrival_date=stop.arrival_date,
                departure_date=stop.departure_date,
                order=stop.order
            )
            for item in stop.itinerary_items.all():
                ItineraryItem.objects.create(
                    stop=new_stop,
                    activity=item.activity,
                    title=item.title,
                    category=item.category,
                    date=item.date,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    cost=item.cost,
                    order=item.order,
                    notes=item.notes
                )
        return Response(TripSerializer(cloned_trip).data, status=status.HTTP_201_CREATED)

# 13. Admin / Analytics Dashboard


class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "total_trips": Trip.objects.count(),
            "total_users": request.user.__class__.objects.count(),
            "top_destinations": City.objects.annotate(trip_count=Count('tripstop')).order_by('-trip_count')[:5].values('name', 'country', 'trip_count'),
            "top_activities": Activity.objects.annotate(use_count=Count('itineraryitem')).order_by('-use_count')[:5].values('title', 'use_count'),
        })
