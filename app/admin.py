from distutils.command import register
from django.contrib import admin

# Register your models here.
from app.models import Club, Activity, ClubPartnerPreregister, ClubPartner, Category, ClubSeatActivity, \
    ClubSeatActivityPlace, ClubSeat


class AdminClub(admin.ModelAdmin):
    list_display = ('name','status',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('updated_at', 'created_at')

admin.site.register(Club,AdminClub)

class AdminClubSeat(admin.ModelAdmin):
    list_display = ('club','name','status',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('updated_at', 'created_at')
admin.site.register(ClubSeat,AdminClubSeat)

class AdminActivity(admin.ModelAdmin):
    list_display = ('name','category','status',)
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('updated_at', 'created_at')
admin.site.register(Activity, AdminActivity)

class AdminClubSeatActivity(admin.ModelAdmin):
    list_display = ('club_seat','activity','status',)
    # list_filter = ('club','activity',)
admin.site.register(ClubSeatActivity, AdminClubSeatActivity)

class AdminClubSeatActivityPlace(admin.ModelAdmin):
    list_display = ('club_seat_activity','name','description','status',)
    # list_filter = ('club','activity',)
admin.site.register(ClubSeatActivityPlace, AdminClubSeatActivityPlace)

class AdminClubPartnerPreregister(admin.ModelAdmin):
    list_display = ('club','dni','code','status')
    list_filter = ('club',)

admin.site.register(ClubPartnerPreregister, AdminClubPartnerPreregister)

class AdminClubPartner(admin.ModelAdmin):
    list_display = ('club','user','dni','code',)
    list_filter = ('club','user',)

admin.site.register(ClubPartner, AdminClubPartner)
admin.site.register(Category)
