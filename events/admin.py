from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import RSVP, Event

admin.site.register(RSVP)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "details_link", "edit_link"]

    class Meta:
        model = Event
        fields = "__all__"

    def details_link(self, event):
        """Link to the event detail page."""
        url = reverse("events:detail", kwargs={"pk": event.id})
        return format_html('<a href="{}">Details</a>', url)

    def edit_link(self, event):
        """Link to the event detail page."""
        url = reverse("events:update", kwargs={"pk": event.id}) + "?" + "secret=" + event.secret()
        return format_html('<a href="{}">Edit</a>', url)
