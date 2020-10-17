from django.contrib import admin

# Register your models here.
from v1.apps.boxes.models import Box


class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'fullness', 'building__address', 'organization__name')
    list_display_links = ('id',)
    list_filter = ('building__organization__name',)
    ordering = ('-fullness',)


admin.site.register(Box, BoxAdmin)
