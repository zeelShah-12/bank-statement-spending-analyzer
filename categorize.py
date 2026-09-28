import json
import os

from groq import Groq

# Text-only model — no vision needed for statement categorization.
MODEL_NAME = "openai/gpt-oss-120b"

CATEGORIES = [
    "Food & Dining",
    "Shopping",
    "Transport",
    "Subscriptions",
    "Utilities & Bills",
    "Rent",
    "EMI/Loan",
    "UPI Transfer",
    "Salary/Income",
    "Cash Withdrawal",
    "Investment",
    "Other",
]

MAX_CHARS = 18000  # keep well within context window and cost bounds

PROMPT_TEMPLATE = """You are a financial assistant that categorizes Indian bank statement
transactions (HDFC, SBI, Axis, ICICI, and similar formats all use slightly different table
layouts — infer the columns from context).

Below is raw text extracted from a bank statement PDF. Extract every transaction you can find.

For each transaction report:
- date: in YYYY-MM-DD format (infer the year from the statement period if only day/month shown)
- description: the transaction narration, cleaned up but keep merchant/UPI names
- amount: a positive number (absolute value)
- type: "debit" (money out) or "credit" (money in)
- category: exactly one of {categories}

Also report:
- account_holder: name on the statement if visible, else null
- statement_period: e.g. "01 Jun 2026 - 30 Jun 2026" if visible, else null

Respond with ONLY valid JSON, no markdown fences:
{{
  "account_holder": str | null,
  "statement_period": str | null,
  "transactions": [
    {{"date": str, "description": str, "amount": number, "type": "debit" | "credit", "category": str}}
  ]
}}

STATEMENT TEXT:
---
{statement_text}
---
"""


def _get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Groq(api_key=api_key)


def categorize_statement(statement_text: str) -> dict:
    client = _get_client()

    truncated = statement_text[:MAX_CHARS]
    prompt = PROMPT_TEMPLATE.format(
        categories=", ".join(CATEGORIES),
        statement_text=truncated,
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    result = json.loads(response.choices[0].message.content)
    result["_truncated"] = len(statement_text) > MAX_CHARS
    return result
