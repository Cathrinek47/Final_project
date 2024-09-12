from django.contrib import admin
from booking.models import *


admin.site.register(Apartment)

# @admin.register(Apartment)
# class ApartmentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'location''created_at')
#     search_fields = ('title',)
#     list_filter = ('title', 'category')
#     ordering = ('-created_at',)


# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username',)
#     search_fields = ('username',)
#     ordering = ('username',)

