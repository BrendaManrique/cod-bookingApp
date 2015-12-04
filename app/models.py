from datetime import date
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext as _

# Create your models here.
class Club(models.Model):
    STATUS_CHOICES = (
        (1, _('active')),
        (2, _('inactive')),
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='resources/img', blank=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_seats(self):
        return ClubSeat.objects.filter(club=self)


class Category(models.Model):
    STATUS_CHOICES = (
        (1, _('active')),
        (2, _('inactive')),
    )
    name = models.CharField(max_length=100, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Activity(models.Model):  # Football (category=sports)
    STATUS_CHOICES = (
        (1, _('active')),
        (2, _('inactive')),
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = ForeignKey(Category)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClubSeat(models.Model):
    STATUS_CHOICES = (
        (1, _('active')),
        (2, _('inactive')),
    )
    club = ForeignKey(Club)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    address = models.CharField(max_length=200, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.name + " - " + self.name

    def get_categories(self):
        categories = Category.objects.filter(activity__clubseatactivity__club_seat=self).distinct()
        for category in categories:
            category.club_seat_activities = []
            for club_seat_activity_tmp in self.get_activities():
                if category == club_seat_activity_tmp.activity.category:
                    category.club_seat_activities.append(club_seat_activity_tmp)
        return categories

    def get_activities(self):
        objects_filter = ClubSeatActivity.objects.filter(club_seat=self)
        return objects_filter


class ClubSeatActivity(models.Model):
    STATUS_CHOICES = (
        (1, _('active')),
        (2, _('inactive')),
    )
    club_seat = ForeignKey(ClubSeat)
    activity = ForeignKey(Activity)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club_seat.club.name + "," + self.club_seat.name + " - "+self.activity.category.name +"-" + self.activity.name


class ClubSeatActivityPlace(models.Model):  # Cancha1 ( club_activity = inter-football)
    ACTIVE = 1
    INACTIVE = 2

    STATUS_CHOICES = (
        (ACTIVE, _('active')),
        (INACTIVE, _('inactive')),
    )
    club_seat_activity = ForeignKey(ClubSeatActivity)
    name = models.CharField(max_length=100, )
    photo = models.ImageField(upload_to='resources/img', default='resources/img/default/field.jpg')
    description = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_reservations_by_day(self, date=date.today):
        return self.reservation_set.filter(date=date).values()

    def get_reservations_between(self, day_from, day_to):
        return self.reservation_set.filter(date__range=(day_from, day_to)).values()


class ClubPartnerPreregister(models.Model):
    ACTIVE = 1
    INACTIVE = 2

    STATUS_CHOICES = (
        (ACTIVE, _('active')),
        (INACTIVE, _('inactive')),
    )

    club = ForeignKey(Club, null=None, )
    dni = models.IntegerField(max_length=8, blank=None, null=None)
    code = models.CharField(max_length=10, blank=None, null=None)
    status = models.IntegerField(choices=STATUS_CHOICES, default=INACTIVE)


class ClubPartner(models.Model):
    ACTIVE = 1
    INACTIVE = 2

    STATUS_CHOICES = (
        (ACTIVE, _('active')),
        (INACTIVE, _('inactive')),
    )

    club = ForeignKey(Club, null=None, )
    user = ForeignKey(User, null=None, )
    dni = models.IntegerField(max_length=8, blank=None, null=None)
    code = models.CharField(max_length=10, blank=None, null=None)
    status = models.IntegerField(choices=STATUS_CHOICES, default=ACTIVE)


class Reservation(models.Model):
    user = ForeignKey(User)
    clubSeatActivityPlace = ForeignKey(ClubSeatActivityPlace)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    time = models.TimeField(null=True)