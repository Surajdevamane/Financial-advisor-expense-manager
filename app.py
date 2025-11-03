import streamlit as st
from PIL import Image
import pytesseract
import re
import io
import pandas as pd

# ---------- CATEGORY KEYWORDS ----------
CATEGORY_KEYWORDS = {
    "Food": ["zomato", "swiggy", "food", "restaurant", "hotel", "cafe", "coffee", "meal", "eatery"],
    "Transport": ["uber", "ola", "taxi", "bus", "train", "fuel", "petrol", "diesel", "auto", "metro"],
    "Shopping": ["amazon", "flipkart", "ajio", "myntra", "mall", "store", "shop", "fashion", "cloth", "purchase"],
    "Entertainment": ["movie", "netflix", "spotify", "pvr", "inox", "ticket", "show", "game", "entertainment"],
    "Groceries": ["grocery", "supermarket", "dmart", "mart", "bazaar"],
    "Health": ["pharmacy", "medical", "medicine", "hospital", "clinic", "doctor"],
    "Bills": ["electricity", "bill", "wifi", "broadband", "recharge", "upi", "paytm", "google pay", "phonepe"],
    "Others": []
}

# ---------- CATEGORY ADVICE DATABASE ----------
CATEGORY_ADVICE = {
    "Food": [
        "🍽️ Keep food spending under 15% of your total income.",
        "🍱 Plan weekly meals to avoid overspending on takeout.",
        "☕ Make coffee at home — small savings add up!"
    ],
    "Transport": [
        "🚗 Track your fuel usage and plan trips efficiently.",
        "🚌 Try carpooling or public transport to save fuel costs.",
        "🚴 Short distances? Consider walking or biking!"
    ],
    "Shopping": [
        "🛍️ Avoid impulse buys — wait 24 hours before purchasing.",
        "💳 Compare prices before checking out online.",
        "📦 Track your monthly shopping budget and set limits."
    ],
    "Entertainment": [
        "🎬 Limit subscriptions to only the services you use often.",
        "🎮 Budget for entertainment — 5–10% of income max.",
        "🎧 Free hobbies can be just as rewarding!"
    ],
    "Health": [
        "💊 Keep 10% of your income aside for medical expenses.",
        "🏥 Health is wealth — insurance saves in emergencies.",
        "🧘‍♂️ Invest in preventive care, not just medicine."
    ],
    "Groceries": [
        "🛒 Make a weekly grocery list and stick to it.",
        "🥦 Buy in bulk for non-perishables to save money.",
        "🍎 Compare prices across stores for essentials."
    ],
    "Bills": [
        # "💡 Automate payments to avoid late fees.",
        "📶 Check subscriptions and cancel unused plans.",
        "📲 Review recurring payments every month."
    ],
    "Others": [
        "📘 Track unknown expenses manually to avoid leaks.",
        "💰 Every rupee counts — even small savings matter."
    ]
}

# ---------- Helper: Find category ----------
def detect_category(text_line):
    text_line = text_line.lower()
    best_category = "Others"
    best_score = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for k in keywords if k in text_line)
        if score > best_score:
            best_score = score
            best_category = category
    return best_category

# ---------- Helper: Parse each line ----------
def parse_expenses(text):
    expenses = []
    lines = text.splitlines()
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        # find amount
        matches = re.findall(r'([0-9]+(?:\.[0-9]{1,2})?)', clean)
        if not matches:
            continue
        amount = float(matches[-1])
        category = detect_category(clean)
        # remove digits to keep only item name
        name = re.sub(r'[^a-zA-Z ]', '', clean).strip().title()
        expenses.append({
            "Item": name if name else "Unknown",
            "Amount (₹)": amount,
            "Category": category
        })
    return expenses

# ---------- Helper: Generate financial advice ----------
def generate_financial_advice(df):
    if df.empty:
        return "No expenses detected to analyze."

    total = df["Amount (₹)"].sum()
    advice_list = []

    # Check each category spending
    cat_totals = df.groupby("Category")["Amount (₹)"].sum().to_dict()
    for cat, amount in cat_totals.items():
        if cat in CATEGORY_ADVICE:
            sample_advice = CATEGORY_ADVICE[cat][0]
            if amount > 1000:  # simple threshold
                sample_advice = CATEGORY_ADVICE[cat][1]
            advice_list.append(f"**{cat}:** {sample_advice}")

    # Overall budget advice
    advice_list.append(f"💵 Your total spending this session is ₹{total:.2f}.")
    if total > 5000:
        advice_list.append("⚠️ You’re spending quite a bit! Try the 50–30–20 rule: 50% needs, 30% wants, 20% savings.")
    else:
        advice_list.append("✅ You’re doing great — keep tracking expenses regularly!")

    return "\n\n".join(advice_list)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Expense + Financial Advisor", page_icon="💰", layout="centered")
st.title("💰 Smart Expense Categorizer + Financial Advisor")

uploaded = st.file_uploader("📸 Upload your receipt or expense list image", type=["png", "jpg", "jpeg","pdf"])

if uploaded:
    image = Image.open(io.BytesIO(uploaded.getvalue()))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("🔍 Analyze & Extract All Expenses"):
        st.write("⏳ Processing image with OCR...")
        text = pytesseract.image_to_string(image)
        st.subheader("🧾 Extracted Text")
        st.text_area("OCR Output", value=text, height=200)

        parsed = parse_expenses(text)

        if not parsed:
            st.warning("No valid expenses found. Try uploading a clearer image.")
        else:
            df = pd.DataFrame(parsed)
            st.subheader("📊 Categorized Expenses")
            st.dataframe(df, use_container_width=True)

            total = df["Amount (₹)"].sum()
            by_cat = df.groupby("Category")["Amount (₹)"].sum().reset_index()

            st.markdown(f"### 💰 Total Expense: ₹{total:.2f}")
            st.bar_chart(by_cat.set_index("Category"))

            # --- New Advice Section ---
            st.subheader("🧠 Personalized Financial Advice")
            advice = generate_financial_advice(df)
            st.markdown(advice)

            # Optional: Download results
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Expense Report (CSV)", data=csv, file_name="expense_report.csv", mime="text/csv")
