from django.conf.urls import patterns, url

urlpatterns = \
    patterns(
        'app.views',
        url(r'^$', 'index', name='index'),
        url(r'^seats', 'seats', name='seats'),
        url(r'^reservation', 'reservation', name='reservation'),
        url(r'^activities/(?P<seat_slug>[-\w]+)/(?P<activity_slug>[-\w]+)', 'activities', name='activities'),
        url(r'^do-reservation', 'do_reservation', name='do_reservation'),
        url(r'^cancel-reservation/(?P<reservation_id>[-\d]+)', 'cancel_reservation', name='cancel_reservation'),
        url(r'^faq', 'faq', name='faq'),
        url(r'^about_us', 'about_us', name='about_us'),
        url(r'^terms_conditions', 'terms_conditions', name='terms_conditions'),
        url(r'^contact_club', 'contact_club', name='contact_club'),
        url(r'^my-reservations', 'reservation_user', name='reservation_user'),
        url(r'^all-reservations', 'reservation_all', name='reservation_all'),
        url(r'^place-all-reservations', 'place_reservation_all', name='place_reservation_all'),
        url(r'^profile', 'profile', name='profile'),
        url(r'^set-email', 'set_email', name='set_email'),

        url(r'^registers', 'list_register', name='registers'),
        url(r'^add-register', 'create_register', name='add_register'),
        url(r'^edit-register/(?P<register_id>[-\d]+)', 'edit_register', name='edit_register'),
        url(r'^delete-register/(?P<register_id>[-\d]+)', 'delete_register', name='delete_register'),
    )