- Use `tools/compound_interest.py` when the user asks to calculate compound interest.
- Accept principal, annual interest rate, compounds per year, and total years as numeric inputs.
- Convert 8 years and 7 months to `8.583333333333334` years when the script argument must be a decimal.
- Require a positive `compounds_per_year` value.
- Invoke the script from the project root:
  `python3 tools/compound_interest.py <principal> <annual_rate_percent> <compounds_per_year> <total_years>`
- Use the annual rate as a percentage, not a decimal.
- Example:
  `python3 tools/compound_interest.py 15847 7.34 12 8.583333333333334`
- Present the script's final amount and interest earned unchanged.
- Format currency values with a dollar sign and two decimal places.
- State the compounding assumption, including the compounds-per-year value and total term.
- Do not calculate or present a result only from this instruction when the required numeric inputs are missing.
