from django.urls import include, re_path
from v1.apps.boxes import urls as b_urls
from v1.apps.dropoffs import urls as d_urls
from v1.apps.organizations import urls as o_urls
from v1.apps.organizations import b_urls as buildings_urls
from v1.apps.users import urls as u_urls

urlpatterns = [
    re_path(r"^boxes/", include(b_urls)),
    re_path(r"^dropoffs/", include(d_urls)),
    re_path(r"^organizations/", include(o_urls)),
    re_path(r"^buildings/", include(buildings_urls)),
    re_path(r"^users/", include(u_urls)),
]
