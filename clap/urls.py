from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:  mysite.com
                       # Examples:  mysite.com/people
                       # Examples:  mysite.com/companies
                       url(r'^$', 'app.views.index', name='index'),
                       url(r'^home', 'app.views.home', name='home'),
                       url(r'^welcome', 'app.views.welcome', name='welcome'),
                       url(r'^club_sede', 'app.views.club_sede', name='club_sede'),
                       url(r'^reservation/(?P<club_id>[-\w]+)', 'app.views.reservation', name='reservation'),
                       url(
                           r'^reservation_activity/(?P<club_slug>[-\w]+)/(?P<clubseat_slug>[-\w]+)/(?P<activity_slug>[-\w]+)',
                           'app.views.reservation_activity', name='reservation_activity'),
                       url(r'^reservation_make_reservation', 'app.views.reservation_make', name='reservation_make'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/profile', 'app.views.profile', name='profile'),
                       # url(r'^accounts/signup', 'app.views.index'),
                       # url(r'^accounts/login', 'app.views.index'),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
                       url(r'^accounts/', include('allauth.urls')),
                       url(r'^faq', 'app.views.faq', name='faq'),
                       url(r'^about_us', 'app.views.about_us', name='about_us'),
                       url(r'^contact_club', 'app.views.contact_club', name='contact_club'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)