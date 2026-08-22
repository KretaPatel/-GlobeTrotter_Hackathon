from django.contrib import admin
from .models import City, Activity, Trip, TripStop, ItineraryItem, TripExpense, SavedDestination

admin.site.register(City)
admin.site.register(Activity)
admin.site.register(Trip)
admin.site.register(TripStop)
admin.site.register(ItineraryItem)
admin.site.register(TripExpense)
admin.site.register(SavedDestination)
