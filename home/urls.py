from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "home"

router = DefaultRouter()
router.register(r'trips', views.TripViewSet, basename='trip')
router.register(r'stops', views.TripStopViewSet, basename='stop')
router.register(r'itinerary-items', views.ItineraryItemViewSet, basename='itinerary-item')
router.register(r'destinations', views.CityViewSet, basename='destination')
router.register(r'cities', views.CityViewSet, basename='city')
router.register(r'activities', views.ActivityViewSet, basename='activity')

urlpatterns = [
    path("", views.index, name="index"),        # Renders the HTML template
    path("api/dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("api/trips/<int:trip_id>/budget/", views.TripBudgetView.as_view(), name="trip_budget"),
    path("api/trips/shared/<uuid:share_token>/", views.SharedTripView.as_view(), name="shared_trip"),
    path("api/trips/shared/<uuid:share_token>/clone/", views.CloneTripView.as_view(), name="clone_trip"),
    path("api/admin/analytics/", views.AdminAnalyticsView.as_view(), name="admin_analytics"),
    path("api/", include(router.urls)),
]

