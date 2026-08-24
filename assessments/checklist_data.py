"""
All the fixed question text from the SPI-RT Laboratory (POC) Assessment tool.
Kept as plain Python data (not database rows) because the questions never
change per-facility -- only the *answers* do. This is the single place to
edit if the wording of a question needs to change.

Each section is a dict:
    {
        "number": 1,
        "name": "ORGANISATION AND MANAGEMENT",
        "items": [ ("1.1", "question text"), ("1.2", "question text"), ... ],
    }

SECTIONS holds every scored section EXCEPT section 8 (Testing), because
section 8 is repeated once per test/pathogen the facility performs, not
just once per facility.

TEST_QUESTIONS holds the 15 fixed sub-questions (8.1 - 8.15) that get
asked for every test kit entered by the user.
"""

SECTIONS = [
    {
        "number": 1,
        "name": "ORGANISATION AND MANAGEMENT",
        "items": [
            ("1.1", "Is there a current facility organogram that shows lines of authority including the designated POCT Site Coordinator / Laboratory Lead?"),
            ("1.2", "Does each healthcare worker involved in POCT have a current job description that includes their POCT-specific roles and responsibilities?"),
            ("1.3", "Are regular facility / debriefing meetings held (at least monthly) and are minutes available?"),
            ("1.4", "Is the current national/county POCT guideline available and accessible at the testing site?"),
            ("1.5", "Are copies of previous assessment reports available?"),
            ("1.6", "Is there documented evidence that non-conformities identified during the previous assessment/supervision have been addressed within agreed timelines?"),
            ("1.7", "Has the County or Sub-County Health Management Team provided administrative or technical support supervision in the last quarter?"),
            ("1.8", "Does the facility have a systematic mechanism for collecting client/patient feedback on POCT services, with documented evidence of its use in the last quarter?"),
            ("1.9", "Has the facility held documented quality review or performance review meetings involving POCT staff in the last quarter? (Ref: Guideline Section 2.12)"),
            ("1.10", "Is there a designated POCT Site Coordinator or Laboratory Lead responsible for day-to-day POCT oversight at this facility?"),
            ("1.11", "Does the facility have an active Facility-Level POCT Committee with documented meeting records?"),
        ],
    },
    {
        "number": 2,
        "name": "PERSONNEL TRAINING & CERTIFICATION",
        "items": [
            ("2.1", "Have all personnel performing the POCT completed a standardized formal training program before performing patient testing? Are there training logs and attestation for that? (training must cover: test procedures, QC, biosafety, IPC, documentation, and instrument maintenance) (Ref: Guideline 2.3.1)"),
            ("2.2", "Are valid and up-to-date training certificates available and on file for all active POCT testers at this facility?"),
            ("2.3", "Have all active POCT testers received documented refresher training (including on any new test or procedure introduced) within the last 12 months?"),
            ("2.4", "Are formal competency assessments conducted for all POCT testers at least annually, using a documented multi-method approach (e.g., direct observation, QC review, written test)? (Ref: Guideline 2.3.2)"),
            ("2.5", "Are training records and competency assessment documentation maintained and accessible for review?"),
            ("2.6", "Have all POCT testers received specific documented training on biosafety, biosecurity, and Infection Prevention and Control (IPC)? (Ref: Guideline Section 3.5 training curriculum)"),
        ],
    },
    {
        "number": 3,
        "name": "PHYSICAL FACILITY",
        "items": [
            ("3.1", "Is there a designated area for POCT?"),
            ("3.2", "Is the testing area access-controlled and secure?"),
            ("3.3", "Is the testing area clean, well-ventilated, and organized to prevent cross-contamination?"),
            ("3.4", "Is sufficient lighting available in the designated testing area?"),
            ("3.5", "Are there suitable facilities for secure storage of test kits and reagents stored according to the manufacturer's instructions?"),
            ("3.6", "Is there a designated specimen reception area appropriate for the tests performed?"),
        ],
    },
    {
        "number": 4,
        "name": "SAFETY",
        "items": [
            ("4.1", "Are current SOPs and/or job aids in place to implement safety practices, with evidence of ongoing implementation, including procedures for accidental exposure management, spill management, waste segregation, and proper hand hygiene."),
            ("4.2", "Are personal protective equipment (PPE) available to testers?"),
            ("4.3", "Do all testers properly and consistently use PPE throughout the testing process?"),
            ("4.4", "Is clean water and soap (or hand sanitizer) available for hand washing, and being used by testers?"),
            ("4.5", "Is there an appropriate disinfectant available?"),
            ("4.6", "Is the disinfectant properly labelled with content, date of preparation and expiration?"),
            ("4.7", "Is biohazard waste (infectious and non-infectious) properly segregated, handled, and disposed of in accordance with national biosafety and environmental guidelines?"),
            ("4.8", "Have all Health care service providers been vaccinated against Hepatitis B virus?"),
            ("4.9", "Is there a documented procedure for reporting and managing accidental exposure incidents (e.g., needlestick injury), with evidence of implementation? (Ref: Guideline 2.16)"),
        ],
    },
    {
        "number": 5,
        "name": "COMMODITY MANAGEMENT",
        "items": [
            ("5.1", "Are adequate test kits and consumables available for all tests?"),
            ("5.2", "Is there an up-to-date commodity management system in place?"),
            ("5.3", "Are only in-date reagents and test kits used?"),
            ("5.4", "Are expired kits/reagents documented and separated awaiting disposal?"),
            ("5.5", "Are storage conditions (temperature, humidity) monitored daily, and are records of any deviations available? (Ref: Guideline 3.11)"),
            ("5.6", "Does the facility submit accurate monthly consumption and stock status reports to the sub-county level through the approved reporting platform (e.g., KHIS 706, 643B)? (Ref: Guideline 3.9)"),
        ],
    },
    {
        "number": 6,
        "name": "EQUIPMENT MANAGEMENT",
        "items": [
            ("6.1", "Is there an updated equipment management SOP in place?"),
            ("6.2", "Is there documented evidence that calibration and calibration verification of all auxiliary equipment (e.g., pipettes, thermometers, timers) has been performed at specified intervals?"),
            ("6.3", "Are equipment daily maintenance charts available and up-to-date?"),
            ("6.4", "Where applicable, are current service contracts or maintenance agreements in place for POCT equipment? If not applicable, is a documented maintenance schedule in place?"),
        ],
    },
    {
        "number": 7,
        "name": "QUALITY ASSURANCE",
        "items": [
            ("7.1", "Is QC testing routinely performed in accordance with SOPs? Including for new consignment, monthly QC, and new lots."),
            ("7.2", "Are QC result logs regularly reviewed by a designated supervisor, and is there documented evidence of this review? (Ref: Guideline 2.7)"),
            ("7.3", "Is this facility enrolled in a national EQA/Proficiency Testing (PT) scheme for each POCT method offered, with evidence of active participation? (Ref: Guideline 2.8)"),
            ("7.4", "Are EQA/PT reports formally reviewed by a designated laboratory professional, with documented review records?"),
            ("7.5", "Is there documented evidence of Corrective and Preventive Action (CAPA) being implemented for every unsatisfactory EQA/PT result or QC failure, within defined timelines?"),
            ("7.6", "Is the facility actively implementing a Continuous Quality Improvement (CQI) program (e.g., RT-CQI or equivalent disease-agnostic framework)? (Ref: Guideline 2.10)"),
            ("7.7", "Are structured quality review meetings held involving multidisciplinary teams (laboratory, clinical, QA) to analyze QC/EQA trends and identify root causes? (Ref: Guideline 2.12)"),
            ("7.8", "Has the site actively participated in post-market surveillance (PMS) activities for applicable devices?"),
        ],
    },
    {
        "number": 9,
        "name": "SPECIMEN REFERRAL",
        "note": "If the testing facility does not refer specimens, mark N/A for every question in this section.",
        "items": [
            ("9.1", "Is there a current guideline/SOP on specimen referral?"),
            ("9.2", "Are records in place for specimen referral?"),
            ("9.3", "Is there a current SOP for specimen rejection and are records available?"),
            ("9.4", "Are adequate triple packaging materials available and correctly used as per SOP?"),
            ("9.5", "Are drivers/riders trained on biosafety and are annual refresher trainings conducted?"),
            ("9.6", "Does the referring facility receive back results from the reference lab?"),
            ("9.7", "Is there appropriate storage for referred specimens?"),
        ],
    },
    {
        "number": 10,
        "name": "COMMUNITY TESTING",
        "note": "The respondent for this section is the CHA (Community Health Assistant), Facility In-charge, or Laboratory Supervisor.",
        "items": [
            ("10.1", "Do the CHPs have a valid training certificate for each test they perform?"),
            ("10.2", "Are all test kits in use within their expiry date?"),
            ("10.3", "Are only nationally approved test kits being used?"),
            ("10.4", "Are QCs done for all new test kit consignments before distribution to the CHPs, during change of lot and every month? Are records available and reviewed?"),
            ("10.5", "Are test kits stored correctly per manufacturer instructions (temperature, away from sunlight)?"),
            ("10.6", "Are current job aid(s) or illustrated procedure guide available and accessible to the CHPs during testing?"),
            ("10.7", "Are appropriate PPEs (gloves at minimum) available to the CHPs and do they use them for every test?"),
            ("10.8", "Is infectious waste (used sharps, strips, swabs, gloves) segregated and disposed of correctly?"),
            ("10.9", "Is a register available to the CHPs and does the register capture all quality indicators: date, client ID, test name, test results?"),
            ("10.10", "Is a standard register available to the CHPs and does it capture all quality indicators: date, client ID, test name, test results?"),
            ("10.11", "Are abnormal/positive results acted upon with appropriate client referral to the linked facility?"),
            ("10.12", "Is there documented evidence that referred clients reached the health facility (feedback loop)?"),
            ("10.13", "Are monthly test summary reports submitted to the linked facility on time?"),
        ],
    },
]

# Section 8 (TESTING) is evaluated once per pathogen/test the facility performs.
TEST_QUESTIONS = [
    ("8.1", "Is the test and its associated kit/equipment approved by national authorities? (kmlttb.org/validation/reagents/ or products.pharmacyboardkenya.org)"),
    ("8.2", "Is the current testing algorithm(s) available and consistently used?"),
    ("8.3", "Are current testing SOPs / Job Aids available and easily accessible?"),
    ("8.4", "Is a standardized register available and in use?"),
    ("8.5", "Does the register include all key quality elements? e.g. kit/assay name, expiry date, kit lot number, client ID, date of testing, tester ID, test result, and QC result reference. (Ref: Guideline 2.2.1)"),
    ("8.6", "Is testing conducted in accordance with SOPs?"),
    ("8.7", "Are invalid test results documented, test repeated and results recorded in the register?"),
    ("8.8", "Are records available for the turnaround time of test results?"),
    ("8.9", "Is there a current record for specimen rejection?"),
    ("8.10", "Are records available to compare the ratio of specimens received to the number tested?"),
    ("8.11", "Does the site have appropriate and functional equipment for the test?"),
    ("8.12", "Does the site use test kit contents appropriately? Is there evidence that test kit components are used in full accordance with the manufacturer's instructions (e.g., correct sample volume, correct buffer, within stated time limits)?"),
    ("8.13", "Are validation reports / certificates for all test kits and equipment available from the manufacturer?"),
    ("8.14", "Is there documented evidence of device/method verification having been performed before the test kit or equipment was put into use? (Ref: Guideline 2.5)"),
    ("8.15", "Are test results communicated to the clinician/patient in a timely manner, with evidence of the reporting pathway? (Ref: Guideline 2.4)"),
]

RESPONSE_CHOICES = [
    ("Y", "Yes"),
    ("P", "Partial"),
    ("N", "No"),
    ("NA", "N/A"),
]

POINTS = {"Y": 2, "P": 1, "N": 0}  # NA is excluded from scoring entirely

LEVELS = [
    (90, 4, "Eligible to national site certification"),
    (80, 3, "Close to national site certification"),
    (60, 2, "Partially eligible"),
    (50, 1, "Needs improvement in specific areas"),
    (0, 0, "Needs improvement in all areas and immediate remediation"),
]


def get_level(percentage):
    """Return (level_number, description) for a given percentage score."""
    for threshold, level, desc in LEVELS:
        if percentage >= threshold:
            return level, desc
    return 0, LEVELS[-1][2]
