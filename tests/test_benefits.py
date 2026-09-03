"""Unit tests for lib/benefits.py — run with `python -m unittest discover`.

Stdlib unittest only (no pytest). Covers the deadline math, the чл. 54в
duration boundaries, the benefit-estimate clamps, and a DRIFT test that ties
lib/benefits.py's constants back to knowledge-base/bg-legal.md.
"""

import os
import re
import sys
import unittest
from datetime import date
from decimal import Decimal

# Make the repo root importable regardless of how discover is invoked
# (e.g. `python -m unittest discover` or `... discover -s tests`).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from lib import benefits  # noqa: E402


class TestBureauDeadline(unittest.TestCase):
    def test_spans_weekend_and_holiday(self):
        # Termination Wed 8 Apr 2026. The 7 working days skip Good Friday
        # (10 Apr), the 11–12 Apr weekend, Easter Monday (13 Apr), and the
        # 18–19 Apr weekend → deadline Tue 21 Apr 2026.
        self.assertEqual(
            benefits.bureau_registration_deadline(date(2026, 4, 8)),
            date(2026, 4, 21),
        )

    def test_plain_case(self):
        # Termination Fri 14 Aug 2026, no August holidays → 7 working days
        # land on Tue 25 Aug 2026.
        self.assertEqual(
            benefits.bureau_registration_deadline(date(2026, 8, 14)),
            date(2026, 8, 25),
        )

    def test_already_missed(self):
        # Termination 14 Aug 2026; "today" 3 Sep 2026 is well past the
        # 25 Aug deadline → registration is overdue.
        self.assertTrue(
            benefits.is_bureau_registration_missed(
                date(2026, 8, 14), today=date(2026, 9, 3)
            )
        )

    def test_not_yet_missed(self):
        # On the deadline day itself it is not yet missed.
        self.assertFalse(
            benefits.is_bureau_registration_missed(
                date(2026, 8, 14), today=date(2026, 8, 25)
            )
        )


class TestNoiDeadline(unittest.TestCase):
    def test_plain_three_months(self):
        self.assertEqual(
            benefits.noi_declaration_deadline(date(2026, 8, 14)),
            date(2026, 11, 14),
        )

    def test_month_end_clamp(self):
        # 30 Nov + 3 months → Feb, which has no 30th → clamp to 28 Feb 2027.
        self.assertEqual(
            benefits.noi_declaration_deadline(date(2026, 11, 30)),
            date(2027, 2, 28),
        )

    def test_year_rollover(self):
        self.assertEqual(
            benefits.noi_declaration_deadline(date(2026, 12, 31)),
            date(2027, 3, 31),
        )


class TestBenefitDuration(unittest.TestCase):
    """чл. 54в boundaries: exactly 3y, 3y+1d, 7y, 7y+1d, 11y, 15y, 15y+1d."""

    def test_exactly_3y(self):
        self.assertEqual(benefits.benefit_duration_months(3, 0), 4)

    def test_3y_1d(self):
        self.assertEqual(benefits.benefit_duration_months(3, 1), 6)

    def test_exactly_7y(self):
        self.assertEqual(benefits.benefit_duration_months(7, 0), 6)

    def test_7y_1d(self):
        self.assertEqual(benefits.benefit_duration_months(7, 1), 8)

    def test_exactly_11y(self):
        self.assertEqual(benefits.benefit_duration_months(11, 0), 8)

    def test_exactly_15y(self):
        self.assertEqual(benefits.benefit_duration_months(15, 0), 10)

    def test_15y_1d(self):
        self.assertEqual(benefits.benefit_duration_months(15, 1), 12)

    def test_below_3y(self):
        self.assertEqual(benefits.benefit_duration_months(0, 0), 4)

    def test_well_above_15y(self):
        self.assertEqual(benefits.benefit_duration_months(30, 0), 12)


class TestMonthlyBenefitEstimate(unittest.TestCase):
    def test_normal_no_clamp(self):
        # 1500 EUR/mo, 21 working days: daily income 71.43, ×60% = 42.86,
        # within [9.21, 54.78] → monthly = 0.60 × 1500 = 900.00.
        self.assertEqual(
            benefits.monthly_benefit_estimate(1500, 21),
            Decimal("900.00"),
        )

    def test_clamped_to_min(self):
        # Very low income → daily benefit below 9.21 → floored to 9.21/day.
        self.assertEqual(
            benefits.monthly_benefit_estimate(200, 21),
            Decimal("9.21") * 21,  # 193.41
        )

    def test_clamped_to_max_uses_income_cap(self):
        # 2500 EUR is above the 2300 cap; even capped, daily benefit exceeds
        # 54.78 → ceiled to 54.78/day → monthly = 54.78 × 21.
        self.assertEqual(
            benefits.monthly_benefit_estimate(2500, 21),
            Decimal("54.78") * 21,  # 1150.38
        )

    def test_returns_two_decimal_places(self):
        result = benefits.monthly_benefit_estimate(1500, 21)
        self.assertEqual(result.as_tuple().exponent, -2)

    def test_zero_working_days_rejected(self):
        with self.assertRaises(ValueError):
            benefits.monthly_benefit_estimate(1500, 0)


class TestDriftAgainstKnowledgeBase(unittest.TestCase):
    """Fail if lib/benefits.py drifts from knowledge-base/bg-legal.md.

    Reads both files as text. Each key constant must appear in bg-legal.md
    (guards against an unmirrored KB edit) AND in lib/benefits.py (guards
    against the calculator drifting from the KB).
    """

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO_ROOT, "knowledge-base", "bg-legal.md"),
                  encoding="utf-8") as fh:
            cls.kb = fh.read()
        with open(os.path.join(REPO_ROOT, "lib", "benefits.py"),
                  encoding="utf-8") as fh:
            cls.lib = fh.read()

    def test_daily_bounds_present_in_both(self):
        for value in ("9.21", "54.78"):
            self.assertIn(value, self.kb, f"{value} missing from bg-legal.md")
            self.assertIn(value, self.lib, f"{value} missing from lib/benefits.py")

    def test_income_cap_present_in_both(self):
        self.assertIn("2300", self.kb, "2300 cap missing from bg-legal.md")
        self.assertIn("2300", self.lib, "2300 cap missing from lib/benefits.py")

    def test_chl54v_months_match(self):
        # Pull every "→ N мес" month figure out of bg-legal.md.
        kb_months = {int(m) for m in re.findall(r"→\s*(\d+)\s*мес", self.kb)}
        self.assertTrue(kb_months, "no чл. 54в months found in bg-legal.md")

        lib_months = {m for _, m in benefits.BENEFIT_DURATION_TABLE}
        lib_months.add(benefits.BENEFIT_DURATION_ABOVE_MAX_MONTHS)

        self.assertEqual(
            kb_months, lib_months,
            "чл. 54в months in lib/benefits.py drift from bg-legal.md",
        )

    def test_chl54v_ordered_table(self):
        ordered = [m for _, m in benefits.BENEFIT_DURATION_TABLE]
        ordered.append(benefits.BENEFIT_DURATION_ABOVE_MAX_MONTHS)
        self.assertEqual(ordered, [4, 6, 8, 10, 12])


if __name__ == "__main__":
    unittest.main()
