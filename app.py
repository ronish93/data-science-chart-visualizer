import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Data Science Chart Studio", layout="wide")
# --- PREMIUM CUSTOM CSS INJECTION ---
st.markdown("""
    <style>
        /* 1. Change core website background and main font stack */
        .stApp {
            background-color: #F8F9FA;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* 2. Upgrade the Main Header styling with a smooth dark gradient background */
        h1 {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            padding-bottom: 10px;
        }
        
        /* 3. Make sidebar/configuration panel look like a sleek modern card floating layout */
        [data-testid="stVerticalBlock"] > div:has(div.stSelectbox) {
            background-color: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            border: 1px solid #E5E7EB !important;
        }

        /* 4. Style select boxes and dropdown parameter input forms neatly */
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 8px !important;
            border-color: #D1D5DB !important;
        }
        
        /* 5. Custom card background box for your chart visualization frame wrapper */
        .plotly-graph-div {
            background-color: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Ultimate Data Science Chart Visualizer")
st.write("Upload your dataset to unlock full exploratory data science insights instantly.")

# --- DEFENSIVE DATA LOADING ---
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"📁 Successfully loaded uploaded dataset: {df.shape[0]} rows and {df.shape[1]} columns.")
    except Exception as e:
        st.error("❌ **File Error:** The uploaded file could not be read. Please ensure it is a valid CSV.")
        st.stop()
else:
    # Fallback Sample Data
    st.info("💡 Loading built-in sample customer data for preview:")
    df = pd.DataFrame({
        "CustomerID": [f"ID-{i}" for i in range(1, 101)],
        "TenureMonths": [1, 24, 12, 60, 2, 36, 5, 48, 3, 18] * 10,
        "MonthlyCharges": [29.99, 79.99, 59.99, 99.99, 35.00, 110.00, 45.00, 115.00, 30.00, 85.00] * 10,
        "SeniorCitizen": [0, 0, 0, 1, 0, 1, 0, 0, 1, 0] * 10,
        "ChurnStatus": ["Yes", "No", "No", "No", "Yes", "No", "Yes", "No", "Yes", "No"] * 10
    })

# --- DATA CLEANING & TRANSLATION FOR SENIOR CITIZENS ---
# If the dataset contains SeniorCitizen with 0 and 1, translate it for better UX
if "SeniorCitizen" in df.columns:
    df["SeniorCitizen"] = df["SeniorCitizen"].replace({0: "Non-Senior", 1: "Senior Citizen"})

# --- USER CONTROL INTERFACE ---
col1, col2 = st.columns(2) 

with col1:
    st.subheader("⚙️ Configure Your Chart")
    all_columns = df.columns.tolist()
    
    x_axis = st.selectbox("Select X-Axis Variable", all_columns, index=min(1, len(all_columns)-1))
    y_axis = st.selectbox("Select Y-Axis Variable (Optional Breakdowns)", ["None"] + all_columns, index=0)
    
    chart_type = st.selectbox("Select Data Science Plot Type", [
        "Histogram (Distribution)", 
        "Box Plot (Outlier Detection)", 
        "Scatter Plot (Relationships)", 
        "Correlation Heatmap"
    ])

# --- DYNAMIC CHART GENERATION ---
with col2:
    st.subheader(f"📈 Mode Active: {chart_type}")
    y_val = None if y_axis == "None" else y_axis
    fig = None
    explanation_text = ""

    try:
        if chart_type == "Histogram (Distribution)":
            # If the column has few unique choices, treat it as a crisp categorical plot
            if df[x_axis].nunique() <= 5:
                # If a Y-axis option is chosen, break down categories by that variable using color segments
                if y_val:
                    # Multi-variable stacked bar count
                    df_counts = df.groupby([x_axis, y_val]).size().reset_index(name='Count')
                    df_counts['Percentage'] = (df_counts['Count'] / df_counts['Count'].sum() * 100).round(1)
                    df_counts[x_axis] = df_counts[x_axis].astype(str)
                    
                    fig = px.bar(df_counts, x=x_axis, y='Count', color=y_val, text='Count',
                                 barmode='group', title=f"Distribution of {x_axis} Segmented by {y_val}")
                    fig.update_traces(textposition='inside')
                    explanation_text = f"This chart plots the categorical count totals for **{x_axis}**, grouped separately by **{y_val}** segment splits."
                else:
                    # Single-variable categorical bar count
                    df_counts = df[x_axis].value_counts().reset_index()
                    df_counts.columns = [x_axis, 'Count']
                    df_counts['Percentage'] = (df_counts['Count'] / df_counts['Count'].sum() * 100).round(1)
                    df_counts[x_axis] = df_counts[x_axis].astype(str)
                    
                    fig = px.bar(df_counts, x=x_axis, y='Count', text='Count',
                                 title=f"Distribution Split Analysis: {x_axis}")
                    fig.update_traces(texttemplate='Count: %{text}<br>%{customdata}%', textposition='inside', customdata=df_counts['Percentage'])
                    explanation_text = f"This **Bar Plot** tracks distinct categories in **{x_axis}**, presenting direct total calculation metrics."
            else:
                # Continuous numerical values histogram distribution layout
                fig = px.histogram(df, x=x_axis, color=y_val, marginal="box", title=f"Distribution Profile: {x_axis}")
                explanation_text = f"This **Histogram** maps out the visual value spreads and counts across continuous scales of **{x_axis}**."
                
        elif chart_type == "Box Plot (Outlier Detection)":
            if y_val and not pd.api.types.is_numeric_dtype(df[y_val]) and not pd.api.types.is_numeric_dtype(df[x_axis]):
                st.warning(f"⚠️ **Variable Suggestion:** Box Plots work best when tracking a categorical string against a numerical calculation metric.")
            fig = px.box(df, x=x_axis, y=y_val, color=x_axis, title=f"Outlier Spread Evaluation")
            explanation_text = "The center blocks plot your middle data densities. Extended isolated dots indicate calculated mathematical **outliers**."
            
        elif chart_type == "Scatter Plot (Relationships)":
            if y_axis == "None":
                st.warning("⚠️ **Variable Suggestion:** Please pick a column for your Y-Axis to map coordinate fields.")
            elif not pd.api.types.is_numeric_dtype(df[x_axis]) or (y_val and not pd.api.types.is_numeric_dtype(df[y_val])):
                st.warning(f"⚠️ **Variable Suggestion:** Scatter plots display clean continuous insights when both axes map numbers.")
                fig = px.scatter(df, x=x_axis, y=y_val, title=f"Categorical Coordinate Mappings")
            else:
                fig = px.scatter(df, x=x_axis, y=y_val, trendline="ols", title=f"Trend Correlation Analysis")
            explanation_text = "Every plotted point reflects a single dataset observation row details."
            
        elif chart_type == "Correlation Heatmap":
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                fig = px.imshow(numeric_df.corr(), text_auto=".2f", color_continuous_scale="RdBu_r", title="Global Feature Correlation Matrix")
                explanation_text = "A calculation map tracking patterns between values. Bright red grid segments suggest strong parallel trends."
            else:
                st.error("❌ No numeric fields found in this dataset to build a correlation matrix.")

        # --- SAFE RENDERING LAYOUT ---
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            if explanation_text:
                st.info(f"💡 **Data Analyst Insight:** {explanation_text}")
                
    except Exception as chart_error:
        st.error("❌ **Configuration Error:** The combination of variables chosen could not be calculated into this specific chart type. Please switch fields.")
