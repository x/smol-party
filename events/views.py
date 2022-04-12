from django.core.exceptions import PermissionDenied
from django.forms.widgets import DateTimeInput
from django.urls import reverse
from django.views import generic

from .models import RSVP, Event


class CreateOrUpdateView(generic.UpdateView):
    # This override lets us use the UpdateView as both a CreateView and an UpdateView.
    # See: https://stackoverflow.com/a/48116803
    def get_object(self, queryset=None):

        # Try to find the object using the primary key in case it's an update.
        try:
            object = super().get_object(queryset)

        # If it's not there, assume they're creating a new event.
        except AttributeError:
            return None

        # Now that we have the object, we should confirm they're allowed to
        # update it via the secret param.
        secret = self.request.GET.get("secret")
        if secret == object.secret():
            return object
        else:
            raise PermissionDenied


class EventDetailView(generic.DetailView):
    model = Event
    template_name = "events/detail.html"

    def is_event_owner(self) -> bool:
        """Determine, based on the session, if the user is the owner of the event."""
        return self.object.secret() == self.request.session.get(f"{self.object.id}_event_secret")

    def get_context_data(self, *args, **kwargs):
        context = super(EventDetailView, self).get_context_data(*args, **kwargs)
        context["is_owner"] = self.is_event_owner()
        return context


class CreateRSVPView(generic.CreateView):
    model = RSVP
    fields = ["name"]

    def form_valid(self, form):
        form.instance.event_id = self.kwargs["event_id"]
        return super().form_valid(form)

    def set_created_rsvp(self) -> None:
        """Store the rsvp_id in the session with the event_id as the key so we know we've RSVP'd."""
        event_id = self.kwargs["event_id"]
        rsvp_id = self.object.id
        # TODO: Someday replace this key with "{event_id}_rsvp_id".
        self.request.session[str(event_id)] = str(rsvp_id)

    def get_success_url(self):
        """Set that this event was RSVP'd by this user and redirect to the event detail page."""
        self.set_created_rsvp()
        return reverse("events:detail", kwargs={"pk": self.kwargs["event_id"]})


class CreateUpdateEventView(CreateOrUpdateView):
    model = Event
    fields = "__all__"

    def get_form(self):
        form = super(CreateUpdateEventView, self).get_form()
        form.fields["start_time"].widget = DateTimeInput(
            attrs={"type": "datetime-local"}, format=("%Y-%m-%dT%H:%M")
        )
        form.fields["end_time"].widget = DateTimeInput(
            attrs={"type": "datetime-local"}, format=("%Y-%m-%dT%H:%M")
        )
        # Set the description to not be "required" because we're hiding it in the template. This raises issues in Safari.
        form.fields["description"].required = False
        return form

    def set_event_owner(self) -> None:
        """Set the secret for the event to the session. This way we can confirm
        that the user is the owner of the event later."""
        self.request.session[f"{self.object.id}_event_secret"] = self.object.secret()

    def get_success_url(self):
        """Set that this event was created by this user and redirect to the event detail page."""
        self.set_event_owner()
        return reverse("events:detail", kwargs={"pk": self.object.id})
