from datetime import date
import re

from django import forms
from django.contrib.auth import authenticate
from django.forms import formset_factory

from .models import Assessment, Facility
from .checklist_data import (
    SECTIONS,
    TEST_QUESTIONS,
    RESPONSE_CHOICES,
)


# =========================================================
# LOGIN FORM
# =========================================================

class RoleLoginForm(forms.Form):

    ROLE_CHOICES = [
        ("user", "User"),
        ("admin", "Admin"),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Login as",
        widget=forms.Select(
            attrs={
                "class": "login-input",
            }
        ),
    )

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "login-input",
                "placeholder": "Enter username",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "login-input",
                "placeholder": "Enter password",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        role = cleaned_data.get("role")

        if not username or not password or not role:
            return cleaned_data

        user = authenticate(
            self.request,
            username=username,
            password=password,
        )

        if user is None:
            raise forms.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive."
            )

        if role == "admin":
            if not (
                user.is_staff
                or user.is_superuser
            ):
                raise forms.ValidationError(
                    "This account is not an administrator account."
                )

        elif role == "user":
            if (
                user.is_staff
                or user.is_superuser
            ):
                raise forms.ValidationError(
                    "Please select Admin when logging in with an administrator account."
                )

        self.user_cache = user

        return cleaned_data

    def get_user(self):
        return self.user_cache


# =========================================================
# FACILITY LOOKUP FORM
# =========================================================

class FacilityLookupForm(forms.Form):

    mfl_code = forms.CharField(
        label="Facility MFL Code",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter MFL code",
                "autocomplete": "off",
            }
        ),
    )


# =========================================================
# ASSESSMENT INFORMATION
# =========================================================

class AssessmentInfoForm(forms.ModelForm):

    POC_TEST_CHOICES = [
        ("CRAG", "CRAG"),
        ("CRP", "CRP"),
        ("D-Dimers", "D-Dimers"),
        ("HBA1C", "HBA1C"),
        ("Hepatitis A", "Hepatitis A"),
        ("Hepatitis B", "Hepatitis B"),
        ("Hepatitis C", "Hepatitis C"),
        ("HIV TrinScreen", "HIV TrinScreen"),
        ("HIV Standard Q", "HIV Standard Q"),
        ("HIV First Response", "HIV First Response"),
        ("HIV One Step", "HIV One Step"),
        ("LF LAM", "LF LAM"),
        ("TB LAMP", "TB LAMP"),
        ("GeneXpert MTB/RIF", "GeneXpert MTB/RIF"),
        ("Malaria RDT", "Malaria RDT"),
        ("Random Blood Sugar", "Random Blood Sugar"),
        ("Rota AdenoviRus", "Rota AdenoviRus"),
        ("Salmonella Antigen Test", "Salmonella Antigen Test"),
        ("VDRL", "VDRL"),
        ("Thyroid TSH", "Thyroid TSH"),
        ("Thyroid T4", "Thyroid T4"),
        ("Urinalysis", "Urinalysis"),
        ("Hemoglobin", "Hemoglobin"),
        ("Pregnancy Test", "Pregnancy Test"),
        ("PSA", "PSA"),
    ]

    poc_tests_conducted = forms.MultipleChoiceField(
        required=False,
        label="List of POC tests conducted at this facility",
        choices=POC_TEST_CHOICES,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "poc-test-checkboxes",
            }
        ),
    )

    class Meta:
        model = Assessment

        fields = [
            "facility",
            "county_name",
            "sub_county",
            "facility_name",
            "facility_mfl_code",
            "site",
            "assessment_type",
            "date_of_assessment",
            "time_of_assessment",
            "date_of_previous_assessment",
            "facility_type",
            "facility_type_other",
            "level",
            "affiliation",
            "affiliation_other",
            "partner",
            "partner_specify",
            "physical_address",
            "interviewee_name",
            "interviewee_title",
            "interviewee_phone",
            "poc_tests_conducted",
            "assessors",
            "site_supervisor_name",
            "site_supervisor_date",
            "assessor_date",
        ]

        widgets = {

            "facility": forms.HiddenInput(),

            "county_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            "sub_county": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            "facility_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            "facility_mfl_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_facility_mfl_code",
                    "placeholder": "Enter facility MFL code",
                    "autocomplete": "off",
                }
            ),

            "site": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "assessment_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "date_of_assessment": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "max": date.today().isoformat(),
                }
            ),

            "time_of_assessment": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "date_of_previous_assessment": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "max": date.today().isoformat(),
                }
            ),

            "facility_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "facility_type_other": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "level": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "affiliation": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "affiliation_other": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "partner": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "partner_specify": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "physical_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "interviewee_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "interviewee_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "interviewee_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "assessors": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "site_supervisor_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "site_supervisor_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "max": date.today().isoformat(),
                }
            ),

            "assessor_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "max": date.today().isoformat(),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Facility is linked automatically using MFL code.
        self.fields["facility"].required = False

        # Do not load all 931 facilities into a dropdown.
        self.fields["facility"].queryset = Facility.objects.none()

        # Drafts are allowed.
        for field in self.fields.values():
            field.required = False

        # When editing an existing assessment, preserve
        # its linked facility and restore the saved A3 test list
        # into the checkbox field.
        if self.instance and self.instance.pk:
            if self.instance.facility_id:
                self.fields["facility"].initial = (
                    self.instance.facility_id
                )

            raw_tests = (
                self.instance.poc_tests_conducted
                or ""
            )

            saved_tests = [
                value.strip()
                for value in re.split(r"[,;\n]+", raw_tests)
                if value.strip()
            ]

            self.initial["poc_tests_conducted"] = saved_tests

    def clean_poc_tests_conducted(self):
        values = self.cleaned_data.get("poc_tests_conducted") or []
        return ", ".join(values)

    def clean_date_of_assessment(self):
        value = self.cleaned_data.get(
            "date_of_assessment"
        )

        if value and value > date.today():
            raise forms.ValidationError(
                "The assessment date cannot be in the future."
            )

        return value

    def clean_date_of_previous_assessment(self):
        value = self.cleaned_data.get(
            "date_of_previous_assessment"
        )

        if value and value > date.today():
            raise forms.ValidationError(
                "The previous assessment date cannot be in the future."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        mfl_code = (
            cleaned_data.get("facility_mfl_code")
            or ""
        ).strip()

        facility = cleaned_data.get("facility")

        assessment_date = cleaned_data.get(
            "date_of_assessment"
        )

        previous_date = cleaned_data.get(
            "date_of_previous_assessment"
        )

        # =====================================================
        # MFL CODE LOOKUP
        # =====================================================

        if mfl_code:

            # Exact database lookup after stripping spaces.
            facility_record = (
                Facility.objects
                .filter(
                    mfl_code__iexact=mfl_code
                )
                .first()
            )

            if facility_record is None:

                self.add_error(
                    "facility_mfl_code",
                    "No facility was found with this MFL code. Please check the code.",
                )

            else:

                # Link assessment to master facility.
                cleaned_data["facility"] = (
                    facility_record
                )

                # Always use the official MFL code.
                cleaned_data[
                    "facility_mfl_code"
                ] = facility_record.mfl_code

                # Always synchronize the facility information
                # with the master facility record.
                cleaned_data[
                    "facility_name"
                ] = facility_record.facility_name

                cleaned_data[
                    "county_name"
                ] = facility_record.county

                cleaned_data[
                    "sub_county"
                ] = facility_record.sub_county

        # =====================================================
        # FACILITY SELECTED DIRECTLY
        # =====================================================

        elif facility:

            cleaned_data[
                "facility_mfl_code"
            ] = facility.mfl_code

            cleaned_data[
                "facility_name"
            ] = facility.facility_name

            cleaned_data[
                "county_name"
            ] = facility.county

            cleaned_data[
                "sub_county"
            ] = facility.sub_county

        # =====================================================
        # A3 — STORE MULTI-SELECT AS THE EXISTING TEXT VALUE
        # =====================================================

        selected_tests = cleaned_data.get(
            "poc_tests_conducted"
        ) or []

        if isinstance(selected_tests, (list, tuple)):
            cleaned_data["poc_tests_conducted"] = ", ".join(
                selected_tests
            )

        # =====================================================
        # DATE VALIDATION
        # =====================================================

        if (
            assessment_date
            and previous_date
            and previous_date > assessment_date
        ):
            self.add_error(
                "date_of_previous_assessment",
                "The previous assessment date cannot be later than the current assessment date.",
            )

        return cleaned_data


# =========================================================
# STAFF MEMBERS
# =========================================================

class StaffMemberForm(forms.Form):

    name = forms.CharField(
        required=False,
        label="Name of staff",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    title = forms.CharField(
        required=False,
        label="Title of staff",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )


StaffMemberFormSet = formset_factory(
    StaffMemberForm,
    extra=1,
    max_num=50,
)


# =========================================================
# POC TEST STATISTICS
# =========================================================

class POCTestStatForm(forms.Form):

    period = forms.CharField(
        required=False,
        label="Month / Quarter / MM to MM Year",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. January to March 2025",
            }
        ),
    )

    type_of_test = forms.CharField(
        required=False,
        label="Type of Test Performed",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    tests_conducted = forms.CharField(
        required=False,
        label="# of tests conducted (Month / Quarter)",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    positives = forms.CharField(
        required=False,
        label="# Positives (Month / Quarter)",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    negatives = forms.CharField(
        required=False,
        label="# Negatives (Month / Quarter)",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    comments = forms.CharField(
        required=False,
        label="Comments",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": (
                    "e.g. If tests not conducted, state reason"
                ),
            }
        ),
    )


POCTestStatFormSet = formset_factory(
    POCTestStatForm,
    extra=1,
    max_num=50,
)


# =========================================================
# NON-CONFORMITIES
# =========================================================

class NonConformityForm(forms.Form):

    section_number = forms.CharField(
        required=False,
        label="Section No.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    details = forms.CharField(
        required=False,
        label="Details of non-conformity",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
            }
        ),
    )

    correction_type = forms.ChoiceField(
        required=False,
        label="Correction",
        choices=[
            ("", "---"),
            ("onsite", "Onsite"),
            ("follow_up", "Follow up"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    recommendations = forms.CharField(
        required=False,
        label="Recommendations",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
            }
        ),
    )


NonConformityFormSet = formset_factory(
    NonConformityForm,
    extra=1,
    max_num=50,
)


# =========================================================
# CHECKLIST
# =========================================================

class ChecklistForm(forms.Form):

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs,
        )

        for section in SECTIONS:

            for code, _text in section["items"]:

                field_name = self.field_name(
                    code
                )

                self.fields[
                    f"{field_name}_response"
                ] = forms.ChoiceField(
                    choices=RESPONSE_CHOICES,
                    required=False,
                    widget=forms.RadioSelect(),
                )

                self.fields[
                    f"{field_name}_comment"
                ] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(
                        attrs={
                            "class": (
                                "form-control "
                                "form-control-sm"
                            ),
                            "placeholder": (
                                "Reason/comment "
                                "(required for No or Partial)"
                            ),
                        }
                    ),
                )

    def clean(self):

        cleaned_data = super().clean()

        for section in SECTIONS:

            for code, _text in section["items"]:

                field_name = self.field_name(
                    code
                )

                response = (
                    cleaned_data.get(
                        f"{field_name}_response",
                        "",
                    )
                    or ""
                )

                comment = (
                    cleaned_data.get(
                        f"{field_name}_comment",
                        "",
                    )
                    or ""
                )

                if (
                    response in ["N", "P"]
                    and not comment.strip()
                ):

                    self.add_error(
                        f"{field_name}_comment",
                        (
                            "Please provide a reason when "
                            "the response is No or Partial."
                        ),
                    )

        return cleaned_data

    @staticmethod
    def field_name(code):

        return (
            "q_"
            + code.replace(".", "_")
        )


# =========================================================
# SECTION 8 — TEST KIT
# =========================================================

class TestKitForm(forms.Form):

    pathogen_condition = forms.CharField(
        required=False,
        label="Name of pathogen/condition tested",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    technique = forms.CharField(
        required=False,
        label="Technique of the test",
        help_text=(
            "e.g. Rapid Test, molecular, spectrophotometry etc."
        ),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    kit_name = forms.CharField(
        required=False,
        label="Name of test kit",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs,
        )

        for code, _text in TEST_QUESTIONS:

            field_name = self.field_name(
                code
            )

            self.fields[
                f"{field_name}_response"
            ] = forms.ChoiceField(
                choices=RESPONSE_CHOICES,
                required=False,
                widget=forms.RadioSelect(),
            )

            self.fields[
                f"{field_name}_comment"
            ] = forms.CharField(
                required=False,
                widget=forms.TextInput(
                    attrs={
                        "class": (
                            "form-control "
                            "form-control-sm"
                        ),
                        "placeholder": (
                            "Reason/comment "
                            "(required for No or Partial)"
                        ),
                    }
                ),
            )

    def clean(self):

        cleaned_data = super().clean()

        for code, _text in TEST_QUESTIONS:

            field_name = self.field_name(
                code
            )

            response = (
                cleaned_data.get(
                    f"{field_name}_response",
                    "",
                )
                or ""
            )

            comment = (
                cleaned_data.get(
                    f"{field_name}_comment",
                    "",
                )
                or ""
            )

            if (
                response in ["N", "P"]
                and not comment.strip()
            ):

                self.add_error(
                    f"{field_name}_comment",
                    (
                        "Please provide a reason when "
                        "the response is No or Partial."
                    ),
                )

        return cleaned_data

    @staticmethod
    def field_name(code):

        return (
            "t_"
            + code.replace(".", "_")
        )


TestKitFormSet = formset_factory(
    TestKitForm,
    extra=1,
    max_num=50,
)