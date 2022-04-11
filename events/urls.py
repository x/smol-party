from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    # ex: /create/
    path("create/", views.CreateUpdateEventView.as_view(), name="create"),
    # ex: /123/
    path("<uuid:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /123/update/
    path("<uuid:pk>/update/", views.CreateUpdateEventView.as_view(), name="update"),
    # ex: /123/rsvp/
    path("<uuid:event_id>/rsvp/", views.CreateRSVPView.as_view(), name="rsvp"),
]
