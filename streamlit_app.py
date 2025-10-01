import streamlit as st
import pandas as pd
import duckdb

# contributions_url = "2025_Contributions.csv"
# expenditures_url = "2025_Expenditures.csv"
# intermediaries_url = ""
# public_funds_payments = ""
# financial_analysts = ""

# st.write("Contributions")
# contributions = pd.read_csv(contributions_url)
# st.dataframe(contributions)

# st.write("Expenditures")
# expenditures = pd.read_csv(expenditures_url)
# st.dataframe(expenditures)


st.set_page_config(page_title="NYC Campaign Finance")

con = duckdb.connect()
contributions_url = "2025_Contributions.csv"

con.execute(f"""
    CREATE OR REPLACE TABLE contrib AS 
    SELECT * FROM read_csv_auto('{contributions_url}', header=True)
""")


# st.dataframe(con.execute("select * from contrib").df())

st.title("Top Contributions by Recipient")

# ---- Controls ----
top_n = st.slider("How many top recipients to show?", min_value=5, max_value=50, value=10, step=5)

# ---- Query top recipients ----
query_recipients = f"""
    SELECT RECIPNAME, SUM(AMNT) AS total_amt
    FROM contrib
    GROUP BY RECIPNAME
    ORDER BY total_amt DESC
    LIMIT {top_n}
"""
by_recipient = con.execute(query_recipients).df()
# by_recipient = by_recipient.iloc[::-1]
st.subheader("Top recipients by total amount")
st.bar_chart(by_recipient.set_index("RECIPNAME")["total_amt"], sort="-total_amt")

# Optional table for detail
with st.expander("See data table"):
    st.dataframe(by_recipient.style.format({'total_amt': "{:,.2f}"}), use_container_width=True)

# ---- Drilldown: top contributors within a selected recipient ----
st.subheader("Drill down: top contributors within a recipient")
recipient_choice = st.selectbox("Choose a recipient", options=by_recipient["RECIPNAME"].tolist())

query_contributors = f"""
    SELECT NAME, SUM(AMNT) AS total_amt
    FROM contrib
    WHERE RECIPNAME = ?
    GROUP BY NAME
    ORDER BY total_amt DESC
    LIMIT 10
"""
by_contributor = con.execute(query_contributors, [recipient_choice]).df()

st.subheader(f"Top contributors to {recipient_choice}")
st.bar_chart(by_contributor.set_index("NAME")["total_amt"], sort="-total_amt")
# Optional table for detail
with st.expander("See data table"):
    st.dataframe(by_contributor.style.format({'total_amt': "{:,.2f}"}), use_container_width=True)
