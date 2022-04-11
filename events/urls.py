from django.urls import path, register_converter

from . import views, converters

register_converter(converters.ShortUUID, 'shortuuid')

app_name = "events"

urlpatterns = [
    # ex: /create/
    path("create/", views.CreateUpdateEventView.as_view(), name="create"),
    # ex: /123/
    path("<shortuuid:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /123/update/
    path("<shortuuid:pk>/update/", views.CreateUpdateEventView.as_view(), name="update"),
    # ex: /123/rsvp/
    path("<shortuuid:event_id>/rsvp/", views.CreateRSVPView.as_view(), name="rsvp"),
]
