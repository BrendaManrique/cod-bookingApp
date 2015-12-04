from django.forms import ModelForm
from app.models import *


class ClubPartnerPreregisterForm(ModelForm):
    class Meta:
        model = ClubPartnerPreregister
        fields = ('club', 'dni', 'code',)

    def __init__(self, *args, **kwargs):
        super(ClubPartnerPreregisterForm, self).__init__(*args, **kwargs)

#
class ReservationForm(ModelForm):
    class Meta:
        model = Reservation
        fields = ('user','clubSeatActivityPlace','date', 'start_time', 'end_time',)
