import uuid
from urllib.parse import quote

from django.conf import settings
from django.db import models

from .secret_utils import SecretMixin


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(TimeStampMixin, SecretMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    tagline = models.CharField(max_length=256)
    description = models.TextField()
    start_time = models.DateTimeField("from")
    end_time = models.DateTimeField("until")
    location = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.title} ({self.start_time})"

    def google_maps_iframe_url(self):
        return (
            "https://maps.google.com/maps?"
            + "width=100%25&amp;height=400&amp;hl=en"
            + f"&amp;q={quote(self.location)}+({quote(self.title)})"
            + "&amp;t=&amp;z=14&amp;ie=UTF8&amp;iwloc=B&amp;output=embed"
        )

    def add_to_gcal_link(self):
        # This is a total fucking hack.
        # For some reason the dates when you create the events are stored in UTC
        # and not the timezone of the user creating the event.
        # And then you end up with an event with the wrong time in the DB
        # (unless they live in iceland).
        # But we're just going to assume the person who's adding this link to
        # their calendar is in the same timezone as the person who made the
        # event. So basically treat the UTC datetime as if it were naive.
        # Fucking gross.
        start_time = self.start_time.strftime("%Y%m%dT%H%M%S")
        end_time = self.end_time.strftime("%Y%m%dT%H%M%S")
        return (
            "https://calendar.google.com/calendar/render?"
            + "action=TEMPLATE"
            + f"&dates={start_time}/{end_time}"
            + f"&location={quote(self.location)}"
            + f"&text={quote(self.title)}"
            + f"&details={quote(self.description)}"
        )

    def google_maps_url(self):
        """This URL will open google maps on an iOS or Android device."""
        return f"https://maps.google.com/?q={quote(self.location)}"

    def apple_maps_url(self):
        """This URL will open apple maps on an iOS device."""
        return f"https://maps.apple.com/maps?q={quote(self.location)}"


class RSVP(TimeStampMixin, SecretMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.name} RSVP'd to {self.event.title}"
