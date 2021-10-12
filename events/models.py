import uuid
from urllib.parse import quote

from django.db import models


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    tagline = models.CharField(max_length=256)
    description = models.TextField()
    start_time = models.DateTimeField("from")
    end_time = models.DateTimeField("until")
    location = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.title} ({self.start_time})"

    def google_maps_url(self):
        return f"https://maps.google.com/maps?width=100%25&amp;height=400&amp;hl=en&amp;q={quote(self.location)}+({quote(self.title)})&amp;t=&amp;z=14&amp;ie=UTF8&amp;iwloc=B&amp;output=embed"


class RSVP(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.name} RSVP'd to {self.event.title}"
