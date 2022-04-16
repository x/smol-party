import re
from typing import List

from django.core.exceptions import PermissionDenied
from django.forms.widgets import DateTimeInput
from django.urls import reverse
from django.views import generic

from .models import RSVP, Event
from .secret_utils import secret_is_correct

UUID_36_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


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
    template_name = "events/event/detail.html"

    def is_event_owner(self) -> bool:
        """Determine, based on the session, if the user is the owner of the event."""
        return self.object.secret() == self.request.session.get(f"{self.object.id}_event_secret")

    def owned_rsvp_ids(self) -> List[str]:
        """Return the RSVP IDs for the user and confirm they own them by
        checking the secret. A user should only have one of these but..."""
        rsvp_ids = []
        for key, rsvp_secret in self.request.session.items():
            if not re.match(f"^{UUID_36_REGEX}_{UUID_36_REGEX}_rsvp_secret$", key):
                continue
            event_id, rsvp_id, _ = key.split("_", maxsplit=2)
            if event_id == str(self.object.id) and secret_is_correct(rsvp_id, rsvp_secret):
                rsvp_ids.append(rsvp_id)
        return rsvp_ids

    def get_context_data(self, *args, **kwargs):
        context = super(EventDetailView, self).get_context_data(*args, **kwargs)
        context["is_event_owner"] = self.is_event_owner()
        context["owned_rsvp_ids"] = self.owned_rsvp_ids()
        return context


class CreateUpdateEventView(CreateOrUpdateView):
    model = Event
    fields = "__all__"
    template_name = "events/event/create_update.html"

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


class DeleteEventView(generic.DeleteView):
    model = Event
    template_name = "events/event/delete.html"
    success_url = "/"

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        # Confirm they're allowed to delete the object via the "secret" param.
        if self.request.GET.get("secret") == object.secret():
            return object
        else:
            raise PermissionDenied


class CreateUpdateRSVPView(CreateOrUpdateView):
    model = RSVP
    fields = ["name"]
    template_name = "events/rsvp/create_update.html"

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

    def get_context_data(self, *args, **kwargs):
        context = super(CreateUpdateRSVPView, self).get_context_data(*args, **kwargs)
        context["event"] = Event.objects.get(pk=self.kwargs["event_id"])
        return context


class DeleteRSVPView(generic.DeleteView):
    model = RSVP
    template_name = "events/rsvp/delete.html"

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        # Confirm they're allowed to delete the object via the "secret" param.
        if self.request.GET.get("secret") == object.secret():
            return object
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse("events:detail", kwargs={"pk": self.kwargs["event_id"]})

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteRSVPView, self).get_context_data(*args, **kwargs)
        context["event"] = Event.objects.get(pk=self.kwargs["event_id"])
        return context
