# urls.py
from django.contrib import admin
from django.urls import re_path

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
]
