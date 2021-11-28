from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    # ex: /events/create/
    path("create/", views.CreateEventView.as_view(), name="create"),
    # ex: /events/123/
    path("<uuid:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /events/123/rsvp/
    path("<uuid:event_id>/rsvp/", views.CreateRSVPView.as_view(), name="rsvp"),
]
