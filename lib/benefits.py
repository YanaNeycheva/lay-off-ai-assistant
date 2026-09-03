"""Deterministic Bulgarian unemployment-benefit calculator.

Mirror of knowledge-base/bg-legal.md — keep in sync. This module holds the
DATE and MONEY math that must not be done in LLM prose. bg-legal.md (verified
by the freshness-checker subagent) is the SOURCE OF TRUTH for the constants;
this file is only the calculator. If the two drift, tests/test_benefits.py
(the drift test) fails.

Standard library only (datetime, calendar, decimal). No external deps, so it
runs anywhere Python 3 does and is safe to call from bg-navigator via `python`.

Constants and their bg-legal.md source:
  * 7 working days  — Bureau registration deadline
    ("Регистрация в Бюро по труда … Срок: 7 работни дни")
  * 3 calendar months — НОИ молба-декларация deadline
    ("Молба-декларация в НОИ … Срок: до 3 месеца")
  * чл. 54в КСО duration table — BENEFIT_DURATION_TABLE below
  * 60% of the average осигурителен доход — BENEFIT_RATE
  * 9.21 / 54.78 EUR daily min/max (2026) — DAILY_BENEFIT_MIN / _MAX
  * 2300 EUR max monthly осигурителен доход (from 01.08.2026) — MAX_INSURABLE_INCOME_EUR
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

# --------------------------------------------------------------------------
# Constants — mirror of knowledge-base/bg-legal.md. Keep in sync.
# --------------------------------------------------------------------------

# Бюро по труда (Агенция по заетостта): 7 working days from termination.
BUREAU_REGISTRATION_WORKING_DAYS = 7

# НОИ молба-декларация: within 3 calendar months of termination.
NOI_DECLARATION_MONTHS = 3

# Размер на обезщетението: 60% of the average осигурителен доход (24 мес).
BENEFIT_RATE = Decimal("0.60")

# Дневни граници на ПОБ (2026), in EUR. bg-legal.md, verified 2026-08-29.
DAILY_BENEFIT_MIN_EUR = Decimal("9.21")
DAILY_BENEFIT_MAX_EUR = Decimal("54.78")

# Максимален месечен осигурителен доход (from 01.08.2026), in EUR.
# bg-legal.md, verified 2026-08-29 — cap applied before computing the benefit.
MAX_INSURABLE_INCOME_EUR = Decimal("2300")

# Продължителност на изплащане — таблица по чл. 54в КСО.
# bg-legal.md, verified against НОИ 2026-09-03.
# Each entry: (upper bound of осигурителен стаж as (years, days) INCLUSIVE, months).
# Read as: до 3 г. → 4; 3 г. 1 д – 7 г. → 6; 7 г. 1 д – 11 г. → 8;
#          11 г. 1 д – 15 г. → 10; над 15 г. → 12.
BENEFIT_DURATION_TABLE = [
    ((3, 0), 4),
    ((7, 0), 6),
    ((11, 0), 8),
    ((15, 0), 10),
]
BENEFIT_DURATION_ABOVE_MAX_MONTHS = 12  # над 15 г.

# --------------------------------------------------------------------------
# BG official public holidays — PER-YEAR constant. ⚠️ UPDATE YEARLY.
# --------------------------------------------------------------------------
# Official non-working days per чл. 154 КТ, incl. the movable Orthodox Easter
# and the substitute Mondays under чл. 154, ал. 2 (a fixed holiday falling on
# Sat/Sun pushes the next working day(s) to non-working).
#
# 2026 set verified against official / reference sources on 2026-09-03:
#   * Orthodox Easter 2026 = Sun 12 Apr → Good Friday 10 Apr, Easter Monday 13 Apr
#     (sofiaglobe.com, holidays-info.com).
#   * Full 2026 calendar incl. the one-off 2 Jan euro-adoption day and the moved
#     Mondays (flagman.bg / egn.bg; МС decree for the euro day).
# NOTE: 1 November (Ден на народните будители) is a non-working day ONLY for
# educational institutions (чл. 154, ал. 1, т. 8), NOT a general labour holiday,
# so it is deliberately EXCLUDED from this working-day set.
#
# ⚠️ UPDATE YEARLY: recompute Easter, re-check the МС decree for one-off days,
# and recompute substitute Mondays before relying on this for a new year.
BG_PUBLIC_HOLIDAYS = {
    2026: frozenset({
        date(2026, 1, 1),    # Нова година
        date(2026, 1, 2),    # Еднократен неработен ден (въвеждане на еврото), обявен от МС
        date(2026, 3, 3),    # Ден на Освобождението
        date(2026, 4, 10),   # Велики петък
        date(2026, 4, 11),   # Велика събота (weekend anyway)
        date(2026, 4, 12),   # Великден (weekend anyway)
        date(2026, 4, 13),   # Велики понеделник
        date(2026, 5, 1),    # Ден на труда
        date(2026, 5, 6),    # Гергьовден
        date(2026, 5, 24),   # Ден на българската просвета и култура (Sun)
        date(2026, 5, 25),   # заместващ понеделник за 24 май
        date(2026, 9, 6),    # Съединение (Sun)
        date(2026, 9, 7),    # заместващ понеделник за 6 септември
        date(2026, 9, 22),   # Ден на Независимостта
        date(2026, 12, 24),  # Бъдни вечер
        date(2026, 12, 25),  # Рождество Христово
        date(2026, 12, 26),  # Рождество Христово (Sat)
        date(2026, 12, 28),  # заместващ понеделник за 26 декември
    }),
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _is_working_day(day: date) -> bool:
    """True if `day` is Mon–Fri and not an official BG public holiday.

    Days in a year we have no holiday table for fall back to weekday-only
    (weekends excluded); callers should keep BG_PUBLIC_HOLIDAYS current.
    """
    if day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False
    holidays = BG_PUBLIC_HOLIDAYS.get(day.year, frozenset())
    return day not in holidays


def bureau_registration_deadline(termination_date: date) -> date:
    """Deadline to register at the Бюро по труда: 7 WORKING days after termination.

    Working days are Mon–Fri excluding official BG public holidays. Counting
    starts the day after the termination date; the returned date is the 7th
    working day. Mirror of bg-legal.md ("Срок: 7 работни дни").
    """
    remaining = BUREAU_REGISTRATION_WORKING_DAYS
    day = termination_date
    while remaining > 0:
        day += timedelta(days=1)
        if _is_working_day(day):
            remaining -= 1
    return day


def is_bureau_registration_missed(termination_date: date, today: date) -> bool:
    """True if `today` is past the 7-working-day bureau registration deadline.

    Missing it does not forfeit the right (bg-legal.md), but the benefit is then
    counted from the later registration date — so flag it.
    """
    return today > bureau_registration_deadline(termination_date)


def noi_declaration_deadline(termination_date: date) -> date:
    """Deadline for the НОИ молба-декларация: +3 calendar months.

    Mirror of bg-legal.md ("Срок: до 3 месеца от прекратяването"). Day-of-month
    is clamped to the target month's length (e.g. 30 Nov → 28/29 Feb).
    """
    month_index = termination_date.month - 1 + NOI_DECLARATION_MONTHS
    year = termination_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(termination_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def benefit_duration_months(osig_staj_years: int, osig_staj_days: int = 0) -> int:
    """Months of benefit by осигурителен стаж — таблица по чл. 54в КСО.

    до 3 г. → 4; 3 г. 1 д – 7 г. → 6; 7 г. 1 д – 11 г. → 8;
    11 г. 1 д – 15 г. → 10; над 15 г. → 12. Bounds are handled exactly: an
    extra day past a whole-year bound tips into the next bracket. Mirror of
    bg-legal.md ("Продължителност … таблица по чл. 54в КСО").
    """
    staj = (osig_staj_years, osig_staj_days)
    for upper_bound, months in BENEFIT_DURATION_TABLE:
        if staj <= upper_bound:
            return months
    return BENEFIT_DURATION_ABOVE_MAX_MONTHS


def monthly_benefit_estimate(
    avg_monthly_osig_income_eur, working_days_in_month: int
) -> Decimal:
    """Estimated MONTHLY unemployment benefit (ПОБ), in EUR.

    Formula (mirror of bg-legal.md, "Размер и срок на изплащане"):
      1. Cap the average monthly осигурителен доход at MAX_INSURABLE_INCOME_EUR
         (2300 EUR from 01.08.2026).
      2. Daily осигурителен доход = capped monthly income / working days in month.
      3. Daily benefit = 60% of that daily income.
      4. Clamp the daily benefit to [9.21, 54.78] EUR (2026 daily min/max).
      5. Monthly benefit = daily benefit × working days in month
         ("месечната сума = дневен размер × работни дни в месеца").
    Returned as a Decimal rounded to 2 decimal places. This is an ESTIMATE —
    НОИ computes the daily доход over the real 24-month working-day count.
    """
    if working_days_in_month <= 0:
        raise ValueError("working_days_in_month must be positive")

    income = Decimal(str(avg_monthly_osig_income_eur))
    capped_income = min(income, MAX_INSURABLE_INCOME_EUR)
    working_days = Decimal(working_days_in_month)

    daily_income = capped_income / working_days
    daily_benefit = BENEFIT_RATE * daily_income

    # Clamp to the official daily bounds.
    if daily_benefit < DAILY_BENEFIT_MIN_EUR:
        daily_benefit = DAILY_BENEFIT_MIN_EUR
    elif daily_benefit > DAILY_BENEFIT_MAX_EUR:
        daily_benefit = DAILY_BENEFIT_MAX_EUR

    monthly = daily_benefit * working_days
    return monthly.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------
# Small CLI so bg-navigator can compute without doing math in prose.
# --------------------------------------------------------------------------

def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Deterministic BG unemployment-benefit calculator "
        "(mirror of knowledge-base/bg-legal.md)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_bureau = sub.add_parser("bureau-deadline", help="7-working-day bureau deadline")
    p_bureau.add_argument("termination_date", type=_parse_date, help="YYYY-MM-DD")

    p_noi = sub.add_parser("noi-deadline", help="+3-month НОИ deadline")
    p_noi.add_argument("termination_date", type=_parse_date, help="YYYY-MM-DD")

    p_dur = sub.add_parser("duration", help="чл. 54в benefit duration (months)")
    p_dur.add_argument("years", type=int, help="осигурителен стаж, whole years")
    p_dur.add_argument("days", type=int, nargs="?", default=0, help="residual days")

    p_est = sub.add_parser("estimate", help="estimated monthly benefit (EUR)")
    p_est.add_argument("avg_monthly_income", help="avg monthly осиг. доход, EUR")
    p_est.add_argument("working_days", type=int, help="working days in the month")

    p_all = sub.add_parser("all", help="everything for one person")
    p_all.add_argument("termination_date", type=_parse_date, help="YYYY-MM-DD")
    p_all.add_argument("years", type=int, help="осигурителен стаж, whole years")
    p_all.add_argument("days", type=int, nargs="?", default=0, help="residual days")
    p_all.add_argument("--income", help="avg monthly осиг. доход, EUR")
    p_all.add_argument("--working-days", type=int, help="working days in the month")

    args = parser.parse_args(argv)

    if args.command == "bureau-deadline":
        print(bureau_registration_deadline(args.termination_date).isoformat())
    elif args.command == "noi-deadline":
        print(noi_declaration_deadline(args.termination_date).isoformat())
    elif args.command == "duration":
        print(benefit_duration_months(args.years, args.days))
    elif args.command == "estimate":
        print(monthly_benefit_estimate(args.avg_monthly_income, args.working_days))
    elif args.command == "all":
        print(f"bureau_registration_deadline: "
              f"{bureau_registration_deadline(args.termination_date).isoformat()}")
        print(f"noi_declaration_deadline:     "
              f"{noi_declaration_deadline(args.termination_date).isoformat()}")
        print(f"benefit_duration_months:      "
              f"{benefit_duration_months(args.years, args.days)}")
        if args.income is not None and args.working_days is not None:
            print(f"monthly_benefit_estimate:     "
                  f"{monthly_benefit_estimate(args.income, args.working_days)} EUR")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
