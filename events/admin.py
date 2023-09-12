from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import RSVP, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "details_link", "edit_link"]
    ordering = ["-created_at"]

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


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ["name", "event_link", "edit_link"]
    ordering = ["-created_at"]

    class Meta:
        model = RSVP
        fields = "__all__"

    def event_link(self, rsvp):
        """Link to the event detail page."""
        url = reverse("events:detail", kwargs={"pk": rsvp.event.id})
        return format_html('<a href="{}">{}</a>', url, rsvp.event.title)

    def edit_link(self, rsvp):
        """Link to the rsvp detail page."""
        url = (
            reverse("events:rsvp_update", kwargs={"event_id": rsvp.event.id, "pk": rsvp.id})
            + "?"
            + "secret="
            + rsvp.secret()
        )
        return format_html('<a href="{}">Edit</a>', url)
