from django.contrib import admin

# Register your models here.
from v1.apps.boxes.models import Box


class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'fullness', 'building_address', 'organization_name')
    list_display_links = ('id',)
    list_filter = ('building__organization__name',)
    ordering = ('-fullness',)

    def building_address(self, obj):
        return obj.building.address

    def organization_name(self, obj):
        return obj.building.organization.name


admin.site.register(Box, BoxAdmin)
