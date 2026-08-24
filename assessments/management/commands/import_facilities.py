from pathlib import Path

import pandas as pd

from django.core.management.base import BaseCommand, CommandError

from assessments.models import Facility


class Command(BaseCommand):
    help = "Import facility MFL codes and facility information from an Excel file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="mflcodes_and_facilities(1).xlsx",
            help="Path to the Excel file containing facility data.",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Facility records before importing.",
        )

    def handle(self, *args, **options):

        file_path = Path(options["file"])

        # =========================================================
        # CHECK THAT THE EXCEL FILE EXISTS
        # =========================================================

        if not file_path.exists():
            raise CommandError(
                f"Excel file was not found:\n"
                f"{file_path.resolve()}"
            )

        self.stdout.write(
            self.style.NOTICE(
                f"Reading Excel file:\n"
                f"{file_path.resolve()}"
            )
        )

        # =========================================================
        # READ EXCEL FILE
        # =========================================================

        try:
            dataframe = pd.read_excel(file_path)

        except Exception as exc:
            raise CommandError(
                f"Could not read the Excel file: {exc}"
            )

        # =========================================================
        # CLEAN COLUMN NAMES
        # =========================================================

        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        self.stdout.write(
            f"Columns found: {list(dataframe.columns)}"
        )

        # =========================================================
        # CHECK REQUIRED COLUMNS
        # =========================================================

        required_columns = {
            "county",
            "subcounty",
            "facility",
            "MFLCode",
        }

        missing_columns = (
            required_columns
            - set(dataframe.columns)
        )

        if missing_columns:
            raise CommandError(
                "The Excel file is missing these columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        # =========================================================
        # KEEP ONLY THE COLUMNS WE NEED
        # =========================================================

        dataframe = dataframe[
            [
                "county",
                "subcounty",
                "facility",
                "MFLCode",
            ]
        ].copy()

        # =========================================================
        # REMOVE ROWS WITHOUT AN MFL CODE
        # =========================================================

        dataframe = dataframe.dropna(
            subset=["MFLCode"]
        )

        # =========================================================
        # CLEAN VALUES
        # =========================================================

        dataframe["MFLCode"] = (
            dataframe["MFLCode"]
            .astype(str)
            .str.strip()
        )

        dataframe["county"] = (
            dataframe["county"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        dataframe["subcounty"] = (
            dataframe["subcounty"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        dataframe["facility"] = (
            dataframe["facility"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # REMOVE EMPTY MFL CODES
        # =========================================================

        dataframe = dataframe[
            dataframe["MFLCode"] != ""
        ]

        # =========================================================
        # REMOVE DUPLICATE MFL CODES
        # =========================================================

        dataframe = dataframe.drop_duplicates(
            subset=["MFLCode"],
            keep="first",
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Facilities ready for import: "
                f"{len(dataframe)}"
            )
        )

        # =========================================================
        # OPTIONAL: CLEAR EXISTING FACILITIES
        # =========================================================

        if options["clear"]:

            count = Facility.objects.count()

            Facility.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {count} existing facility records."
                )
            )

        # =========================================================
        # IMPORT FACILITIES
        # =========================================================

        created_count = 0
        updated_count = 0

        for _, row in dataframe.iterrows():

            mfl_code = str(
                row["MFLCode"]
            ).strip()

            county = str(
                row["county"]
            ).strip()

            sub_county = str(
                row["subcounty"]
            ).strip()

            facility_name = str(
                row["facility"]
            ).strip()

            facility, created = (
                Facility.objects.update_or_create(
                    mfl_code=mfl_code,
                    defaults={
                        "facility_name": facility_name,
                        "county": county,
                        "sub_county": sub_county,
                    },
                )
            )

            if created:
                created_count += 1

            else:
                updated_count += 1

        # =========================================================
        # FINAL SUMMARY
        # =========================================================

        total = Facility.objects.count()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "FACILITY IMPORT COMPLETE"
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Updated: {updated_count}"
        )

        self.stdout.write(
            f"Total facilities in database: {total}"
        )