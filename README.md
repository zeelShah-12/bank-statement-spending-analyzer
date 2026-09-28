# Bank Statement Spending Analyzer

Bank statements list every transaction but tell you nothing about where your money
actually goes — categorizing hundreds of lines by hand is a chore nobody does.
**Bank Statement Spending Analyzer** automates it:

![Demo: upload a statement, AI categorizes it, charts + transaction table](demo.gif)

- Upload a bank statement PDF (HDFC, SBI, Axis, ICICI, and similar Indian bank formats).
- AI reads every transaction and categorizes it — Food & Dining, Shopping, Transport,
  Subscriptions, Utilities, Rent, EMI/Loan, UPI Transfer, Salary/Income, Cash Withdrawal,
  Investment, Other.
- Spending breakdown by category (bar chart) and over time (line chart).
- Full transaction table with category filtering.
- Export to Excel (transactions + category summary) or CSV.

**Who pays:** Individual consumers (₹99–299/month) and fintech apps that want to embed
this as a feature.

## Stack

- **Streamlit** — single-file UI
- **pdfplumber** — extracts text from statement PDFs (text-based exports, not scans)
- **Groq** (`openai/gpt-oss-120b`) — transaction extraction + categorization, no
  vision needed since this is a text-based PDF
- **Altair** — category and trend charts, using a CVD-safe fixed categorical palette
- **Pandas + openpyxl** — transaction table + Excel export

## Local setup

```bash
cd "10 project"
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY (free at console.groq.com)
streamlit run app.py
```

Runs on `http://localhost:8501`.

## Project structure

```
10 project/
├── app.py               Streamlit UI — upload, overview charts, transactions, export
├── pdf_extract.py         Extracts raw text from the statement PDF via pdfplumber
├── categorize.py          Groq call + prompt/schema for transaction extraction
├── sample_statements/     (drop demo statement PDFs here for testing)
├── requirements.txt
└── .env.example
```

## Notes for the portfolio writeup

- Only works with **text-based** PDF exports, not scanned/photographed statements —
  most Indian banks' netbanking portals export text-based PDFs by default, so this
  covers the common case without needing OCR.
- Statement text is truncated to ~18k characters before being sent to the model, to
  keep cost and latency bounded on very long statements — the UI surfaces a warning
  when truncation happens so numbers aren't silently wrong.
- Category bar chart uses a fixed, CVD-validated 8-color categorical palette (see the
  `dataviz` design system) rather than a default color cycle, and skips a legend in
  favor of direct axis labels since each bar is already named.
