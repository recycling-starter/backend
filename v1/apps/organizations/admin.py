from django.contrib import admin

# Register your models here.
from v1.apps.organizations.models import Building, Organization


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'dropoff_email_to',
                    'dropoff_email_from')
    search_fields = ('name', 'dropoff_email_to', 'dropoff_email_from')
    list_display_links = ('name',)
    ordering = ('name',)


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('address', 'organization_name')
    list_display_links = ('address',)
    list_filter = ('organization__name',)
    ordering = ('address',)

    def organization_name(self, obj):
        return obj.organization.name


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Building, BuildingAdmin)
