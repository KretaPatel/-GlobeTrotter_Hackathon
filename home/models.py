import uuid
from django.db import models
from django.conf import settings


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cost_index = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.0)  # 1.0 = avg, >1 = expensive
    popularity_score = models.IntegerField(default=50)  # 0 - 100
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.country}"


class Activity(models.Model):
    CATEGORY_CHOICES = [
        ('sightseeing', 'Sightseeing'),
        ('food', 'Food & Dining'),
        ('adventure', 'Adventure'),
        ('culture', 'Culture & History'),
        ('relaxation', 'Relaxation'),
        ('nightlife', 'Nightlife'),
    ]
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default='sightseeing')
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration_hours = models.FloatField(default=2.0)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.city.name})"


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='trips')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    cover_photo = models.URLField(blank=True, null=True)
    budget_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.0)
    is_public = models.BooleanField(default=False)
    share_token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TripStop(models.Model):
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name='stops')
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'arrival_date']

    def __str__(self):
        return f"{self.trip.name} - Stop: {self.city.name}"


class ItineraryItem(models.Model):
    CATEGORY_CHOICES = [
        ('transport', 'Transport'),
        ('stay', 'Stay/Hotel'),
        ('activity', 'Activity/Sightseeing'),
        ('meal', 'Meal/Dining'),
        ('other', 'Other'),
    ]
    stop = models.ForeignKey(
        TripStop, on_delete=models.CASCADE, related_name='itinerary_items')
    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default='activity')
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    order = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'order', 'start_time']


class TripExpense(models.Model):
    CATEGORY_CHOICES = [
        ('transport', 'Transport'),
        ('stay', 'Stay'),
        ('activities', 'Activities'),
        ('meals', 'Meals'),
        ('other', 'Other'),
    ]
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    note = models.CharField(max_length=255, blank=True, null=True)


class SavedDestination(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_destinations')
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'city')
