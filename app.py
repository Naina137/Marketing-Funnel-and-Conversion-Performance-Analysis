import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Marketing Funnel & Conversion Analysis",
    page_icon="",
    layout="wide"
)

st.title("Marketing Funnel & Conversion Performance Analysis")
st.write(
    "An interactive dashboard for analyzing marketing campaigns, "
    "customer responses, conversion performance and campaign effectiveness."
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

possible_paths = [
    Path("bank+marketing/bank/bank-full.csv"),
    Path("bank/bank-full.csv"),
    Path("bank-full.csv")
]

data_file = None

for path in possible_paths:
    if path.exists():
        data_file = path
        break

if data_file is None:
    st.error(
        "bank-full.csv was not found. Please check that the dataset "
        "is inside the project folder."
    )
    st.stop()

try:
    df = pd.read_csv(data_file, sep=";")
except Exception:
    df = pd.read_csv(data_file)

df.columns = df.columns.str.strip().str.lower()

# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------

df = df.drop_duplicates()

for column in df.select_dtypes(include="object").columns:
    df[column] = df[column].astype(str).str.strip().str.lower()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

filtered_df = df.copy()

if "job" in df.columns:
    jobs = sorted(df["job"].unique())
    selected_jobs = st.sidebar.multiselect(
        "Job",
        jobs,
        default=jobs
    )

    if selected_jobs:
        filtered_df = filtered_df[
            filtered_df["job"].isin(selected_jobs)
        ]

if "education" in df.columns:
    education = sorted(df["education"].unique())
    selected_education = st.sidebar.multiselect(
        "Education",
        education,
        default=education
    )

    if selected_education:
        filtered_df = filtered_df[
            filtered_df["education"].isin(selected_education)
        ]

if "contact" in df.columns:
    contacts = sorted(df["contact"].unique())
    selected_contacts = st.sidebar.multiselect(
        "Contact Channel",
        contacts,
        default=contacts
    )

    if selected_contacts:
        filtered_df = filtered_df[
            filtered_df["contact"].isin(selected_contacts)
        ]

if "y" in df.columns:
    outcomes = sorted(df["y"].unique())
    selected_outcomes = st.sidebar.multiselect(
        "Campaign Outcome",
        outcomes,
        default=outcomes
    )

    if selected_outcomes:
        filtered_df = filtered_df[
            filtered_df["y"].isin(selected_outcomes)
        ]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_customers = len(filtered_df)

converted = 0

if "y" in filtered_df.columns:
    converted = (filtered_df["y"] == "yes").sum()

conversion_rate = (
    converted / total_customers * 100
    if total_customers > 0
    else 0
)

if "contact" in filtered_df.columns:
    contacted = (
        filtered_df["contact"] != "unknown"
    ).sum()
else:
    contacted = 0

contact_rate = (
    contacted / total_customers * 100
    if total_customers > 0
    else 0
)

# --------------------------------------------------
# KPI DASHBOARD
# --------------------------------------------------

st.header("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Leads",
    f"{total_customers:,}"
)

col2.metric(
    "Converted Customers",
    f"{converted:,}"
)

col3.metric(
    "Conversion Rate",
    f"{conversion_rate:.2f}%"
)

col4.metric(
    "Contact Rate",
    f"{contact_rate:.2f}%"
)

# --------------------------------------------------
# MARKETING FUNNEL
# --------------------------------------------------

st.header("Marketing Funnel")

funnel_values = [
    total_customers,
    contacted,
    converted
]

funnel_labels = [
    "Total Leads",
    "Contacted Leads",
    "Converted Customers"
]

funnel_df = pd.DataFrame({
    "Stage": funnel_labels,
    "Customers": funnel_values
})

fig_funnel = px.funnel(
    funnel_df,
    y="Stage",
    x="Customers",
    title="Lead-to-Customer Conversion Funnel"
)

st.plotly_chart(
    fig_funnel,
    use_container_width=True
)

# --------------------------------------------------
# CONVERSION ANALYSIS
# --------------------------------------------------

st.header("Conversion Analysis")

col1, col2 = st.columns(2)

with col1:

    if "y" in filtered_df.columns:

        outcome_data = (
            filtered_df["y"]
            .value_counts()
            .reset_index()
        )

        outcome_data.columns = [
            "Outcome",
            "Customers"
        ]

        fig = px.bar(
            outcome_data,
            x="Outcome",
            y="Customers",
            title="Converted vs Non-Converted Customers",
            text="Customers"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    if "contact" in filtered_df.columns:

        contact_data = (
            filtered_df.groupby("contact")["y"]
            .apply(
                lambda x: (x == "yes").mean() * 100
            )
            .reset_index()
        )

        contact_data.columns = [
            "Contact Channel",
            "Conversion Rate"
        ]

        fig = px.bar(
            contact_data,
            x="Contact Channel",
            y="Conversion Rate",
            title="Conversion Rate by Contact Channel",
            text="Conversion Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# CAMPAIGN ANALYSIS
# --------------------------------------------------

st.header("Campaign Performance")

col1, col2 = st.columns(2)

with col1:

    if "campaign" in filtered_df.columns:

        campaign_data = (
            filtered_df.groupby("campaign")
            .size()
            .reset_index(name="Customers")
        )

        campaign_data = campaign_data[
            campaign_data["campaign"] <= 20
        ]

        fig = px.bar(
            campaign_data,
            x="campaign",
            y="Customers",
            title="Customers by Number of Campaign Contacts"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    if "campaign" in filtered_df.columns:

        campaign_conversion = (
            filtered_df.groupby("campaign")["y"]
            .apply(
                lambda x: (x == "yes").mean() * 100
            )
            .reset_index()
        )

        campaign_conversion.columns = [
            "Campaign Contacts",
            "Conversion Rate"
        ]

        campaign_conversion = campaign_conversion[
            campaign_conversion["Campaign Contacts"] <= 20
        ]

        fig = px.line(
            campaign_conversion,
            x="Campaign Contacts",
            y="Conversion Rate",
            markers=True,
            title="Conversion Rate by Campaign Contacts"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------

st.header("Customer Segment Analysis")

col1, col2 = st.columns(2)

with col1:

    if "job" in filtered_df.columns:

        job_data = (
            filtered_df.groupby("job")["y"]
            .apply(
                lambda x: (x == "yes").mean() * 100
            )
            .reset_index()
        )

        job_data.columns = [
            "Job",
            "Conversion Rate"
        ]

        job_data = job_data.sort_values(
            "Conversion Rate",
            ascending=False
        )

        fig = px.bar(
            job_data,
            x="Conversion Rate",
            y="Job",
            orientation="h",
            title="Conversion Rate by Job"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    if "education" in filtered_df.columns:

        education_data = (
            filtered_df.groupby("education")["y"]
            .apply(
                lambda x: (x == "yes").mean() * 100
            )
            .reset_index()
        )

        education_data.columns = [
            "Education",
            "Conversion Rate"
        ]

        fig = px.bar(
            education_data,
            x="Education",
            y="Conversion Rate",
            title="Conversion Rate by Education"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# PREVIOUS CAMPAIGN ANALYSIS
# --------------------------------------------------

st.header("Previous Campaign Performance")

if "poutcome" in filtered_df.columns:

    previous_data = (
        filtered_df.groupby("poutcome")["y"]
        .apply(
            lambda x: (x == "yes").mean() * 100
        )
        .reset_index()
    )

    previous_data.columns = [
        "Previous Campaign Outcome",
        "Conversion Rate"
    ]

    fig = px.bar(
        previous_data,
        x="Previous Campaign Outcome",
        y="Conversion Rate",
        title="Conversion Rate by Previous Campaign Outcome",
        text="Conversion Rate"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# AGE ANALYSIS
# --------------------------------------------------

if "age" in filtered_df.columns:

    st.header("Age Distribution")

    fig = px.histogram(
        filtered_df,
        x="age",
        color="y",
        nbins=30,
        title="Customer Age Distribution by Campaign Outcome"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.header("Key Business Insights")

if "contact" in filtered_df.columns:

    best_channel = (
        filtered_df.groupby("contact")["y"]
        .apply(
            lambda x: (x == "yes").mean() * 100
        )
        .sort_values(ascending=False)
    )

    if len(best_channel) > 0:

        st.write(
            f"1. The {best_channel.index[0]} channel shows the "
            f"highest observed conversion rate of "
            f"{best_channel.iloc[0]:.2f}%."
        )

if "job" in filtered_df.columns:

    best_job = (
        filtered_df.groupby("job")["y"]
        .apply(
            lambda x: (x == "yes").mean() * 100
        )
        .sort_values(ascending=False)
    )

    if len(best_job) > 0:

        st.write(
            f"2. The {best_job.index[0]} segment demonstrates "
            f"strong conversion performance."
        )

if "poutcome" in filtered_df.columns:

    best_previous = (
        filtered_df.groupby("poutcome")["y"]
        .apply(
            lambda x: (x == "yes").mean() * 100
        )
        .sort_values(ascending=False)
    )

    if len(best_previous) > 0:

        st.write(
            f"3. Previous campaign outcomes can be used to "
            f"identify customers with stronger conversion potential."
        )

st.write(
    f"4. The current filtered customer population has an overall "
    f"conversion rate of {conversion_rate:.2f}%."
)

# --------------------------------------------------
# RECOMMENDATIONS
# --------------------------------------------------

st.header("Actionable Recommendations")

recommendations = [
    "Prioritize marketing channels with stronger conversion performance.",
    "Use customer segmentation to create targeted marketing campaigns.",
    "Use previous campaign outcomes to identify high-potential customers.",
    "Avoid excessive campaign contacts when repeated communication does not improve conversion.",
    "Monitor funnel drop-offs to identify where potential customers are being lost.",
    "Use campaign performance metrics to improve future marketing strategies.",
    "Personalize customer communication based on customer characteristics."
]

for i, recommendation in enumerate(recommendations, 1):
    st.write(f"{i}. {recommendation}")

# --------------------------------------------------
# DATA EXPLORER
# --------------------------------------------------

st.header("Data Explorer")

with st.expander("View Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Analyzed Data",
    csv,
    "marketing_funnel_analysis.csv",
    "text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.write(
    "Marketing Funnel & Conversion Performance Analysis | "
    "Data Science & Analytics Project"
)