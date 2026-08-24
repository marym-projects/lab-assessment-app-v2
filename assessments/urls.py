from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("new/", views.assessment_create, name="assessment_create"),
    path("assessments/", views.my_assessments, name="my_assessments"),
    path("assessment/<int:pk>/", views.assessment_detail, name="assessment_detail"),
    path("assessment/<int:pk>/edit/", views.assessment_edit, name="assessment_edit"),
    path("assessment/<int:pk>/complete/", views.assessment_complete, name="assessment_complete"),
    path("assessment/<int:pk>/report/", views.assessment_report, name="assessment_report"),
    path("reports/", views.reports, name="reports"),
    path("facility-lookup/", views.facility_lookup, name="facility_lookup"),
]
