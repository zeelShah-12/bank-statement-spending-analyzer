"""Regenerates mock_statement.pdf — a synthetic bank statement (fictional bank,
fictional people) used to test the analyzer without needing a real statement.
Requires: pip install fpdf2
"""
from fpdf import FPDF

transactions = [
    ("01-06-2026", "UPI-SWIGGY-order4471", "612.00", "Dr"),
    ("02-06-2026", "SALARY CREDIT-ACME SOFTWARE PVT LTD", "68000.00", "Cr"),
    ("03-06-2026", "NEFT-RENT-LANDLORD RAMESH GUPTA", "18000.00", "Dr"),
    ("04-06-2026", "UPI-ZOMATO ORDER", "455.00", "Dr"),
    ("05-06-2026", "NETFLIX.COM SUBSCRIPTION", "649.00", "Dr"),
    ("06-06-2026", "UPI-OLA CABS", "220.00", "Dr"),
    ("07-06-2026", "AMAZON.IN PURCHASE", "2399.00", "Dr"),
    ("09-06-2026", "ELECTRICITY BILL PAYMENT-BSES", "1840.00", "Dr"),
    ("10-06-2026", "EMI-HDFC PERSONAL LOAN", "5200.00", "Dr"),
    ("12-06-2026", "UPI-BIGBASKET GROCERY", "1780.00", "Dr"),
    ("14-06-2026", "SPOTIFY PREMIUM", "119.00", "Dr"),
    ("15-06-2026", "ATM CASH WITHDRAWAL", "5000.00", "Dr"),
    ("18-06-2026", "UPI-UBER TRIP", "310.00", "Dr"),
    ("20-06-2026", "MYNTRA FASHION PURCHASE", "1599.00", "Dr"),
    ("22-06-2026", "UPI-P2P TRANSFER TO RAHUL", "2000.00", "Dr"),
    ("25-06-2026", "MUTUAL FUND SIP-ICICI PRU", "5000.00", "Dr"),
    ("28-06-2026", "UPI-SWIGGY ORDER", "389.00", "Dr"),
    ("01-07-2026", "SALARY CREDIT-ACME SOFTWARE PVT LTD", "68000.00", "Cr"),
    ("03-07-2026", "NEFT-RENT-LANDLORD RAMESH GUPTA", "18000.00", "Dr"),
    ("06-07-2026", "UPI-ZOMATO ORDER", "512.00", "Dr"),
    ("08-07-2026", "AMAZON.IN PURCHASE", "3299.00", "Dr"),
    ("10-07-2026", "EMI-HDFC PERSONAL LOAN", "5200.00", "Dr"),
    ("15-07-2026", "MOBILE RECHARGE-JIO", "599.00", "Dr"),
    ("18-07-2026", "UPI-OLA CABS", "180.00", "Dr"),
]

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 8, "PARAMOUNT NATIONAL BANK", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, "Savings Account Statement", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Account Holder: Ankit Sharma   |   Account No: XXXXXXXX4521", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Statement Period: 01 Jun 2026 - 18 Jul 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

pdf.set_font("Helvetica", "B", 9)
col_widths = [25, 105, 30, 20]
headers = ["Date", "Narration", "Amount (INR)", "Type"]
for w, h in zip(col_widths, headers):
    pdf.cell(w, 7, h, border=1)
pdf.ln()

pdf.set_font("Helvetica", "", 8)
for date, narration, amount, txn_type in transactions:
    pdf.cell(col_widths[0], 6, date, border=1)
    pdf.cell(col_widths[1], 6, narration, border=1)
    pdf.cell(col_widths[2], 6, amount, border=1, align="R")
    pdf.cell(col_widths[3], 6, txn_type, border=1, align="C")
    pdf.ln()

pdf.output("mock_statement.pdf")
print("done")
