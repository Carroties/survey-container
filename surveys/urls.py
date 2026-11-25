from django.urls import path

from . import views

urlpatterns = [
    path("", views.board, name="board"),
    path("survei/tambah/", views.add_survey, name="add_survey"),
    path("survei/<int:pk>/", views.survey_detail, name="survey_detail"),
]
