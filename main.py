import streamlit as st
import math
import pandas as pd

st.title("HDB Resale Purchase Calculator")

st.write("#### CPF Housing Grants")

col1, col2, col3 = st.columns(3)
ftg = col1.number_input(
    "First Timer Grant ($)",
    min_value=0.0,
    value=0.0,
    max_value=80000.0,
    step=40000.0
)
ehg = col1.number_input(
    "Enhanced Housing Grant ($)",
    min_value=0.0,
    value=0.0,
    max_value=120000.0,
    step=5000.0
)
phg = col1.number_input(
    "Proximity Housing Grant ($)",
    min_value=0.0,
    value=0.0,
    max_value=30000.0,
    step=10000.0
)

total_grants = ftg + ehg + phg
col3.metric(label="Total Grants", value=f"${total_grants:,.0f}")
st.divider()

st.write("#### Purchase Breakdown")

col1, col2, col3 = st.columns(3)
purchase_price = col1.number_input(
    label="Purchase Price ($)",
    min_value=200000.0,
    value=300000.0,
    step=500.0
)
hdb_valuation = col1.number_input(
    label="HDB Valuation ($)",
    min_value=200000.0,
    value=300000.0,
    step=500.0,
    max_value=purchase_price
)
stretch_tenure = col1.toggle(
    label="Stretch Tenure",
    value=False,
    help="Stretching Tenure would result in lower loan to value.")

cov = purchase_price - hdb_valuation
downpayment_cash = hdb_valuation * \
    0.05 if not stretch_tenure else hdb_valuation * 0.10
downpayment_cpf = hdb_valuation * \
    0.20 if not stretch_tenure else hdb_valuation * 0.35
downpayment_loan = hdb_valuation * \
    0.75 if not stretch_tenure else hdb_valuation * 0.55

col3.metric(label="COV", value=f"${cov:,.0f}")
col3.metric(label="5% Cash" if not stretch_tenure else "10% Cash",
            value=f"${downpayment_cash:,.0f}")
col3.metric(label="20% CPF" if not stretch_tenure else "35% CPF",
            value=f"${downpayment_cpf:,.0f}")
col3.metric(label="75% Loan" if not stretch_tenure else "55% Loan",
            value=f"${downpayment_loan:,.0f}")

st.divider()

st.write("#### Loan Requirement")

col1, col2, col3 = st.columns(3)

loan_required = col1.number_input(
    "Loan Required ($)",
    min_value=0.0,
    value=downpayment_loan + (downpayment_cpf - total_grants),
    max_value=downpayment_loan + (downpayment_cpf - total_grants),
    step=1000.00
)

loan_eligible = col1.number_input(
    "Loan Eligible ($)",
    min_value=0.0,
    value=loan_required,
    max_value=loan_required,
    step=1000.0
)
interest_rate = col1.number_input(
    "Interest (%)",
    min_value=1.0,
    value=2.6,
    step=0.05,
)
loan_term = col1.number_input(
    "Term (Years)",
    min_value=5,
    value=25 if not stretch_tenure else 30,
    max_value=25 if not stretch_tenure else 30
)

monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12
monthly_payment = (
    loan_eligible
    * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
    / ((1 + monthly_interest_rate) ** number_of_payments - 1)
)
total_payments = monthly_payment * number_of_payments
total_interest = total_payments - loan_eligible

# Create a dataframe with the repayment schedule
schedule = []
remaining_balance = loan_eligible

for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    penalty = remaining_balance * 0.015
    year = math.ceil(i/12)
    schedule.append(
        [
            year,
            i,
            monthly_payment,
            principal_payment,
            interest_payment,
            remaining_balance,
            penalty
        ]
    )


col3.metric(label="Loan Amount", value=f"${loan_eligible:,.0f}")
col3.metric(label="Monthly", value=f"${monthly_payment:,.0f}")
col3.metric(label="Total", value=f"${total_payments:,.0f}")
col3.metric(label="Interest", value=f"${total_interest:,.0f}")

st.divider()


def calculate_bsd(purchase_price):
    if purchase_price <= 180000:
        bsd = purchase_price * 0.01
    elif purchase_price <= 360000:
        bsd = purchase_price * 0.02 - 1800
    elif purchase_price <= 1000000:
        bsd = purchase_price * 0.03 - 5400
    elif purchase_price <= 1500000:
        bsd = purchase_price * 0.04 - 15400
    elif purchase_price <= 3000000:
        bsd = purchase_price * 0.05 - 30400
    else:
        bsd = purchase_price * 0.06 - 60400
    return bsd


st.write("#### Cash Outlay")
col1, col2, col3 = st.columns(3)
valuation_fee = 120
submission_fee = 80
bsd = calculate_bsd(purchase_price)
legal_fee = 1788
shortfall_loan = loan_required - loan_eligible

col1.metric(
    label="Cash Over Valuation", value=f"+ ${cov:,.0f}")
col1.metric(
    label="Valuation Fee", value=f"+ ${valuation_fee:,.0f}")
col1.metric(
    label="Submission Fee", value=f"+ ${submission_fee:,.0f}")
col1.metric(
    label="Buyer Stamp Duty",
    value=f"+ ${bsd:,.0f}",
    help="As Stamp Duty is payable within 14 days from the date of purchase, you will need to pay Buyer's Stamp Duty (BSD) in cash first. Subsequently obtain reimbursement from your CPF account.")
col1.metric(
    label="Legal Fee", value=f"+ ${legal_fee:,.0f}")
col1.metric(
    label="5% Cash" if not stretch_tenure else "10% Cash",
    value=f"+ ${downpayment_cash:,.0f}")
col1.metric(
    label="Loan Shortfall",
    value=f"+ ${shortfall_loan:,.0f}")

total_cash_outlay = cov + valuation_fee + submission_fee + \
    bsd + legal_fee + downpayment_cash + shortfall_loan
col3.metric(label="Total", value=f"= ${total_cash_outlay:,.0f}")

st.divider()

st.write("#### Sale Breakdown")
col1, col2, col3 = st.columns(3)

selling_price = col1.number_input(
    "Selling Price ($)",
    min_value=0.0,
    value=purchase_price,
    step=1000.00
)
holding_period = col1.number_input(
    "Holding Period (Years)",
    min_value=5,
    value=5
)

outstanding_loan = (-monthly_payment * ((1 + interest_rate/100 / 12) ** (12 * holding_period) - 1) /
                    (interest_rate/100 / 12) + loan_eligible * (1 + interest_rate/100 / 12) ** (12 * holding_period))
cpf_return = (0 * ((1 + 0.025/12) ** (12 * holding_period) - 1) /
              (0.025 / 12) + total_grants * (1 + 0.025 / 12) ** (12 * holding_period))
cash_proceeds = selling_price - outstanding_loan - cpf_return


col3.metric(
    label="Selling Price",
    value=f"${selling_price:,.0f}")
col3.metric(
    label="Outstanding Loan",
    value=f"- ${outstanding_loan:,.0f}")
col3.metric(
    label="CPF Used & Accrued Interest",
    value=f"- ${cpf_return:,.0f}")
col3.metric(
    label="Cash Proceeds",
    value=f"= ${cash_proceeds:,.0f}")

st.divider()

st.write("#### Return on Investment")
col1, col2, col3 = st.columns(3)

legal_fee = 1400
submission_fee = 80
agent_fee = 0.02 * selling_price

total_selling_fee = legal_fee + submission_fee + agent_fee
growth = (selling_price / purchase_price) - 1
yoy_growth = (selling_price / purchase_price) ** (1/holding_period) - 1
roc = (cash_proceeds - total_selling_fee -
       total_cash_outlay) / total_cash_outlay
roc_annualized = (1+roc)**(1/holding_period)-1

col1.metric(
    label="Legal Fee",
    value=f"+ ${legal_fee:,.0f}")
col1.metric(
    label="Submission Fee",
    value=f"+ ${submission_fee:,.0f}")
col1.metric(
    label="Agent Fee",
    value=f"+ ${agent_fee:,.0f}")
col1.metric(
    label="Total Selling Fee",
    value=f"= ${total_selling_fee:,.0f}")

col2.metric(
    label="Property Growth",
    value=f"{growth*100:.2f}%")
col2.metric(
    label="Property Growth (Annualized)",
    value=f"{yoy_growth*100:.2f}%")
col2.metric(
    label="Time Horizon",
    value=f"{holding_period:.0f} Years")

col3.metric(
    label="Return on Capital",
    value=f"{roc*100:.2f}%")

col3.metric(
    label="Return on Capital (Annualized)",
    value=f"{roc_annualized*100:.2f}%")
