from django.forms.widgets import DateTimeInput, HiddenInput
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import RSVP, Event


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events"

    def get_queryset(self):
        """Return the 10 upcoming events."""
        # today = arrow.now().to("America/New_York").floor("day").isoformat()  # TODO timezones
        # return Event.objects.filter(start_time__gte=today).order_by("start_time")[:10]
        return Event.objects.all().order_by("start_time")[:10]


class DetailView(generic.DetailView):
    model = Event
    template_name = "events/detail.html"


class CreateRSVPView(generic.CreateView):
    model = RSVP
    fields = [
        "name",
        # Only shows up if potluck
        "potluck_dish_description",
        "potluck_dish_course",
        "potluck_dish_is_vegetarian",
        "potluck_dish_is_vegan",
        "potluck_dish_contains_nuts",
        "potluck_dish_is_spicy",
    ]

    def form_valid(self, form):
        form.instance.event_id = self.kwargs["event_id"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = get_object_or_404(Event, pk=self.kwargs["event_id"])
        return context

    def get_success_url(self):
        event_id = self.kwargs["event_id"]
        rsvp_id = self.object.id
        # Store the rsvp_id in the session with the event_id as the key so we know we've RSVP'd
        self.request.session[str(event_id)] = str(rsvp_id)
        # Redirect back to the event detail page
        return reverse("events:detail", kwargs={"pk": event_id})


class CreateEventView(generic.CreateView):
    model = Event
    fields = "__all__"

    def get_form(self):
        form = super(CreateEventView, self).get_form()
        form.fields["start_time"].widget = DateTimeInput(attrs={"type": "datetime-local"})
        form.fields["end_time"].widget = DateTimeInput(attrs={"type": "datetime-local"})
        return form

    def get_success_url(self):
        return reverse("events:detail", kwargs={"pk": self.object.id})
