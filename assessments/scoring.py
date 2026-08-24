"""Scoring logic for a saved Assessment.

Y = 2, P = 1, N = 0. N/A and blank responses are excluded.
Section 8 is stored separately and is deliberately inserted after Section 7
in the ordered section result returned to templates and future dashboards.
"""

from .checklist_data import SECTIONS, TEST_QUESTIONS, POINTS, get_level


def _score_responses(responses):
    obtained = 0
    possible = 0
    for response in responses:
        if response.response in POINTS:
            obtained += POINTS[response.response]
            possible += 2
    return obtained, possible


def _percentage(obtained, possible):
    if not possible:
        return None
    return round(100 * obtained / possible, 1)


def score_assessment(assessment):
    responses = list(assessment.checklist_responses.all())
    by_section = {}

    for section in SECTIONS:
        number = section["number"]
        section_responses = [
            r for r in responses if r.section_number == number
        ]
        obtained, possible = _score_responses(section_responses)
        by_section[number] = {
            "number": number,
            "name": section["name"],
            "obtained": obtained,
            "possible": possible,
            "percentage": _percentage(obtained, possible),
        }

    test_kit_scores = []
    section8_obtained = 0
    section8_possible = 0

    for kit in assessment.test_kits.all():
        obtained, possible = _score_responses(kit.responses.all())
        section8_obtained += obtained
        section8_possible += possible
        test_kit_scores.append({
            "kit": kit,
            "obtained": obtained,
            "possible": possible,
            "percentage": _percentage(obtained, possible),
        })

    section8 = {
        "number": 8,
        "name": "Test Kits",
        "obtained": section8_obtained,
        "possible": section8_possible,
        "percentage": _percentage(section8_obtained, section8_possible),
        "test_kits": test_kit_scores,
    }

    ordered_sections = []
    for number in range(1, 11):
        if number == 8:
            ordered_sections.append(section8)
        elif number in by_section:
            ordered_sections.append(by_section[number])

    checklist_obtained = sum(s["obtained"] for s in by_section.values())
    checklist_possible = sum(s["possible"] for s in by_section.values())
    total_obtained = checklist_obtained + section8_obtained
    total_possible = checklist_possible + section8_possible
    percentage = round(100 * total_obtained / total_possible, 1) if total_possible else 0

    if total_possible:
        level, level_description = get_level(percentage)
    else:
        level = None
        level_description = "No scoreable items yet"

    return {
        "by_section": by_section,
        "ordered_sections": ordered_sections,
        "section8": section8,
        "facility_score": percentage,
        "total_obtained": total_obtained,
        "total_possible": total_possible,
        "percentage": percentage,
        "level": level,
        "level_description": level_description,
    }
