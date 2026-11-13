import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="Titanic Dashboard", page_icon="🚢", layout="wide")

st.title("🚢 Titanic Survival Dashboard")
st.write("Explore the Titanic passenger dataset.")

def get_data(query):
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "titanic_db"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "")
    )
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()

try:
    data = get_data("""
        SELECT p.passenger_id, p.name, p.sex, p.age,
               s.pclass, s.survived, t.fare, t.embarked
        FROM titanic_project.passengers p
        JOIN titanic_project.survival_details s
        ON p.passenger_id = s.passenger_id
        JOIN titanic_project.travel_details t
        ON p.passenger_id = t.passenger_id
    """)

    total = len(data)
    survivors = int(data["survived"].sum())
    avg_age = round(data["age"].mean(), 2)
    survival_rate = round(survivors / total * 100, 2)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Passengers", total)
    c2.metric("Survivors", survivors)
    c3.metric("Average Age", avg_age)
    c4.metric("Survival Rate", f"{survival_rate}%")

    st.subheader("Survival by Gender")
    gender_data = data.groupby("sex")["survived"].sum()
    st.bar_chart(gender_data)

    st.subheader("Survival Percentage by Passenger Class")
    class_survival = data.groupby("pclass").agg(
        total_passengers=("survived", "count"),
        survivors=("survived", "sum")
        )
    
    class_survival["survival_percentage"] = (
        class_survival["survivors"] /
        class_survival["total_passengers"] * 100
        ).round(2)
    
    st.bar_chart(class_survival["survival_percentage"])
    
    st.dataframe(class_survival, use_container_width=True)

    st.subheader("Survival by Age Group")
    
    data["age_group"] = pd.cut(
        data["age"],
        bins=[0, 12, 19, 39, 59, 100],
        labels=["Child", "Teen", "Adult", "Middle Age", "Senior"]
        )
    
    age_survival = data.groupby(
        "age_group", observed=False
        )["survived"].mean() * 100
    
    st.bar_chart(age_survival)

    st.subheader("Passenger Survival Distribution")
    
    survival_data = data["survived"].value_counts()
    
    survival_data.index = survival_data.index.map({
        0: "Did Not Survive",
        1: "Survived"
        
        })
    
    st.write("Survival distribution:")
    
    st.bar_chart(survival_data)

    st.subheader("Average Fare by Passenger Class")
    
    fare_data = data.groupby("pclass")["fare"].mean().round(2)
    
    st.bar_chart(fare_data)
    
    st.write("Average fare for each class:")
    
    st.dataframe(fare_data.reset_index(), use_container_width=True)

    st.subheader("Search Passenger by Name")
    
    search_name = st.text_input("Enter passenger name")
    
    if search_name:
        search_results = data[
            data["name"].str.contains(
                search_name,
                case=False,
                na=False
                )
                ]
        
        st.dataframe(search_results, use_container_width=True)
        
        st.write("Passengers found:", len(search_results))

        st.subheader("Survival Percentage by Gender")
        
        gender_survival = data.groupby("sex")["survived"].mean() * 100
        
        gender_survival = gender_survival.round(2)
        
        st.bar_chart(gender_survival)
        
        st.dataframe(
            
            gender_survival.reset_index(),
            use_container_width=True
            )


        st.subheader("Survival Statistics Summary")
        
        survived_count = int(data["survived"].sum())
        
        not_survived_count = len(data) - survived_count
        
        col1, col2 = st.columns(2)
        col1.metric(
            "Passengers Survived",
            survived_count
            )
        
        col2.metric(
            "Passengers Did Not Survive",
            not_survived_count
            )
        
        st.subheader("Passenger Details")
    
    gender = st.selectbox("Select Gender", ["All", "female", "male"])

    passenger_class = st.selectbox(
        "Select Passenger Class",
        ["All", 1, 2, 3]
        )

    filtered = data.copy()
    
    if gender != "All":
        
        filtered = filtered[filtered["sex"] == gender]
        
        if passenger_class != "All":
            
            filtered = filtered[
                filtered["pclass"] == passenger_class
                ]

    st.dataframe(filtered, use_container_width=True)
    st.subheader("Download Passenger Data")
    
    csv = filtered.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="titanic_filtered_data.csv",
        mime="text/csv"
        )

    st.download_button(
        "Download Passenger Data",
        data=filtered.to_csv(index=False),
        file_name="titanic_data.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))


st.divider()

st.header("📌 Project Conclusion")

st.write("""
### Key Findings

1. A total of 891 passengers were included in the analysis.
2. 342 passengers survived and 549 did not survive.
3. Female passengers had a higher survival rate than male passengers.
4. First-class passengers had a higher survival rate than third-class passengers.
5. Missing values were found in Age, Cabin and Embarked columns.

### Technologies Used

- PostgreSQL
- Python
- Pandas
- Psycopg2
- Streamlit

### Project Objective

To analyze Titanic passenger data using SQL and Python
and present meaningful insights through an interactive dashboard.
""")