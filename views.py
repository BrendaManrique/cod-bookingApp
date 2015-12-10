from datetime import timedelta, datetime, date
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
# Create your views here.
from app.forms import ReservationForm, RegisterForm, EmailForm
from app.models import SeatActivity, Category, Advertisement, Seat, SeatActivityPlace, Reservation, Register, Activity
from django.utils.translation import ugettext_lazy as _
from clap import settings


def index(request):
    if request.POST:
        pass
    return render(request, 'app/index.html', locals())


@login_required()
def reservation(request):
    seats_activities = SeatActivity.objects.all()
    categories = Category.objects.all()
    isClubPage = 'T'

    for category in categories:
        category.activities = []
        for seat_activity in seats_activities:
            if category == seat_activity.activity.category:
                category.activities.append(seat_activity)
    return render(request, 'app/reservation.html', locals())


@login_required()
def activities(request, seat_slug, activity_slug):
    # TODO die if some of these not found
    seat = Seat.objects.get(slug=seat_slug)
    seat_activity = SeatActivity.objects.get(activity__slug=activity_slug, seat=seat)
    seat_activity_places = SeatActivityPlace.objects.filter(seat_activity=seat_activity)

    other_seats = SeatActivity.objects.filter(activity__slug=activity_slug).exclude(seat=seat)

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

    for seat_activity_place_tmp in seat_activity_places:
        seat_activity_place_tmp.reservations = seat_activity_place_tmp.get_reservations_by_day(day)
        seat_activity_place_tmp.reservations_week = seat_activity_place_tmp.get_reservations_between(day_from, day_to)



    return render(request, 'app/activities.html', locals())


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


@login_required()
def do_reservation(request):
    if request.POST:
        form = ReservationForm(request.POST)
        is_ok = True
        if form.is_valid():
            reservationTmp = form.save(commit=False)
            start_conflict = Reservation.objects. \
                filter(start_time__range=(reservationTmp.start_time, reservationTmp.end_time)). \
                filter(seatActivityPlace=reservationTmp.seatActivityPlace). \
                filter(date=reservationTmp.date)
            end_conflict = Reservation.objects. \
                filter(end_time__range=(reservationTmp.start_time, reservationTmp.end_time)). \
                filter(seatActivityPlace=reservationTmp.seatActivityPlace). \
                filter(date=reservationTmp.date)
            during_conflict = Reservation.objects. \
                filter(start_time__lte=reservationTmp.start_time, end_time__gte=reservationTmp.end_time). \
                filter(seatActivityPlace=reservationTmp.seatActivityPlace). \
                filter(date=reservationTmp.date)

            if (start_conflict or end_conflict or during_conflict):
                messages.add_message(request, messages.ERROR,
                                     (_('Lo sentimos. No hay disponibilidad en ese horario.')))
                is_ok = False
            else:
                if request.user.is_staff:
                    code = request.POST.get("code")
                    try:
                        reservationTmp.user = User.objects.get(username=code)
                        is_ok = True
                    except User.DoesNotExist:
                        messages.add_message(request, messages.ERROR,
                                             (_('Lo sentimos. El codigo del socio es incorrecto.')))
                else:
                    max_hours_per_day = reservationTmp.seatActivityPlace.seat_activity.activity.max_hours_per_day
                    difference = datetime.combine(reservationTmp.date, reservationTmp.start_time) - datetime.combine(
                        reservationTmp.date, reservationTmp.end_time)
                    difference = difference.seconds / 3600
                    difference = 24 - difference

                    if difference > max_hours_per_day:
                        messages.add_message(request, messages.ERROR,
                                             (_('Lo sentimos. Solo puede reservar hasta %(max)s hours.') % {
                                             'max': str(max_hours_per_day)}))
                        is_ok = False

                    max_times_per_week = reservationTmp.seatActivityPlace.seat_activity.activity.max_times_per_week

            if is_ok:
                reservationTmp.save()
                messages.add_message(request, messages.SUCCESS,
                                     (_(
                                         '¡Excelente! Tu reservación fue exitosa. Reservaste el día ' + reservationTmp.date.strftime(
                                             "%d-%m-%Y") +
                                         ' en el horario de ' + reservationTmp.start_time.strftime(
                                             "%H:%M") + ' a ' + reservationTmp.end_time.strftime(
                                             "%H:%M") + '.')))

                if reservationTmp.user.email:
                    subject = 'CLAP - Tu reservación ha sido hecha con exito'
                    body = 'Hi <br/> Tu reservación ha sido hecha con exito'
                    msg = EmailMultiAlternatives(subject, body, settings.EMAIL_HOST_USER, [reservationTmp.user.email])
                    msg.attach_alternative(body, "text/html")
                    msg.send()

            request.session['_date'] = reservationTmp.date.strftime("%d-%m-%Y")
        else:
            messages.add_message(request, messages.ERROR,
                                 (_('Porfavor consideré las siguientes observaciones.')))
            for error in form._errors:
                messages.add_message(request, messages.ERROR,
                                     (_(error + ' ' + form._errors[error][0])))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def faq(request):
    # clubsUnique = Club.objects.filter()[:1].get()
    return render(request, 'app/faq.html', locals())


def about_us(request):
    # clubsUnique = Club.objects.filter()[:1].get()
    return render(request, 'app/about_us.html', locals())


def contact_club(request):
    # clubsUnique = Club.objects.filter()[:1].get()
    return render(request, 'app/contact_club.html', locals())


@login_required()
def seats(request):
    seats = Seat.objects.all()
    advertisements = Advertisement.objects.all()
    show_tab_club = True
    return render(request, 'app/seats.html', locals())


@login_required()
def reservation_user(request):
    advertisements = Advertisement.objects.all()
    day = request.session.get('_date')
    if day is None:
        day = date.today()
    else:
        day = datetime.strptime(day, "%d-%m-%Y")
    day_to = day.replace(day.year + 1)
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'app/reservation_user.html', locals())


@login_required()
@staff_member_required
def reservation_all(request):
    advertisements = Advertisement.objects.all()
    day = request.session.get('_date')
    if day is None:
        day = date.today()
    else:
        day = datetime.strptime(day, "%d-%m-%Y")
    day_to = day.replace(day.year + 1)
    reservations = Reservation.objects.all()
    return render(request, 'app/reservation_all.html', locals())

@login_required()
@staff_member_required
def place_reservation_all(request):
    advertisements = Advertisement.objects.all()
    if request.POST:
        place_id = request.POST.get("placeId")
        seatActivityPlace = SeatActivityPlace.objects.get(pk=place_id)
        reservations = Reservation.objects.filter(seatActivityPlace=seatActivityPlace)
    seats = Seat.objects.all()
    return render(request, 'app/reservation_all_place.html', locals())

@login_required()
def cancel_reservation(request, reservation_id):
    try:
        if request.user.is_staff:
            reservationTmp = Reservation.objects.get(pk=reservation_id)
        else:
            reservationTmp = Reservation.objects.get(pk=reservation_id, user=request.user)
        reservationTmp.delete()
    except Reservation.DoesNotExist:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def terms_conditions(request):
    return render(request, 'app/terms_conditions.html', locals())


@login_required()
def profile(request):
    register = Register.objects.get(code=request.user)
    return render(request, 'app/profile.html', locals())

@login_required
def set_email(request):
    register = Register.objects.get(code=request.user)
    if request.POST:
        form =  EmailForm(request.POST, instance=register)
        if form.is_valid():
            emailTmp = form.save(commit=False)
            if (1==1):
                 emailTmp.save()
                 messages.add_message(request, messages.SUCCESS,
                                             (_('Su e-mail fue guardado exitosamente.' )))

            else:
                messages.add_message(request, messages.ERROR,
                                     (_('Error en guardar su e-mail.')))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@staff_member_required
def list_register(request):
    registers = Register.objects.all()
    return render(request, 'app/registers.html', locals())


@login_required
@staff_member_required
def create_register(request):
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('app:registers'))
    else:
        form = RegisterForm()
    return render(request, 'app/register_form.html', locals())


@login_required
@staff_member_required
def edit_register(request, register_id):
    try:
        register = Register.objects.get(pk=register_id)
    except Register.DoesNotExist:
        raise Http404

    if request.POST:
        form = RegisterForm(request.POST, instance=register)
        if form.is_valid():
            form.save()
            return redirect(reverse('app:registers'))
    else:
        form = RegisterForm(instance=register)
        form.form_meta['title'] = _('Editando registro')
    return render(request, 'app/register_form.html', locals())


@login_required
@staff_member_required
def delete_register(request, register_id):
    try:
        register = Register.objects.get(pk=register_id)
    except Register.DoesNotExist:
        raise Http404
    register.delete()
    return redirect(reverse('app:registers'))