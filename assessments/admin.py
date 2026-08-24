from django.contrib import admin
from .models import (
    Assessment, StaffMember, POCTestStat, ChecklistResponse,
    TestKitAssessed, TestKitResponse, NonConformity,
)


class StaffMemberInline(admin.TabularInline):
    model = StaffMember
    extra = 0


class POCTestStatInline(admin.TabularInline):
    model = POCTestStat
    extra = 0


class ChecklistResponseInline(admin.TabularInline):
    model = ChecklistResponse
    extra = 0


class TestKitAssessedInline(admin.TabularInline):
    model = TestKitAssessed
    extra = 0


class NonConformityInline(admin.TabularInline):
    model = NonConformity
    extra = 0


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("facility_name", "county_name", "date_of_assessment", "created_at")
    search_fields = ("facility_name", "county_name", "sub_county", "facility_mfl_code")
    inlines = [StaffMemberInline, POCTestStatInline, ChecklistResponseInline, TestKitAssessedInline, NonConformityInline]


@admin.register(TestKitAssessed)
class TestKitAssessedAdmin(admin.ModelAdmin):
    list_display = ("assessment", "pathogen_condition", "kit_name")
