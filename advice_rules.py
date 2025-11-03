ADVICE = {
    "Dining": lambda amt: f"You spent ₹{amt:.0f} on dining. Tip: try a weekly dining cap; set aside 5% of monthly income for eating out.",
    "Transport": lambda amt: f"Transport ₹{amt:.0f}. Tip: consider monthly passes or carpooling to reduce costs.",
    "Groceries": lambda amt: f"Groceries ₹{amt:.0f}. Tip: compare unit prices and buy staples in bulk.",
    "Entertainment": lambda amt: f"Entertainment ₹{amt:.0f}. Tip: choose 1 paid subscription and cancel others you rarely use.",
    "Others": lambda amt: f"Expense ₹{amt:.0f}. Tip: log this expense category and review weekly."
}
