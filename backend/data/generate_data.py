"""Generate realistic synthetic customer profiles and transaction histories.

Run:  python data/generate_data.py
Creates: customers.json, transactions.json (15 customers, ~6 months each)
"""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
random.seed(42)

# --- Transaction merchant catalogue ---
CATEGORIES: dict[str, list[str]] = {
    "salary": ["Salary Credit", "Contract Payment"],
    "rent": ["House Rent", "PG Rent"],
    "emi": ["Home Loan EMI", "Car Loan EMI", "Personal Loan EMI"],
    "groceries": ["BigBasket", "Zepto", "Blinkit", "DMart", "Reliance Fresh"],
    "dining": ["Swiggy", "Zomato", "Dominos", "McDonalds", "Local Restaurant"],
    "transport": ["Uber", "Ola", "Metro Card", "Petrol Pump"],
    "shopping": ["Amazon", "Flipkart", "Myntra", "Reliance Digital"],
    "utilities": ["Electricity Bill", "Water Bill", "Gas Bill", "Broadband"],
    "subscriptions": ["Netflix", "Spotify", "Hotstar", "YouTube Premium"],
    "medical": ["Apollo Pharmacy", "Hospital", "Lab Tests", "Insurance Premium"],
    "education": ["School Fee", "Course Fee", "Udemy", "Books"],
    "travel": ["MakeMyTrip", "IRCTC", "IndiGo", "Hotel Booking"],
    "jewellery": ["Tanishq", "Kalyan Jewellers", "Malabar Gold"],
    "wedding": ["Venue Booking", "Catering", "Wedding Shopping", "Invitation Cards"],
    "investment": ["SBI MF SIP", "PPF Deposit", "FD Booking", "NPS Contribution"],
    "insurance": ["LIC Premium", "SBI Life Premium", "Health Insurance"],
    "upi": ["UPI P2P Transfer", "PhonePe", "Google Pay"],
    "atm": ["ATM Withdrawal", "Cash Deposit"],
    "government": ["Income Tax", "GST Payment", "Municipal Tax"],
}

CHANNELS = ["upi", "netbanking", "card", "atm", "yono"]

# --- 15 hand-authored customer profiles ---
PROFILES = [
    {
        "id": "CUST_001", "name": "Rahul Sharma", "age": 28, "location": "Bengaluru",
        "persona": "Young Professional", "income_band": "8-12 LPA", "monthly_income": 95000,
        "products_held": ["savings_account", "debit_card", "home_loan"],
        "risk_appetite": "moderate", "digital_activity": "high",
        "pattern": "salary_hike_wedding",
    },
    {
        "id": "CUST_002", "name": "Priya Menon", "age": 32, "location": "Mumbai",
        "persona": "Working Mother", "income_band": "12-18 LPA", "monthly_income": 120000,
        "products_held": ["savings_account", "debit_card", "credit_card"],
        "risk_appetite": "moderate", "digital_activity": "high",
        "pattern": "child_school_no_insurance",
    },
    {
        "id": "CUST_003", "name": "Amit Kumar", "age": 45, "location": "Delhi",
        "persona": "Mid-Career Manager", "income_band": "18-30 LPA", "monthly_income": 200000,
        "products_held": ["savings_account", "credit_card", "home_loan", "fixed_deposit"],
        "risk_appetite": "moderate", "digital_activity": "medium",
        "pattern": "kids_college_retirement",
    },
    {
        "id": "CUST_004", "name": "Sneha Reddy", "age": 24, "location": "Hyderabad",
        "persona": "Fresh Graduate", "income_band": "4-6 LPA", "monthly_income": 45000,
        "products_held": ["savings_account", "debit_card"],
        "risk_appetite": "aggressive", "digital_activity": "high",
        "pattern": "first_job_no_planning",
    },
    {
        "id": "CUST_005", "name": "Vikram Patel", "age": 58, "location": "Ahmedabad",
        "persona": "Pre-Retirement", "income_band": "30-50 LPA", "monthly_income": 350000,
        "products_held": ["savings_account", "fixed_deposit", "mutual_fund", "credit_card"],
        "risk_appetite": "conservative", "digital_activity": "medium",
        "pattern": "retiring_soon_pension",
    },
    {
        "id": "CUST_006", "name": "Ananya Das", "age": 30, "location": "Kolkata",
        "persona": "Freelancer", "income_band": "8-12 LPA", "monthly_income": 75000,
        "products_held": ["savings_account", "debit_card"],
        "risk_appetite": "moderate", "digital_activity": "high",
        "pattern": "irregular_income_no_savings",
    },
    {
        "id": "CUST_007", "name": "Rajesh Iyer", "age": 35, "location": "Chennai",
        "persona": "Small Business Owner", "income_band": "18-30 LPA", "monthly_income": 150000,
        "products_held": ["savings_account", "current_account", "credit_card", "business_loan"],
        "risk_appetite": "aggressive", "digital_activity": "high",
        "pattern": "business_expansion_credit",
    },
    {
        "id": "CUST_008", "name": "Kavita Singh", "age": 42, "location": "Lucknow",
        "persona": "Government Employee", "income_band": "8-12 LPA", "monthly_income": 80000,
        "products_held": ["savings_account", "ppf", "fixed_deposit"],
        "risk_appetite": "conservative", "digital_activity": "low",
        "pattern": "stable_underutilizes_digital",
    },
    {
        "id": "CUST_009", "name": "Deepak Nair", "age": 27, "location": "Kochi",
        "persona": "IT Professional", "income_band": "12-18 LPA", "monthly_income": 110000,
        "products_held": ["savings_account", "debit_card", "credit_card"],
        "risk_appetite": "aggressive", "digital_activity": "high",
        "pattern": "high_digital_no_tax_planning",
    },
    {
        "id": "CUST_010", "name": "Meera Joshi", "age": 55, "location": "Pune",
        "persona": "Senior Professional", "income_band": "30-50 LPA", "monthly_income": 400000,
        "products_held": ["savings_account", "fixed_deposit", "mutual_fund", "credit_card", "ppf"],
        "risk_appetite": "moderate", "digital_activity": "medium",
        "pattern": "daughter_wedding_estate",
    },
    {
        "id": "CUST_011", "name": "Arjun Malhotra", "age": 22, "location": "Jaipur",
        "persona": "College Student", "income_band": "0-2 LPA", "monthly_income": 15000,
        "products_held": ["savings_account"],
        "risk_appetite": "moderate", "digital_activity": "high",
        "pattern": "first_account_basic",
    },
    {
        "id": "CUST_012", "name": "Fatima Sheikh", "age": 38, "location": "Bhopal",
        "persona": "Homemaker", "income_band": "0-2 LPA", "monthly_income": 0,
        "products_held": ["savings_account", "fixed_deposit"],
        "risk_appetite": "conservative", "digital_activity": "low",
        "pattern": "family_finances_gold",
    },
    {
        "id": "CUST_013", "name": "Suresh Yadav", "age": 50, "location": "Patna",
        "persona": "Farmer/Rural", "income_band": "2-4 LPA", "monthly_income": 30000,
        "products_held": ["savings_account"],
        "risk_appetite": "conservative", "digital_activity": "low",
        "pattern": "pm_schemes_low_digital",
    },
    {
        "id": "CUST_014", "name": "Nisha Agarwal", "age": 34, "location": "Noida",
        "persona": "HR Manager", "income_band": "12-18 LPA", "monthly_income": 140000,
        "products_held": ["savings_account", "credit_card", "debit_card"],
        "risk_appetite": "moderate", "digital_activity": "high",
        "pattern": "relocated_new_baby",
    },
    {
        "id": "CUST_015", "name": "Karthik Raman", "age": 40, "location": "Coimbatore",
        "persona": "Doctor", "income_band": "50+ LPA", "monthly_income": 500000,
        "products_held": ["savings_account", "credit_card", "car_loan"],
        "risk_appetite": "moderate", "digital_activity": "medium",
        "pattern": "high_income_poor_planning",
    },
]

ALL_PRODUCTS = [
    "savings_account", "debit_card", "credit_card", "fixed_deposit", "mutual_fund",
    "term_insurance", "health_insurance", "ppf", "home_loan", "car_loan",
    "personal_loan", "nps", "current_account", "business_loan",
]


def month_starts(months: int = 6) -> list[date]:
    """Return the first day of each of the last `months` months (oldest first)."""
    today = date(2026, 6, 1)
    starts = []
    y, m = today.year, today.month
    for _ in range(months):
        starts.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(starts))


def add_txn(txns, cid, d, ttype, amount, desc, category, balance):
    txns.append({
        "id": f"TXN_{len(txns) + 1:06d}",
        "customer_id": cid,
        "date": d.isoformat(),
        "type": ttype,
        "amount": round(amount, 2),
        "description": desc,
        "category": category,
        "channel": random.choice(CHANNELS),
        "balance_after": round(balance, 2),
    })


def pattern_spend(profile, month_idx, total_months):
    """Return extra pattern-specific transactions for a given month index."""
    extra = []
    p = profile["pattern"]
    last = total_months - 1
    if p == "salary_hike_wedding" and month_idx >= last - 1:
        extra += [("Tanishq", "jewellery", random.randint(45000, 90000)),
                  ("Venue Booking", "wedding", random.randint(60000, 120000)),
                  ("Wedding Shopping", "wedding", random.randint(20000, 40000))]
    elif p == "child_school_no_insurance" and month_idx >= last - 2:
        extra += [("School Fee", "education", random.randint(35000, 55000)),
                  ("Books", "education", random.randint(3000, 6000))]
    elif p == "kids_college_retirement" and month_idx % 2 == 0:
        extra += [("Course Fee", "education", random.randint(40000, 70000))]
    elif p == "daughter_wedding_estate" and month_idx >= last - 1:
        extra += [("Kalyan Jewellers", "jewellery", random.randint(150000, 300000)),
                  ("Catering", "wedding", random.randint(100000, 200000))]
    elif p == "relocated_new_baby" and month_idx >= last - 2:
        extra += [("Hospital", "medical", random.randint(30000, 80000)),
                  ("Reliance Digital", "shopping", random.randint(25000, 60000))]
    elif p == "business_expansion_credit":
        extra += [("GST Payment", "government", random.randint(20000, 50000))]
    elif p == "pm_schemes_low_digital" and month_idx % 3 == 0:
        extra += [("ATM Withdrawal", "atm", random.randint(5000, 12000))]
    return extra


def generate():
    customers = []
    transactions = []
    starts = month_starts(6)
    total_months = len(starts)

    for profile in PROFILES:
        cid = profile["id"]
        income = profile["monthly_income"]
        # opening balance proportional to income
        balance = max(15000, income * random.uniform(0.8, 2.5))

        monthly_spend_total = 0
        for mi, mstart in enumerate(starts):
            # salary credit (with a hike for the salary_hike pattern in the last 2 months)
            credit = income
            if profile["pattern"] == "salary_hike_wedding" and mi >= total_months - 2:
                credit = round(income)  # already hiked value
            elif profile["pattern"] == "salary_hike_wedding":
                credit = round(income * 0.79)  # pre-hike (75k vs 95k)
            if profile["pattern"] == "irregular_income_no_savings":
                credit = round(income * random.uniform(0.4, 1.6))

            if credit > 0:
                balance += credit
                add_txn(transactions, cid, mstart.replace(day=1), "credit", credit,
                        "Salary Credit" if income > 0 else "Contract Payment", "salary", balance)

            # recurring spends scaled to income
            base = max(8000, income * 0.55) if income > 0 else random.randint(15000, 30000)
            recurring = [
                ("rent", base * 0.30, 5),
                ("groceries", base * 0.15, 8),
                ("dining", base * 0.10, 12),
                ("transport", base * 0.08, 10),
                ("utilities", base * 0.07, 4),
                ("shopping", base * 0.12, 6),
                ("subscriptions", base * 0.02, 3),
            ]
            if "home_loan" in profile["products_held"]:
                recurring.append(("emi", income * 0.13, 7))
            if "car_loan" in profile["products_held"]:
                recurring.append(("emi", income * 0.08, 9))
            if "mutual_fund" in profile["products_held"]:
                recurring.append(("investment", income * 0.05, 5))
            if "ppf" in profile["products_held"]:
                recurring.append(("investment", income * 0.04, 5))

            month_spend = 0
            for category, amt, day in recurring:
                n_txns = random.randint(1, 4) if category in ("groceries", "dining", "transport") else 1
                for _ in range(n_txns):
                    a = (amt / n_txns) * random.uniform(0.8, 1.2)
                    if a <= 0:
                        continue
                    if balance - a < 5000:
                        continue  # skip if it would overdraw
                    balance -= a
                    month_spend += a
                    d = mstart + timedelta(days=min(27, day + random.randint(-2, 4)))
                    add_txn(transactions, cid, d, "debit", a,
                            random.choice(CATEGORIES[category]), category, balance)

            # pattern-specific large spends
            for desc, category, amt in pattern_spend(profile, mi, total_months):
                if balance - amt < 5000:
                    continue  # skip if it would overdraw
                balance -= amt
                month_spend += amt
                d = mstart + timedelta(days=random.randint(8, 25))
                add_txn(transactions, cid, d, "debit", amt, desc, category, balance)

            monthly_spend_total = month_spend

        # build derived profile fields from the last month
        savings_rate = round(max(0, (income - monthly_spend_total) / income * 100), 1) if income > 0 else 0.0
        products_not_held = [p for p in ALL_PRODUCTS if p not in profile["products_held"]]

        customer = {
            **{k: profile[k] for k in (
                "id", "name", "age", "location", "persona", "income_band",
                "monthly_income", "products_held", "risk_appetite", "digital_activity")},
            "customer_id": cid,
            "monthly_spending": round(monthly_spend_total),
            "savings_rate": savings_rate,
            "products_not_held": products_not_held,
            "current_balance": round(balance),
            # contact details for real nudge delivery (placeholders — replace
            # with a real test number/email to see live WhatsApp/SMS/email sends)
            "phone": f"+9198{random.randint(10000000, 99999999)}",
            "email": f"{profile['name'].split()[0].lower()}.{cid[-3:]}@example.com",
            "whatsapp_opt_in": random.random() < 0.7,
            "preferred_language": "en",
        }
        customers.append(customer)

    (DATA_DIR / "customers.json").write_text(json.dumps(customers, indent=2), encoding="utf-8")
    (DATA_DIR / "transactions.json").write_text(json.dumps(transactions, indent=2), encoding="utf-8")

    print(f"Generated {len(customers)} customers")
    print(f"Generated {len(transactions)} transactions")
    print(f"Files written to {DATA_DIR}")


if __name__ == "__main__":
    generate()
