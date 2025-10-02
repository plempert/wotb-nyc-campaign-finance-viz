import streamlit as st
import pandas as pd
import duckdb

##############
# SELECTIONS #
##############

year = st.selectbox(
    "Select year",
    ("2025", "2023", "2017"),
)

offices = {
    "1": "Mayor",
    "2": "Public Advocate",
    "3": "Comptroller",
    "4": "Borough President",
    "5": "City Council",
    "IS": "PACs, LLCs, and other Independent Spenders"
}

office = st.selectbox(
    "Select office",
    list(offices.keys()),
    format_func=lambda x: offices[x]
)

st.set_page_config(page_title="NYC Campaign Finance")

###################
# CONNECT TO FILE #
###################

con = duckdb.connect()
contributions_url = f"{year}_Contributions.csv"

con.execute(f"""
    CREATE OR REPLACE TABLE contrib AS 
    SELECT * FROM read_csv_auto('{contributions_url}', header=True)
""")


###################################
# TOP CONTRIBUTIONS BY RECIPIENT #
###################################

st.title("Top Contributions by Recipient")

# ---- Controls ----
top_n = st.slider("How many top recipients to show?", min_value=5, max_value=20, value=5, step=5)

# ---- Query top recipients ----
query_recipients = f"""
    SELECT RECIPNAME, SUM(AMNT) AS total_amt
    FROM contrib
    WHERE OFFICECD = '{office}'
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


