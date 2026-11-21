import argparse


def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    compounds_per_year: int,
    total_years: float,
) -> tuple[float, float]:
    if principal < 0:
        raise ValueError("principal must be non-negative")
    if annual_rate < 0:
        raise ValueError("annual rate must be non-negative")
    if compounds_per_year <= 0:
        raise ValueError("compounds per year must be positive")
    if total_years < 0:
        raise ValueError("total years must be non-negative")

    rate_per_period = annual_rate / 100 / compounds_per_year
    total_periods = compounds_per_year * total_years
    final_amount = principal * (1 + rate_per_period) ** total_periods
    interest_earned = final_amount - principal
    return final_amount, interest_earned


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate compound interest."
    )
    parser.add_argument("principal", type=float, help="Initial principal")
    parser.add_argument(
        "annual_rate",
        type=float,
        help="Annual interest rate as a percentage",
    )
    parser.add_argument(
        "compounds_per_year",
        type=int,
        help="Number of compounding periods per year",
    )
    parser.add_argument(
        "total_years",
        type=float,
        help="Total time in years",
    )
    args = parser.parse_args()

    try:
        final_amount, interest_earned = calculate_compound_interest(
            args.principal,
            args.annual_rate,
            args.compounds_per_year,
            args.total_years,
        )
    except ValueError as error:
        parser.error(str(error))

    print(f"Final amount: ${final_amount:,.2f}")
    print(f"Interest earned: ${interest_earned:,.2f}")


if __name__ == "__main__":
    main()
