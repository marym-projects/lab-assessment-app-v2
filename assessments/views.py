from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .models import (
    Assessment,
    Facility,
    StaffMember,
    POCTestStat,
    ChecklistResponse,
    TestKitAssessed,
    TestKitResponse,
    NonConformity,
)

from .forms import (
    RoleLoginForm,
    AssessmentInfoForm,
    FacilityLookupForm,
    StaffMemberFormSet,
    POCTestStatFormSet,
    ChecklistForm,
    TestKitFormSet,
    NonConformityFormSet,
)

from .checklist_data import (
    SECTIONS,
    TEST_QUESTIONS,
)

from .scoring import score_assessment


# =========================================================
# USER ACCESS
# =========================================================

def user_can_view_all_assessments(user):
    """
    Administrators/staff can view every assessment.

    Normal users can only view assessments
    they created.
    """

    return (
        user.is_staff
        or user.is_superuser
    )


def visible_assessments_for(user):
    """
    Return assessments the current user
    is allowed to see.
    """

    if user_can_view_all_assessments(user):
        return Assessment.objects.all()

    return Assessment.objects.filter(
        created_by=user
    )


def user_can_edit_assessment(
    user,
    assessment,
):
    """
    Staff/admin can edit everything.

    Normal users can edit their own
    assessments.

    Imported records are also editable by
    authorized users.
    """

    if user_can_view_all_assessments(user):
        return True

    return (
        assessment.created_by == user
    )


# =========================================================
# LOGIN
# =========================================================

class RoleBasedLoginView(LoginView):
    """
    Login page with Admin/User selection.
    """

    template_name = (
        "registration/login.html"
    )

    authentication_form = (
        RoleLoginForm
    )

    def form_valid(self, form):

        user = form.get_user()

        login(
            self.request,
            user,
            backend=(
                "django.contrib.auth.backends."
                "ModelBackend"
            ),
        )

        return redirect(
            "dashboard"
        )


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    assessments = (
        visible_assessments_for(
            request.user
        )
        .order_by("-created_at")
    )

    total_assessments = (
        assessments.count()
    )

    baseline_assessments = (
        assessments.filter(
            assessment_type__icontains="baseline"
        ).count()
    )

    follow_up_assessments = (
        assessments.filter(
            assessment_type__icontains="follow"
        ).count()
    )

    draft_assessments = (
        assessments.filter(
            status="draft"
        ).count()
    )

    completed_assessments = (
        assessments.filter(
            status="completed"
        ).count()
    )

    scores = []

    for assessment in assessments:

        try:
            result = score_assessment(
                assessment
            )

            score = result.get(
                "percentage"
            )

            if score is not None:
                scores.append(
                    float(score)
                )

        except Exception:
            pass

    average_score = (
        round(
            sum(scores)
            / len(scores),
            1,
        )
        if scores
        else 0
    )

    recent_assessments = (
        assessments[:10]
    )

    return render(
        request,
        "assessments/dashboard.html",
        {
            "total_assessments":
                total_assessments,

            "baseline_assessments":
                baseline_assessments,

            "follow_up_assessments":
                follow_up_assessments,

            "draft_assessments":
                draft_assessments,

            "completed_assessments":
                completed_assessments,

            "average_score":
                average_score,

            "recent_assessments":
                recent_assessments,
        },
    )


# =========================================================
# FACILITY LOOKUP
# =========================================================

@login_required
def facility_lookup(request):
    """
    Look up a facility by MFL code.

    AJAX requests receive JSON for the assessment form.
    Normal browser requests retain the standalone lookup page.
    """
    mfl_code = (request.GET.get("mfl_code") or "").strip()

    wants_json = (
        request.headers.get("Accept", "").lower().find("application/json") >= 0
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )

    if wants_json:
        if not mfl_code:
            return JsonResponse({"found": False, "message": "Enter an MFL code."})

        facility = Facility.objects.filter(
            mfl_code__iexact=mfl_code
        ).first()

        if facility is None:
            return JsonResponse({
                "found": False,
                "message": "No facility was found with this MFL code.",
            })

        return JsonResponse({
            "found": True,
            "facility": {
                "id": facility.pk,
                "mfl_code": facility.mfl_code,
                "facility_name": facility.facility_name or "",
                "county_name": getattr(facility, "county", "") or "",
                "sub_county": getattr(facility, "sub_county", "") or "",
                "facility_type": getattr(facility, "facility_type", "") or "",
                "level": getattr(facility, "level", "") or "",
                "affiliation": getattr(facility, "affiliation", "") or "",
                "physical_address": getattr(facility, "physical_address", "") or "",
            },
        })

    facility = None
    form = FacilityLookupForm(request.GET or None)

    if form.is_valid():
        code = (form.cleaned_data.get("mfl_code") or "").strip()
        if code:
            facility = Facility.objects.filter(mfl_code__iexact=code).first()
            if facility is None:
                messages.warning(request, "No facility was found with that MFL code.")

    return render(
        request,
        "assessments/facility_lookup.html",
        {"form": form, "facility": facility},
    )


# =========================================================
# FORM HELPERS
# =========================================================

def build_sections_for_template(
    checklist_form,
):
    """
    Build the checklist structure expected
    by the assessment template.
    """

    sections_for_template = []

    for section in SECTIONS:

        items = []

        for code, text in section[
            "items"
        ]:

            field_name = (
                ChecklistForm.field_name(
                    code
                )
            )

            items.append(
                {
                    "code": code,
                    "text": text,
                    "response_field": (
                        checklist_form[
                            f"{field_name}_response"
                        ]
                    ),
                    "comment_field": (
                        checklist_form[
                            f"{field_name}_comment"
                        ]
                    ),
                }
            )

        sections_for_template.append(
            {
                "number": section[
                    "number"
                ],
                "name": section[
                    "name"
                ],
                "note": section.get(
                    "note"
                ),
                "items": items,
            }
        )

    return sections_for_template


def build_testkits_for_template(
    testkit_formset,
):
    """
    Build Section 8 template data.
    """

    testkits_for_template = []

    for kit_form in testkit_formset:

        items = []

        for code, text in TEST_QUESTIONS:

            field_name = (
                kit_form.field_name(
                    code
                )
            )

            items.append(
                {
                    "code": code,
                    "text": text,
                    "response_field": (
                        kit_form[
                            f"{field_name}_response"
                        ]
                    ),
                    "comment_field": (
                        kit_form[
                            f"{field_name}_comment"
                        ]
                    ),
                }
            )

        testkits_for_template.append(
            {
                "form": kit_form,
                "items": items,
            }
        )

    return testkits_for_template


def build_empty_testkit_data(
    testkit_formset,
):
    """
    Build the empty Section 8 form used
    by the + Add Test Kit button.
    """

    empty_kit_form = (
        testkit_formset.empty_form
    )

    empty_kit_items = []

    for code, text in TEST_QUESTIONS:

        field_name = (
            empty_kit_form.field_name(
                code
            )
        )

        empty_kit_items.append(
            {
                "code": code,
                "text": text,
                "response_field": (
                    empty_kit_form[
                        f"{field_name}_response"
                    ]
                ),
                "comment_field": (
                    empty_kit_form[
                        f"{field_name}_comment"
                    ]
                ),
            }
        )

    return (
        empty_kit_form,
        empty_kit_items,
    )


def assessment_context(
    info_form,
    staff_formset,
    stats_formset,
    checklist_form,
    testkit_formset,
    nc_formset,
    assessment=None,
    edit_mode=False,
):
    """
    Build the common context used by the
    assessment form.
    """

    (
        empty_kit_form,
        empty_kit_items,
    ) = build_empty_testkit_data(
        testkit_formset
    )

    return {
        "assessment": assessment,
        "edit_mode": edit_mode,

        "info_form":
            info_form,

        "a1_excluded_fields": [
            "interviewee_name",
            "interviewee_title",
            "interviewee_phone",
            "poc_tests_conducted",
            "assessors",
            "site_supervisor_name",
            "site_supervisor_date",
            "assessor_date",
        ],

        "staff_formset":
            staff_formset,

        "stats_formset":
            stats_formset,

        "checklist_form":
            checklist_form,

        "sections":
            build_sections_for_template(
                checklist_form
            ),

        "testkit_formset":
            testkit_formset,

        "testkits":
            build_testkits_for_template(
                testkit_formset
            ),

        "empty_kit_form":
            empty_kit_form,

        "empty_kit_items":
            empty_kit_items,

        "nc_formset":
            nc_formset,
    }


# =========================================================
# SAVE STAFF
# =========================================================

def save_staff_formset(
    assessment,
    formset,
):
    """
    Replace the assessment's staff records
    with the submitted rows.
    """

    StaffMember.objects.filter(
        assessment=assessment
    ).delete()

    for form in formset:

        if not hasattr(
            form,
            "cleaned_data",
        ):
            continue

        data = form.cleaned_data

        if not data:
            continue

        if (
            data.get("name")
            or data.get("title")
        ):

            StaffMember.objects.create(
                assessment=assessment,
                name=data.get(
                    "name",
                    "",
                ),
                title=data.get(
                    "title",
                    "",
                ),
            )


# =========================================================
# SAVE POC STATISTICS
# =========================================================

def save_stats_formset(
    assessment,
    formset,
):
    """
    Replace POC statistics with the
    submitted rows.
    """

    POCTestStat.objects.filter(
        assessment=assessment
    ).delete()

    for form in formset:

        if not hasattr(
            form,
            "cleaned_data",
        ):
            continue

        data = form.cleaned_data

        if not data:
            continue

        if any(
            value
            for value in data.values()
        ):

            POCTestStat.objects.create(
                assessment=assessment,
                period=data.get(
                    "period",
                    "",
                ),
                type_of_test=data.get(
                    "type_of_test",
                    "",
                ),
                tests_conducted=data.get(
                    "tests_conducted",
                    "",
                ),
                positives=data.get(
                    "positives",
                    "",
                ),
                negatives=data.get(
                    "negatives",
                    "",
                ),
                comments=data.get(
                    "comments",
                    "",
                ),
            )


# =========================================================
# SAVE CHECKLIST
# =========================================================

def save_checklist(
    assessment,
    checklist_form,
):
    """
    Save checklist answers.

    Existing answers are updated rather than
    duplicated.
    """

    cleaned = (
        checklist_form.cleaned_data
    )

    for section in SECTIONS:

        for code, _text in section[
            "items"
        ]:

            field_name = (
                ChecklistForm.field_name(
                    code
                )
            )

            response = (
                cleaned.get(
                    f"{field_name}_response",
                    "",
                )
                or ""
            )

            comment = (
                cleaned.get(
                    f"{field_name}_comment",
                    "",
                )
                or ""
            )

            if response or comment:

                ChecklistResponse.objects.update_or_create(
                    assessment=assessment,
                    item_code=code,
                    defaults={
                        "section_number":
                            section[
                                "number"
                            ],
                        "response":
                            response,
                        "comment":
                            comment,
                    },
                )

            else:

                ChecklistResponse.objects.filter(
                    assessment=assessment,
                    item_code=code,
                ).delete()


# =========================================================
# SAVE SECTION 8
# =========================================================

def save_section_8(
    assessment,
    testkit_formset,
):
    """
    Replace Section 8 records with the
    submitted test-kit rows.

    This explicitly saves Section 8,
    which also fixes the previous problem
    where it could disappear from saved
    assessments.
    """

    TestKitAssessed.objects.filter(
        assessment=assessment
    ).delete()

    for order, form in enumerate(
        testkit_formset
    ):

        if not hasattr(
            form,
            "cleaned_data",
        ):
            continue

        data = form.cleaned_data

        if not data:
            continue

        header_filled = (
            data.get(
                "pathogen_condition"
            )
            or data.get(
                "technique"
            )
            or data.get(
                "kit_name"
            )
        )

        any_answer = False

        for code, _text in TEST_QUESTIONS:

            field_name = (
                form.field_name(
                    code
                )
            )

            response = (
                data.get(
                    f"{field_name}_response"
                )
                or ""
            )

            comment = (
                data.get(
                    f"{field_name}_comment"
                )
                or ""
            )

            if response or comment:
                any_answer = True
                break

        if not (
            header_filled
            or any_answer
        ):
            continue

        kit = (
            TestKitAssessed.objects.create(
                assessment=assessment,
                pathogen_condition=data.get(
                    "pathogen_condition",
                    "",
                ),
                technique=data.get(
                    "technique",
                    "",
                ),
                kit_name=data.get(
                    "kit_name",
                    "",
                ),
                order=order,
            )
        )

        for code, _text in TEST_QUESTIONS:

            field_name = (
                form.field_name(
                    code
                )
            )

            response = (
                data.get(
                    f"{field_name}_response",
                    "",
                )
                or ""
            )

            comment = (
                data.get(
                    f"{field_name}_comment",
                    "",
                )
                or ""
            )

            if response or comment:

                TestKitResponse.objects.create(
                    test_kit=kit,
                    item_code=code,
                    response=response,
                    comment=comment,
                )


# =========================================================
# SAVE NON-CONFORMITIES
# =========================================================

def save_non_conformities(
    assessment,
    formset,
):
    """
    Replace non-conformity records with
    submitted rows.
    """

    NonConformity.objects.filter(
        assessment=assessment
    ).delete()

    for form in formset:

        if not hasattr(
            form,
            "cleaned_data",
        ):
            continue

        data = form.cleaned_data

        if not data:
            continue

        if any(
            value
            for value in data.values()
        ):

            NonConformity.objects.create(
                assessment=assessment,
                section_number=data.get(
                    "section_number",
                    "",
                ),
                details=data.get(
                    "details",
                    "",
                ),
                correction_type=data.get(
                    "correction_type",
                    "",
                ),
                recommendations=data.get(
                    "recommendations",
                    "",
                ),
            )


# =========================================================
# LOAD EXISTING ASSESSMENT DATA
# =========================================================

def build_existing_forms(
    assessment,
):
    """
    Load an existing assessment back into
    all of the forms so it can be edited.
    """

    info_form = AssessmentInfoForm(
        instance=assessment
    )

    # -----------------------------------------------------
    # STAFF
    # -----------------------------------------------------

    staff_rows = list(
        assessment.staff_members.values(
            "name",
            "title",
        )
    )

    staff_formset = StaffMemberFormSet(
        prefix="staff",
        initial=staff_rows
        if staff_rows
        else None,
    )

    # -----------------------------------------------------
    # POC STATISTICS
    # -----------------------------------------------------

    stats_rows = list(
        assessment.test_stats.values(
            "period",
            "type_of_test",
            "tests_conducted",
            "positives",
            "negatives",
            "comments",
        )
    )

    stats_formset = POCTestStatFormSet(
        prefix="stats",
        initial=stats_rows
        if stats_rows
        else None,
    )

    # -----------------------------------------------------
    # CHECKLIST
    # -----------------------------------------------------

    checklist_initial = {}

    for response in (
        assessment.checklist_responses.all()
    ):

        field_name = (
            ChecklistForm.field_name(
                response.item_code
            )
        )

        checklist_initial[
            f"{field_name}_response"
        ] = response.response

        checklist_initial[
            f"{field_name}_comment"
        ] = response.comment

    checklist_form = ChecklistForm(
        initial=checklist_initial
    )

    # -----------------------------------------------------
    # SECTION 8
    # -----------------------------------------------------

    testkit_initial = []

    for kit in (
        assessment.test_kits.all()
    ):

        row = {
            "pathogen_condition":
                kit.pathogen_condition,

            "technique":
                kit.technique,

            "kit_name":
                kit.kit_name,
        }

        for response in (
            kit.responses.all()
        ):

            field_name = (
                TestKitFormSet.form.field_name(
                    response.item_code
                )
                if hasattr(
                    TestKitFormSet,
                    "form",
                )
                else (
                    "t_"
                    + response.item_code.replace(
                        ".",
                        "_",
                    )
                )
            )

            row[
                f"{field_name}_response"
            ] = response.response

            row[
                f"{field_name}_comment"
            ] = response.comment

        testkit_initial.append(
            row
        )

    testkit_formset = TestKitFormSet(
        prefix="testkit",
        initial=testkit_initial
        if testkit_initial
        else None,
    )

    # -----------------------------------------------------
    # NON-CONFORMITIES
    # -----------------------------------------------------

    nc_rows = list(
        assessment.non_conformities.values(
            "section_number",
            "details",
            "correction_type",
            "recommendations",
        )
    )

    nc_formset = NonConformityFormSet(
        prefix="nc",
        initial=nc_rows
        if nc_rows
        else None,
    )

    return (
        info_form,
        staff_formset,
        stats_formset,
        checklist_form,
        testkit_formset,
        nc_formset,
    )


# =========================================================
# NEW ASSESSMENT
# =========================================================

@login_required
def assessment_create(request):
    """
    Create a new assessment.

    The assessment is saved as a draft first.
    This means the assessor does not have to
    complete every section before the record
    exists.

    The existing template can still submit the
    complete assessment in one POST.
    """

    if request.method == "POST":

        info_form = AssessmentInfoForm(
            request.POST
        )

        staff_formset = StaffMemberFormSet(
            request.POST,
            prefix="staff",
        )

        stats_formset = POCTestStatFormSet(
            request.POST,
            prefix="stats",
        )

        checklist_form = ChecklistForm(
            request.POST
        )

        testkit_formset = TestKitFormSet(
            request.POST,
            prefix="testkit",
        )

        nc_formset = NonConformityFormSet(
            request.POST,
            prefix="nc",
        )

        info_valid = (
            info_form.is_valid()
        )

        staff_valid = (
            staff_formset.is_valid()
        )

        stats_valid = (
            stats_formset.is_valid()
        )

        checklist_valid = (
            checklist_form.is_valid()
        )

        testkit_valid = (
            testkit_formset.is_valid()
        )

        nc_valid = (
            nc_formset.is_valid()
        )

        if all(
            [
                info_valid,
                staff_valid,
                stats_valid,
                checklist_valid,
                testkit_valid,
                nc_valid,
            ]
        ):

            with transaction.atomic():

                assessment = (
                    info_form.save(
                        commit=False
                    )
                )

                assessment.created_by = (
                    request.user
                )

                # Always start as a draft.
                # Completion is handled explicitly.
                assessment.status = (
                    "draft"
                )

                assessment.last_completed_step = 1

                assessment.source = (
                    "live"
                )

                assessment.save()

                save_staff_formset(
                    assessment,
                    staff_formset,
                )

                save_stats_formset(
                    assessment,
                    stats_formset,
                )

                save_checklist(
                    assessment,
                    checklist_form,
                )

                save_section_8(
                    assessment,
                    testkit_formset,
                )

                save_non_conformities(
                    assessment,
                    nc_formset,
                )

            messages.success(
                request,
                (
                    "Assessment saved as a draft. "
                    "You can continue editing it."
                ),
            )

            return redirect(
                "assessment_detail",
                pk=assessment.pk,
            )

        messages.error(
            request,
            (
                "The assessment could not be saved. "
                "Please check the highlighted errors."
            ),
        )

    else:

        initial = {
            "date_of_assessment":
                date.today(),
        }

        info_form = AssessmentInfoForm(
            initial=initial
        )

        staff_formset = (
            StaffMemberFormSet(
                prefix="staff"
            )
        )

        stats_formset = (
            POCTestStatFormSet(
                prefix="stats"
            )
        )

        checklist_form = (
            ChecklistForm()
        )

        testkit_formset = (
            TestKitFormSet(
                prefix="testkit"
            )
        )

        nc_formset = (
            NonConformityFormSet(
                prefix="nc"
            )
        )

    context = assessment_context(
        info_form=info_form,
        staff_formset=staff_formset,
        stats_formset=stats_formset,
        checklist_form=checklist_form,
        testkit_formset=testkit_formset,
        nc_formset=nc_formset,
        edit_mode=False,
    )

    return render(
        request,
        "assessments/assessment_form.html",
        context,
    )


# =========================================================
# EDIT ASSESSMENT
# =========================================================

@login_required
def assessment_edit(
    request,
    pk,
):
    """
    Edit an existing draft or completed
    assessment.

    Completed assessments can be reopened
    for review/correction by an authorized user.
    """

    assessment = get_object_or_404(
        Assessment,
        pk=pk,
    )

    if not user_can_edit_assessment(
        request.user,
        assessment,
    ):

        messages.error(
            request,
            (
                "You do not have permission "
                "to edit this assessment."
            ),
        )

        return redirect(
            "my_assessments"
        )

    if request.method == "POST":

        info_form = AssessmentInfoForm(
            request.POST,
            instance=assessment,
        )

        staff_formset = (
            StaffMemberFormSet(
                request.POST,
                prefix="staff",
            )
        )

        stats_formset = (
            POCTestStatFormSet(
                request.POST,
                prefix="stats",
            )
        )

        checklist_form = ChecklistForm(
            request.POST
        )

        testkit_formset = (
            TestKitFormSet(
                request.POST,
                prefix="testkit",
            )
        )

        nc_formset = (
            NonConformityFormSet(
                request.POST,
                prefix="nc",
            )
        )

        if all(
            [
                info_form.is_valid(),
                staff_formset.is_valid(),
                stats_formset.is_valid(),
                checklist_form.is_valid(),
                testkit_formset.is_valid(),
                nc_formset.is_valid(),
            ]
        ):

            with transaction.atomic():

                assessment = (
                    info_form.save()
                )

                save_staff_formset(
                    assessment,
                    staff_formset,
                )

                save_stats_formset(
                    assessment,
                    stats_formset,
                )

                save_checklist(
                    assessment,
                    checklist_form,
                )

                save_section_8(
                    assessment,
                    testkit_formset,
                )

                save_non_conformities(
                    assessment,
                    nc_formset,
                )

            messages.success(
                request,
                "Assessment updated successfully.",
            )

            return redirect(
                "assessment_detail",
                pk=assessment.pk,
            )

        messages.error(
            request,
            (
                "Please correct the errors "
                "before saving."
            ),
        )

    else:

        (
            info_form,
            staff_formset,
            stats_formset,
            checklist_form,
            testkit_formset,
            nc_formset,
        ) = build_existing_forms(
            assessment
        )

    context = assessment_context(
        info_form=info_form,
        staff_formset=staff_formset,
        stats_formset=stats_formset,
        checklist_form=checklist_form,
        testkit_formset=testkit_formset,
        nc_formset=nc_formset,
        assessment=assessment,
        edit_mode=True,
    )

    return render(
        request,
        "assessments/assessment_form.html",
        context,
    )


# =========================================================
# COMPLETE ASSESSMENT
# =========================================================

@login_required
def assessment_complete(
    request,
    pk,
):
    """
    Explicitly mark an assessment as completed.

    This is intentionally separate from saving
    a draft.
    """

    assessment = get_object_or_404(
        Assessment,
        pk=pk,
    )

    if not user_can_edit_assessment(
        request.user,
        assessment,
    ):

        messages.error(
            request,
            (
                "You do not have permission "
                "to complete this assessment."
            ),
        )

        return redirect(
            "my_assessments"
        )

    if request.method != "POST":

        return redirect(
            "assessment_detail",
            pk=assessment.pk,
        )

    # -----------------------------------------------------
    # Basic completion validation
    # -----------------------------------------------------

    missing_fields = []

    if not assessment.facility_name:
        missing_fields.append(
            "Facility name"
        )

    if not assessment.facility_mfl_code:
        missing_fields.append(
            "Facility MFL code"
        )

    if not assessment.date_of_assessment:
        missing_fields.append(
            "Assessment date"
        )

    if not assessment.assessment_type:
        missing_fields.append(
            "Assessment type"
        )

    if not assessment.assessors:
        missing_fields.append(
            "Assessor(s)"
        )

    if missing_fields:

        messages.error(
            request,
            (
                "The assessment cannot be completed "
                "yet. Missing: "
                + ", ".join(
                    missing_fields
                )
            ),
        )

        return redirect(
            "assessment_edit",
            pk=assessment.pk,
        )

    assessment.status = (
        "completed"
    )

    assessment.last_completed_step = 10

    assessment.save(
        update_fields=[
            "status",
            "last_completed_step",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Assessment marked as completed.",
    )

    return redirect(
        "assessment_detail",
        pk=assessment.pk,
    )


# =========================================================
# MY ASSESSMENTS
# =========================================================

@login_required
def my_assessments(request):

    assessments = (
        visible_assessments_for(
            request.user
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "assessments/my_assessments.html",
        {
            "assessments":
                assessments,

            "is_admin":
                user_can_view_all_assessments(
                    request.user
                ),
        },
    )


# =========================================================
# REPORTS
# =========================================================

@login_required
def reports(request):

    assessments = (
        visible_assessments_for(
            request.user
        )
        .order_by("-created_at")
    )

    report_rows = []

    for assessment in assessments:

        try:
            result = score_assessment(
                assessment
            )

        except Exception:

            result = {
                "percentage": 0,
            }

        report_rows.append(
            {
                "assessment":
                    assessment,

                "result":
                    result,
            }
        )

    return render(
        request,
        "assessments/reports.html",
        {
            "report_rows":
                report_rows,

            "is_admin":
                user_can_view_all_assessments(
                    request.user
                ),
        },
    )


# =========================================================
# ASSESSMENT DETAIL
# =========================================================

@login_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)

    if not user_can_edit_assessment(request.user, assessment):
        messages.error(request, "You do not have permission to view this assessment.")
        return redirect("my_assessments")

    result = score_assessment(assessment)

    response_map = {
        r.item_code: {"response": r.response, "comment": r.comment}
        for r in assessment.checklist_responses.all()
    }
    detail_sections = []
    for section in SECTIONS:
        items = []
        for code, text in section["items"]:
            saved = response_map.get(code, {"response": "", "comment": ""})
            items.append({
                "code": code,
                "text": text,
                "response": saved["response"],
                "comment": saved["comment"],
            })
        detail_sections.append({
            "number": section["number"],
            "name": section["name"],
            "note": section.get("note"),
            "items": items,
        })

    section_8 = []
    for kit in assessment.test_kits.all():
        responses = {
            r.item_code: {"response": r.response, "comment": r.comment}
            for r in kit.responses.all()
        }
        question_rows = []
        for code, text in TEST_QUESTIONS:
            saved = responses.get(code, {"response": "", "comment": ""})
            question_rows.append({
                "code": code,
                "text": text,
                "response": saved["response"],
                "comment": saved["comment"],
            })
        section_8.append({"kit": kit, "questions": question_rows})

    return render(
        request,
        "assessments/assessment_detail.html",
        {
            "assessment": assessment,
            "result": result,
            "detail_sections": detail_sections,
            "section_8": section_8,
            "staff_members": assessment.staff_members.all(),
            "test_stats": assessment.test_stats.all(),
            "non_conformities": assessment.non_conformities.all(),
        },
    )


@login_required
def assessment_report(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    if not user_can_edit_assessment(request.user, assessment):
        messages.error(request, "You do not have permission to view this report.")
        return redirect("my_assessments")
    return render(
        request,
        "assessments/report.html",
        {"assessment": assessment, "result": score_assessment(assessment)},
    )

