"""
payroll_report_app.py — the quarter at a glance, for someone who never opens a terminal.

Every Friday since September the office manager at Salt City Coffee has downloaded
a payroll export from the Assignment 04 app; before that she typed the same file
by hand. The owner now wants to know where the hours went this quarter, the
accountant wants pay by month and department, and the manager wants to see who
has been missing shifts. This page answers all three from the pile of exports.

Same shape as Assignment 04: the page *assembles* the pipeline — one call to
`build_history` does the cleaning — and then shows the reports, filtered by the
department and dates the user picks.

Run it:  Run and Debug -> "Streamlit Run: Current File"
Test it: pytest tests/test_pipeline.py -k app
"""
# --- The page ---------------------------------------------------------------------
#
# No scaffolding. Every function this page needs already exists in the payroll
# package, and every widget it needs you used in Assignments 03 and 04 — plus two
# new ones, st.date_input and st.bar_chart. README Step 8 has the exact widgets,
# keys and labels; the tests in tests/test_pipeline.py -k app check them.
#
# The shape, in words:
#
#   title and a sentence of instructions
#   roster   <- load_employees()                           (fixed; not uploaded)
#   uploads  <- st.file_uploader, key="exports", accept_multiple_files=True
#               (an empty list until files are chosen)
#   if there are uploads:
#       history <- build_history([load_export(u) for u in uploads], roster)
#       st.warning naming any employeeid with no department (not on the roster);
#           the reports below use only the rows that matched
#       st.selectbox, key="department": "All" plus each department
#       st.date_input, key="dates": a (start, end) range, defaulting to the first
#           and last pay_date — compare against pay_date.dt.date to filter
#       the selection as a subheader
#       four st.metric cards in st.columns(4): Weeks, Employees, Total hours,
#           Total gross pay — counts are .nunique(), totals are .sum()
#       st.bar_chart of pay_by_month(selected), with month as the x axis
#       st.dataframe of summarize_employees(selected)
#       st.dataframe of hours_grid(selected), then of missed_weeks(that grid)
#       st.download_button, key="download": pay_by_month(...).to_csv(index=False)
#
# What the page does NOT do: cleaning, grouping, pivoting. If you find yourself
# writing a groupby or a pivot_table here, that logic belongs in the package.

import streamlit as st

from payroll import (
    build_history,
    hours_grid,
    load_employees,
    load_export,
    missed_weeks,
    pay_by_month,
    summarize_employees,
)

st.title("Salt City Coffee — Quarterly Payroll Report")
st.write(
    "Upload the weekly payroll exports for the quarter. The page cleans and "
    "combines them, then shows hours, pay and missed weeks for the department "
    "and dates you choose."
)

roster = load_employees()

uploads = st.file_uploader(
    "Weekly payroll exports (CSV)",
    type="csv",
    accept_multiple_files=True,
    key="exports",
)

if uploads:
    history = build_history([load_export(upload) for upload in uploads], roster)

    # IDs with no department were not on the roster: warn, then report on the rest.
    unmatched = history[history["department"].isna()]
    if not unmatched.empty:
        missing_ids = ", ".join(sorted(unmatched["employeeid"].astype(str).unique()))
        st.warning(
            f"These employee IDs are not on the roster and are left out of the "
            f"reports: {missing_ids}"
        )
    matched = history[history["department"].notna()]

    departments = sorted(matched["department"].unique())
    department = st.selectbox(
        "Department",
        ["All"] + departments,
        key="department",
    )

    first_day = matched["pay_date"].min().date()
    last_day = matched["pay_date"].max().date()
    dates = st.date_input(
        "Pay dates",
        value=(first_day, last_day),
        min_value=first_day,
        max_value=last_day,
        key="dates",
    )
    # While the user is mid-pick, date_input returns only the start date.
    if isinstance(dates, (tuple, list)) and len(dates) == 2:
        start, end = dates
    elif isinstance(dates, (tuple, list)):
        start = end = dates[0]
    else:
        start = end = dates

    selected = matched
    if department != "All":
        selected = selected[selected["department"] == department]
    pay_days = selected["pay_date"].dt.date
    selected = selected[(pay_days >= start) & (pay_days <= end)]

    st.subheader(f"{department} · {start} to {end}")

    if selected.empty:
        st.info("No pay rows match this department and date range.")
    else:
        weeks_col, people_col, hours_col, pay_col = st.columns(4)
        weeks_col.metric("Weeks", selected["week_ending"].nunique())
        people_col.metric("Employees", selected["employee_id"].nunique())
        hours_col.metric("Total hours", f"{selected['hours_worked'].sum():,.2f}")
        pay_col.metric("Total gross pay", f"${selected['gross_pay'].sum():,.2f}")

        monthly = pay_by_month(selected)

        st.subheader("Gross pay by month and department")
        st.bar_chart(monthly, x="month")

        st.subheader("Employee summary")
        st.dataframe(summarize_employees(selected))

        st.subheader("Hours by week")
        grid = hours_grid(selected)
        st.dataframe(grid)

        st.subheader("Missed weeks")
        st.dataframe(missed_weeks(grid))

        st.download_button(
            "Download pay by month (CSV)",
            data=monthly.to_csv(index=False),
            file_name="pay_by_month.csv",
            mime="text/csv",
            key="download",
        )