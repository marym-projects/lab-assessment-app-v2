from django.db import models
from django.contrib.auth.models import User

from .checklist_data import RESPONSE_CHOICES


class Facility(models.Model):
    """
    Master list of health facilities.

    Each facility is identified by a unique MFL code.
    Facility information can be imported from the
    facility master Excel file.
    """

    mfl_code = models.CharField(
        "MFL Code",
        max_length=50,
        unique=True,
        db_index=True,
    )

    facility_name = models.CharField(
        "Facility Name",
        max_length=255,
    )

    county = models.CharField(
        "County",
        max_length=100,
        blank=True,
    )

    sub_county = models.CharField(
        "Sub-county",
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["facility_name"]

    def __str__(self):
        return (
            f"{self.facility_name} "
            f"({self.mfl_code})"
        )


class Assessment(models.Model):
    """
    Part A: General facility information + top-level
    assessment record.

    One row = one visit/assessment of one facility.
    """

    FACILITY_TYPE_CHOICES = [
        ("dispensary", "Dispensary"),
        ("health_centre", "Health Centre"),
        ("sub_county_hospital", "Sub County Hospital"),
        ("county_hospital", "County Hospital"),
        ("national_hospital", "National Hospital"),
        ("other", "Other"),
    ]

    LEVEL_CHOICES = [
        (str(n), f"Level {n}")
        for n in range(2, 7)
    ]

    AFFILIATION_CHOICES = [
        ("government", "Government"),
        ("private", "Private"),
        ("faith_based", "Faith Based"),
        ("ngo", "NGO"),
        ("other", "Other"),
    ]

    PARTNER_CHOICES = [
        ("gok", "GoK"),
        ("gok_coag", "GoK Coag"),
        ("county_government", "County Government"),
        ("partner", "Partner (specify)"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("completed", "Completed"),
    ]

    SOURCE_CHOICES = [
        ("live", "Live Assessment"),
        ("imported", "Imported Historical Assessment"),
        ("test", "Test Data"),
    ]

    # =========================================================
    # OWNERSHIP
    # =========================================================

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assessments",
        null=True,
        blank=True,
    )

    # =========================================================
    # FACILITY MASTER RECORD
    # =========================================================

    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="assessments",
        null=True,
        blank=True,
    )

    # =========================================================
    # LOCATION / IDENTIFICATION
    # =========================================================

    county_name = models.CharField(
        max_length=100,
        blank=True,
    )

    sub_county = models.CharField(
        max_length=100,
        blank=True,
    )

    facility_name = models.CharField(
        max_length=200,
        blank=True,
    )

    facility_mfl_code = models.CharField(
        "Facility MFL code",
        max_length=50,
        blank=True,
    )

    site = models.CharField(
        max_length=100,
        blank=True,
    )

    # =========================================================
    # ASSESSMENT META
    # =========================================================

    assessment_type = models.CharField(
        max_length=100,
        blank=True,
    )

    date_of_assessment = models.DateField(
        null=True,
        blank=True,
    )

    time_of_assessment = models.TimeField(
        blank=True,
        null=True,
    )

    date_of_previous_assessment = models.DateField(
        blank=True,
        null=True,
    )

    # =========================================================
    # FACILITY TYPE / LEVEL / AFFILIATION
    # =========================================================

    facility_type = models.CharField(
        max_length=30,
        choices=FACILITY_TYPE_CHOICES,
        blank=True,
    )

    facility_type_other = models.CharField(
        max_length=150,
        blank=True,
    )

    level = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        blank=True,
    )

    affiliation = models.CharField(
        max_length=20,
        choices=AFFILIATION_CHOICES,
        blank=True,
    )

    affiliation_other = models.CharField(
        max_length=150,
        blank=True,
    )

    partner = models.CharField(
        max_length=20,
        choices=PARTNER_CHOICES,
        blank=True,
    )

    partner_specify = models.CharField(
        max_length=200,
        blank=True,
    )

    physical_address = models.CharField(
        max_length=255,
        blank=True,
    )

    # =========================================================
    # INTERVIEWEE
    # =========================================================

    interviewee_name = models.CharField(
        max_length=150,
        blank=True,
    )

    interviewee_title = models.CharField(
        max_length=150,
        blank=True,
    )

    interviewee_phone = models.CharField(
        max_length=30,
        blank=True,
    )

    poc_tests_conducted = models.TextField(
        "List of POC tests conducted at this facility",
        blank=True,
    )

    # =========================================================
    # PART D / SIGNATURES
    # =========================================================

    assessors = models.CharField(
        "Assessor(s)",
        max_length=255,
        blank=True,
    )

    site_supervisor_name = models.CharField(
        max_length=150,
        blank=True,
    )

    site_supervisor_date = models.DateField(
        blank=True,
        null=True,
    )

    assessor_date = models.DateField(
        blank=True,
        null=True,
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    # =========================================================
    # DATA SOURCE
    # =========================================================

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="live",
    )

    # =========================================================
    # WIZARD / DRAFT PROGRESS
    # =========================================================

    last_completed_step = models.PositiveSmallIntegerField(
        default=0,
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        facility = (
            self.facility_name
            or "Unnamed Facility"
        )

        date = (
            self.date_of_assessment
            or "No Date"
        )

        return f"{facility} - {date}"

    class Meta:
        ordering = ["-created_at"]


class StaffMember(models.Model):
    """
    Name of staff / Title of staff rows in Part A.
    """

    assessment = models.ForeignKey(
        Assessment,
        related_name="staff_members",
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=150,
        blank=True,
    )

    title = models.CharField(
        max_length=150,
        blank=True,
    )

    def __str__(self):
        return self.name or "Unnamed Staff Member"


class POCTestStat(models.Model):
    """
    POC Tests Statistics Summary rows.
    """

    assessment = models.ForeignKey(
        Assessment,
        related_name="test_stats",
        on_delete=models.CASCADE,
    )

    period = models.CharField(
        max_length=100,
        blank=True,
    )

    type_of_test = models.CharField(
        max_length=150,
        blank=True,
    )

    tests_conducted = models.CharField(
        "# of tests conducted (Month/Quarter)",
        max_length=50,
        blank=True,
    )

    positives = models.CharField(
        "# Positives (Month/Quarter)",
        max_length=50,
        blank=True,
    )

    negatives = models.CharField(
        "# Negatives (Month/Quarter)",
        max_length=50,
        blank=True,
    )

    comments = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.type_of_test or 'POC Test'} "
            f"- {self.period or 'No Period'}"
        )


class ChecklistResponse(models.Model):
    """
    One answer to one fixed question from
    Sections 1-7, 9 and 10.
    """

    assessment = models.ForeignKey(
        Assessment,
        related_name="checklist_responses",
        on_delete=models.CASCADE,
    )

    section_number = models.PositiveSmallIntegerField()

    item_code = models.CharField(
        max_length=10,
    )

    response = models.CharField(
        max_length=2,
        choices=RESPONSE_CHOICES,
        blank=True,
    )

    comment = models.CharField(
        max_length=500,
        blank=True,
    )

    class Meta:
        unique_together = (
            "assessment",
            "item_code",
        )

    def __str__(self):
        return (
            f"{self.assessment_id} - "
            f"{self.item_code}"
        )


class TestKitAssessed(models.Model):
    """
    Section 8.

    One record represents one test/pathogen performed
    at the facility.
    """

    assessment = models.ForeignKey(
        Assessment,
        related_name="test_kits",
        on_delete=models.CASCADE,
    )

    pathogen_condition = models.CharField(
        "Name of pathogen/condition tested",
        max_length=150,
        blank=True,
    )

    technique = models.CharField(
        "Technique of the test",
        max_length=150,
        blank=True,
    )

    kit_name = models.CharField(
        "Name of test kit",
        max_length=150,
        blank=True,
    )

    order = models.PositiveSmallIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return (
            self.kit_name
            or self.pathogen_condition
            or "Test Kit"
        )


class TestKitResponse(models.Model):
    """
    One answer for one Section 8 test kit question.
    """

    test_kit = models.ForeignKey(
        TestKitAssessed,
        related_name="responses",
        on_delete=models.CASCADE,
    )

    item_code = models.CharField(
        max_length=10,
    )

    response = models.CharField(
        max_length=2,
        choices=RESPONSE_CHOICES,
        blank=True,
    )

    comment = models.CharField(
        max_length=500,
        blank=True,
    )

    class Meta:
        unique_together = (
            "test_kit",
            "item_code",
        )

    def __str__(self):
        return (
            f"{self.test_kit_id} - "
            f"{self.item_code}"
        )


class NonConformity(models.Model):
    """
    Part D: Non-conformity report
    and recommendations.
    """

    CORRECTION_CHOICES = [
        ("onsite", "Onsite"),
        ("follow_up", "Follow up"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        related_name="non_conformities",
        on_delete=models.CASCADE,
    )

    section_number = models.CharField(
        max_length=10,
        blank=True,
    )

    details = models.CharField(
        max_length=500,
        blank=True,
    )

    correction_type = models.CharField(
        max_length=10,
        choices=CORRECTION_CHOICES,
        blank=True,
    )

    recommendations = models.CharField(
        max_length=500,
        blank=True,
    )

    def __str__(self):
        return (
            f"Non-conformity "
            f"{self.section_number or ''}"
        )