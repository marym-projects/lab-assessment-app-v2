from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, timedelta
import random

from assessments.models import (
    Facility,
    Assessment,
    StaffMember,
    POCTestStat,
    ChecklistResponse,
    TestKitAssessed,
    TestKitResponse,
    NonConformity,
)
from assessments.checklist_data import (
    RESPONSE_CHOICES,
    SECTIONS,
    TEST_QUESTIONS,
)


class Command(BaseCommand):
    help = "Generate realistic fake assessment data for dashboard testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=25,
            help="Number of fake assessments to create (default: 25).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing TEST assessments before generating new ones.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if count < 1:
            self.stdout.write(self.style.ERROR("--count must be at least 1."))
            return

        if clear:
            deleted, _ = Assessment.objects.filter(source="test").delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted} existing test assessment records."
                )
            )

        facilities = list(Facility.objects.all().order_by("id"))

        if not facilities:
            self.stdout.write(
                self.style.ERROR(
                    "No facilities exist. Import your facility master list first."
                )
            )
            return

        random.seed(20260824)

        response_values = [value for value, _label in RESPONSE_CHOICES]

        if not response_values:
            self.stdout.write(
                self.style.ERROR("No RESPONSE_CHOICES were found.")
            )
            return

        positive = self.find_response(response_values, "Y")
        partial = self.find_response(response_values, "P")
        negative = self.find_response(response_values, "N")
        na = self.find_response(response_values, "NA")

        # Build the actual checklist directly from checklist_data.py.
        # No discovery or guessing is used.
        checklist_items = []

        for section in SECTIONS:
            section_number = str(section["number"])

            for item_code, question_text in section["items"]:
                checklist_items.append(
                    (
                        section_number,
                        str(item_code),
                        question_text,
                    )
                )

        # Section 8 is repeated for every test kit.
        section8_items = [
            (str(item_code), question_text)
            for item_code, question_text in TEST_QUESTIONS
        ]

        self.stdout.write(
            f"Loaded {len(checklist_items)} questions for Sections "
            "1-7, 9 and 10."
        )
        self.stdout.write(
            f"Loaded {len(section8_items)} questions for Section 8."
        )

        test_catalogue = [
            ("HIV", "Rapid diagnostic test", "Determine HIV-1/2"),
            ("Malaria", "Rapid diagnostic test", "CareStart Malaria"),
            ("Hepatitis B", "Rapid diagnostic test", "SD Bioline HBsAg"),
            ("Pregnancy", "Lateral flow", "One Step Pregnancy Test"),
            ("Syphilis", "Rapid diagnostic test", "SD Bioline Syphilis"),
        ]

        today = timezone.localdate()
        created_count = 0
        checklist_created = 0
        section8_created = 0
        kit_count_total = 0

        for index in range(count):
            facility = facilities[index % len(facilities)]

            assessment_date = today - timedelta(
                days=random.randint(0, 365)
            )

            previous_date = None
            if random.random() < 0.78:
                previous_date = assessment_date - timedelta(
                    days=random.randint(60, 420)
                )

            # Create meaningful score variation between facilities.
            performance = random.random()

            if performance < 0.12:
                compliance = 0.55
            elif performance < 0.32:
                compliance = 0.68
            elif performance < 0.72:
                compliance = 0.82
            elif performance < 0.93:
                compliance = 0.91
            else:
                compliance = 0.97

            selected_tests = random.sample(
                test_catalogue,
                random.randint(2, 4),
            )

            poc_test_names = [
                test_name
                for test_name, _technique, _kit_name in selected_tests
            ]

            partner = random.choice(
                [
                    "gok",
                    "gok_coag",
                    "county_government",
                    "partner",
                ]
            )

            assessment = Assessment.objects.create(
                facility=facility,
                county_name=facility.county or "",
                sub_county=facility.sub_county or "",
                facility_name=facility.facility_name,
                facility_mfl_code=facility.mfl_code,
                site=random.choice(
                    [
                        "Main Laboratory",
                        "POC Site",
                        "OPD",
                        "Laboratory",
                    ]
                ),
                assessment_type="Routine Assessment",
                date_of_assessment=assessment_date,
                time_of_assessment=random_time(),
                date_of_previous_assessment=previous_date,
                facility_type=facility_type_value(),
                level=random.choice(["2", "3", "4", "5", "6"]),
                affiliation=random.choice(
                    [
                        "government",
                        "private",
                        "faith_based",
                        "ngo",
                    ]
                ),
                affiliation_other="",
                partner=partner,
                partner_specify=(
                    "Test Partner" if partner == "partner" else ""
                ),
                physical_address=(
                    f"{facility.sub_county or 'County'} Health Facility"
                ),
                interviewee_name=random.choice(
                    [
                        "Jane Wanjiku",
                        "Peter Otieno",
                        "Mary Achieng",
                        "David Kamau",
                        "Grace Njeri",
                    ]
                ),
                interviewee_title=random.choice(
                    [
                        "Laboratory Manager",
                        "Laboratory Technologist",
                        "POC Coordinator",
                        "Medical Officer",
                        "Nurse in Charge",
                    ]
                ),
                interviewee_phone=random_phone(),

                # A3 is the master list used by Section 8.
                poc_tests_conducted=", ".join(poc_test_names),

                assessors=random.choice(
                    [
                        "Assessment Team A",
                        "Assessment Team B",
                        "County Laboratory Team",
                    ]
                ),
                site_supervisor_name=random.choice(
                    [
                        "John Mwangi",
                        "Lucy Atieno",
                        "Samuel Kiptoo",
                    ]
                ),
                site_supervisor_date=assessment_date,
                assessor_date=assessment_date,
                status="completed",
                source="test",
                last_completed_step=10,
            )

            # ---------------------------------------------------------
            # STAFF
            # ---------------------------------------------------------
            staff_names = [
                ("Jane Wanjiku", "Laboratory Technologist"),
                ("Peter Otieno", "Laboratory Technologist"),
                ("Grace Njeri", "Nurse"),
                ("David Kamau", "POC Coordinator"),
            ]

            for name, title in random.sample(
                staff_names,
                random.randint(1, 3),
            ):
                StaffMember.objects.create(
                    assessment=assessment,
                    name=name,
                    title=title,
                )

            # ---------------------------------------------------------
            # A4: independent POC statistics
            # ---------------------------------------------------------
            periods = random.sample(
                [
                    "Jan-Mar",
                    "Apr-Jun",
                    "Jul-Sep",
                    "Oct-Dec",
                ],
                random.randint(1, 3),
            )

            for period in periods:
                selected_a4_tests = random.sample(
                    poc_test_names,
                    random.randint(
                        1,
                        min(3, len(poc_test_names)),
                    ),
                )

                for test_name in selected_a4_tests:
                    conducted = random.randint(20, 250)
                    positives = random.randint(
                        0,
                        max(1, conducted // 5),
                    )
                    negatives = conducted - positives

                    POCTestStat.objects.create(
                        assessment=assessment,
                        period=period,
                        type_of_test=test_name,
                        tests_conducted=str(conducted),
                        positives=str(positives),
                        negatives=str(negatives),
                        comments=random.choice(
                            [
                                "",
                                "Routine monthly testing.",
                                "Results reviewed by supervisor.",
                                "Stock and testing records reviewed.",
                            ]
                        ),
                    )

            # ---------------------------------------------------------
            # SECTIONS 1-7, 9 AND 10
            # ---------------------------------------------------------
            for section_number, item_code, _question in checklist_items:
                value = self.random_response(
                    compliance,
                    positive,
                    partial,
                    negative,
                    na,
                )

                ChecklistResponse.objects.create(
                    assessment=assessment,
                    section_number=section_number,
                    item_code=item_code[:10],
                    response=value,
                    comment=response_comment(
                        value,
                        positive,
                    ),
                )

                checklist_created += 1

            # ---------------------------------------------------------
            # SECTION 8
            # ---------------------------------------------------------
            for kit_index, (
                test_name,
                technique,
                kit_name,
            ) in enumerate(selected_tests):

                kit = TestKitAssessed.objects.create(
                    assessment=assessment,
                    pathogen_condition=test_name,
                    technique=technique,
                    kit_name=kit_name,
                    order=kit_index,
                )

                kit_count_total += 1

                # Explicitly create every 8.1-8.15 response.
                for item_code, _question in section8_items:
                    value = self.random_response(
                        compliance,
                        positive,
                        partial,
                        negative,
                        na,
                        section8=True,
                    )

                    TestKitResponse.objects.create(
                        test_kit=kit,
                        item_code=item_code[:10],
                        response=value,
                        comment=response_comment(
                            value,
                            positive,
                            section8=True,
                        ),
                    )

                    section8_created += 1

            # ---------------------------------------------------------
            # NON-CONFORMITIES
            # ---------------------------------------------------------
            if random.random() < 0.62:
                for _ in range(random.randint(1, 3)):
                    NonConformity.objects.create(
                        assessment=assessment,
                        section_number=str(
                            random.randint(1, 10)
                        ),
                        details=random.choice(
                            [
                                "Required documentation was incomplete.",
                                "Quality control records require updating.",
                                "Staff competency evidence was incomplete.",
                                "Some supplies were not adequately documented.",
                                "Follow-up evidence was not available during assessment.",
                            ]
                        ),
                        correction_type=random.choice(
                            [
                                "onsite",
                                "follow_up",
                            ]
                        ),
                        recommendations=random.choice(
                            [
                                "Update records and review with the supervisor.",
                                "Provide refresher training and repeat the check.",
                                "Complete corrective action and verify during follow-up.",
                            ]
                        ),
                    )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} fake assessments successfully."
            )
        )
        self.stdout.write(
            f"Created {checklist_created} checklist responses "
            "for Sections 1-7, 9 and 10."
        )
        self.stdout.write(
            f"Created {kit_count_total} Section 8 test kits."
        )
        self.stdout.write(
            f"Created {section8_created} Section 8 responses "
            "(8.1-8.15 for every test kit)."
        )
        self.stdout.write(
            "A3 POC test names match the Section 8 test kits."
        )
        self.stdout.write(
            "A4 POC statistics are populated independently."
        )
        self.stdout.write(
            "All generated assessments use source='test', so they can "
            "be removed safely with --clear."
        )

    @staticmethod
    def find_response(values, wanted):
        for value in values:
            if str(value).strip().upper() == wanted.upper():
                return value

        # Fall back safely if a project has custom response values.
        return values[0]

    @staticmethod
    def random_response(
        compliance,
        positive,
        partial,
        negative,
        na,
        section8=False,
    ):
        roll = random.random()

        # N/A is deliberately uncommon so it does not dominate scoring.
        if na and roll < (0.025 if section8 else 0.04):
            return na

        if roll < compliance:
            return positive

        if partial and roll < compliance + 0.12:
            return partial

        return negative


def response_comment(value, positive, section8=False):
    if value == positive:
        return ""

    comments = [
        "Action required.",
        "Follow-up needed.",
        "Evidence not available.",
        "Corrective action required.",
    ]

    if section8:
        comments.extend(
            [
                "Review test procedure and document evidence.",
                "Verify implementation during follow-up.",
            ]
        )

    return random.choice(comments)


def random_phone():
    return f"07{random.randint(10000000, 99999999)}"


def random_time():
    return time(
        hour=random.randint(8, 16),
        minute=random.choice([0, 15, 30, 45]),
    )


def facility_type_value():
    return random.choice(
        [
            "dispensary",
            "health_centre",
            "sub_county_hospital",
            "county_hospital",
            "national_hospital",
            "other",
        ]
    )
