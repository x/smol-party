from django.contrib import admin

from .models import RSVP, Event

admin.site.register(Event)
admin.site.register(RSVP)
