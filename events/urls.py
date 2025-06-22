from django.urls import path
from .views import EventsApiView, UpdateDeleteEventsView, CreateEventsApiView, TakePartView, CategoriesApiView
urlpatterns = [
    path("events/", EventsApiView.as_view()),
    path("events/create", CreateEventsApiView.as_view()),
    path("events/categories", CategoriesApiView.as_view()),
    path("events/<str:title>", UpdateDeleteEventsView.as_view()),
    path("events/<str:title>/join", TakePartView.as_view()),
]
