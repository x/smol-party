from django.urls import path, register_converter

from . import converters, views

register_converter(converters.ShortUUID, "shortuuid")

app_name = "events"

urlpatterns = [
    # ex: /create/
    path("create/", views.CreateUpdateEventView.as_view(), name="create"),
    # ex: /123/
    path("<shortuuid:pk>/", views.EventDetailView.as_view(), name="detail"),
    # ex: /123/update/
    path("<shortuuid:pk>/update/", views.CreateUpdateEventView.as_view(), name="update"),
    # ex: /123/rsvp/
    path("<shortuuid:event_id>/rsvp/", views.CreateUpdateRSVPView.as_view(), name="rsvp"),
    # ex: /123/rsvp/456/update
    path(
        "<shortuuid:event_id>/rsvp/<shortuuid:pk>/",
        views.CreateUpdateRSVPView.as_view(),
        name="rsvp_update",
    ),
]
