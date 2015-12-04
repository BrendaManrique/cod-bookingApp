import calendar
from datetime import date, datetime, timedelta
from urllib.request import HTTPPasswordMgrWithDefaultRealm
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

# Create your views here.
from app.form import ClubPartnerPreregisterForm, ReservationForm
from app.models import Club, ClubPartnerPreregister, ClubPartner, Category, Reservation, ClubSeatActivity, \
    ClubSeatActivityPlace, ClubSeat


def home(request):
    return render(request, 'home.html')


def welcome(request):
    clubs = Club.objects.all()
    clubsPartner = ClubPartner.objects.filter(user=request.user)
    isClubPage = 'F'

    if request.POST:
        form = ClubPartnerPreregisterForm(request.POST)
        if form.is_valid():
            clubPartnerPreregister = form.save(commit=False)

            print(clubPartnerPreregister.dni)
            print(clubPartnerPreregister.code)

            clubPartnerPreregister = ClubPartnerPreregister.objects.filter(dni=clubPartnerPreregister.dni,
                                                                           code=clubPartnerPreregister.code,
                                                                           status=ClubPartnerPreregister.INACTIVE)
            if clubPartnerPreregister.__len__() > 0:
                clubPartner = ClubPartner()
                clubPartner.dni = clubPartnerPreregister[0].dni
                clubPartner.code = clubPartnerPreregister[0].code
                clubPartner.club = clubPartnerPreregister[0].club
                clubPartner.user = request.user
                clubPartner.save()

                clubPartnerPreregister[0].status = ClubPartnerPreregister.ACTIVE
                clubPartnerPreregister[0].save()

                messages.add_message(request, messages.SUCCESS,
                                     (_('<strong>Excelente!</strong> Tu club fue agregado.')))
                return HttpResponseRedirect(reverse('club_sede'))

            else:
                messages.add_message(request, messages.ERROR,
                                     (_('<strong>Lo sentimos.</strong> No existe el DNI o CODIGO en este club.')))
        else:
            messages.add_message(request, messages.ERROR,
                                 (_('<strong>Lo sentimos.</strong> La información no es correcta.')))
    else:
        if clubsPartner.__len__() > 0:
            return HttpResponseRedirect(reverse('club_sede'))
        form = ClubPartnerPreregisterForm()

    return render(request, 'welcome.html', locals())


def profile(request):
    clubs = Club.objects.all()
    clubsPartner = ClubPartner.objects.filter(user=request.user)

    return render(request, 'welcome.html', locals())


def index(request):
    return render(request, 'index.html')


def reservation(request, club_id):
    club = Club.objects.get(pk=club_id)
    club_activities = ClubSeatActivity.objects.filter(club=club)
    categories = Category.objects.filter(activity__clubactivity__club=club).distinct()
    isClubPage = 'T'

    for category in categories:
        category.club_activities = []
        for club_activity in club_activities:
            if category == club_activity.activity.category:
                category.club_activities.append(club_activity)
    return render(request, 'reservation.html', locals())


def reservation_activity(request, club_slug, clubseat_slug, activity_slug):
    # TODO die if some of these not found
    club = Club.objects.get(slug=club_slug)
    club_seat = ClubSeat.objects.get(club=club, slug=clubseat_slug)
    club_seat_activity = ClubSeatActivity.objects.get(activity__slug=activity_slug, club_seat=club_seat)

    club_seat_activity_places = ClubSeatActivityPlace.objects.filter(club_seat_activity=club_seat_activity)
    is_club_page = True

    if request.POST:
        day = request.POST.get('day')
        day = datetime.strptime(day, "%d-%m-%Y")

        is_show_list = request.POST.get('is_show_list')
        if is_show_list:
            show_tab_calendar = False
        else:
            show_tab_calendar = True

    else:
        day = request.session.get('_date')
        if day is None:
            day = date.today()
        else:
            day = datetime.strptime(day, "%d-%m-%Y")

    days_from_to = week_range(day)
    day_from = days_from_to[0]
    day_to = days_from_to[1]
    days = []
    for single_date in daterange(day_from, day_to):
        days.append(single_date)

    for club_seat_activity_place_tmp in club_seat_activity_places:
        club_seat_activity_place_tmp.reservations = club_seat_activity_place_tmp.get_reservations_by_day(day)
        club_seat_activity_place_tmp.reservations_week = club_seat_activity_place_tmp.get_reservations_between(day_from, day_to)

    return render(request, 'reservation_activity.html', locals())


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def week_range(date):
    """Find the first/last day of the week for the given day.
    Assuming weeks start on Sunday and end on Saturday.

    Returns a tuple of ``(start_date, end_date)``.

    """
    # isocalendar calculates the year, week of the year, and day of the week.
    # dow is Mon = 1, Sat = 6, Sun = 7
    year, week, dow = date.isocalendar()

    # Find the first day of the week.
    if dow == 1:
        # Since we want to start with Sunday, let's test for that condition.
        start_date = date
    else:
        # Otherwise, subtract `dow` number days to get the first day
        start_date = date - timedelta(dow - 1)

    # Now, add 6 for the last day of the week (i.e., count up to Saturday)
    end_date = start_date + timedelta(7)

    return (start_date, end_date)

def reservation_make(request):
    if request.POST:
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservationTmp = form.save(commit=False)
            start_conflict = Reservation.objects. \
                filter(start_time__range=(reservationTmp.start_time, reservationTmp.end_time)). \
                filter(clubSeatActivityPlace=reservationTmp.clubSeatActivityPlace). \
                filter(date=reservationTmp.date)
            end_conflict = Reservation.objects. \
                filter(end_time__range=(reservationTmp.start_time, reservationTmp.end_time)). \
                filter(clubSeatActivityPlace=reservationTmp.clubSeatActivityPlace). \
                filter(date=reservationTmp.date)
            during_conflict = Reservation.objects. \
                filter(start_time__lte=reservationTmp.start_time, end_time__gte=reservationTmp.end_time). \
                filter(clubSeatActivityPlace=reservationTmp.clubSeatActivityPlace). \
                filter(date=reservationTmp.date)

            if (start_conflict or end_conflict or during_conflict):
                messages.add_message(request, messages.ERROR,
                                     (_('<strong>Lo sentimos.</strong> No hay disponibilidad en ese horario.')))
            else:
                reservationTmp.save()
                messages.add_message(request, messages.SUCCESS,
                                     (_('<strong>Excelente!</strong> Tu reservación fue exitosa.')))
        else:
            messages.add_message(request, messages.ERROR,
                                 (_('<strong>Los sentimos.</strong>') + form.errors))
        request.session['_date'] = reservationTmp.date.strftime("%d-%m-%Y")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def faq(request):
    return render(request, 'faq.html', locals())


def about_us(request):
    return render(request, 'about_us.html', locals())


def contact_club(request):
    return render(request, 'contact_club.html', locals())


def club_sede(request):
    clubsPartner = ClubPartner.objects.filter(user=request.user)
    show_tab_club = True
    return render(request, 'club_sede.html', locals())