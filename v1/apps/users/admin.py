from django.contrib import admin

# Register your models here.
from v1.apps.users.models import User

admin.site.register(User)
