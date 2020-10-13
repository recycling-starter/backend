from django.contrib import admin

# Register your models here.
from v1.apps.organizations.models import Building, Organization

admin.site.register(Organization)
admin.site.register(Building)