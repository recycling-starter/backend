from django.contrib import admin

# Register your models here.
from v1.apps.dropoffs.models import DropoffCall


class DropoffCallAdmin(admin.ModelAdmin):
    list_display = ('datetime_call', 'datetime_dropoff', 'building_address', 'is_sent')
    list_display_links = ('datetime_call',)
    list_filter = ('building__organization__name',)
    ordering = ('datetime_call',)

    def building_address(self, obj):
        return obj.building.address


admin.site.register(DropoffCall, DropoffCallAdmin)
