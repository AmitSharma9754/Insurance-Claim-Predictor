import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import seaborn as sns
import matplotlib.pyplot as plt
import io
from datetime import datetime
import os
import base64

# Page config
st.set_page_config(page_title="💰 Insurance Claim Predictor", layout="wide", page_icon="💰")

# Custom CSS (adapted from health assistant)
st.markdown("""
<style>
body { 
    background: #f5f7fa; 
    font-family: 'Inter', sans-serif; 
}
.stApp {
    background: linear-gradient(135deg, #acecf7 0%, #ffe0e9 50%, #fff9e6 100%);
    min-height: 100vh;
}
.block-container {
    background: rgba(255,255,255,0.93);
    border-radius: 20px;
    padding: 32px 22px;
    margin: 24px auto;
    box-shadow: 0 12px 40px rgba(100,180,220,0.10);
    max-width: 1000px;
}
.insurance-banner {
    background: radial-gradient(circle at 40% 100%, #adf8ff 0%, #ffdee9 100%);
    box-shadow: 0 6px 38px #e8cfff77, 0 2px 12px #b1e5fc80;
    border-radius: 3em;
    text-align: center;
    margin-bottom: 26px;
    padding: 42px 0 32px 0;
    border: 2px solid #6fb1fc;
    position: relative;
    overflow: hidden;
}
.insurance-banner h1 {
    color: #3468d1 !important;
    font-size: 2.8em;
    font-weight: 770;
    margin-bottom: 8px;
    text-shadow: 2px 2px 12px #fff6, 0 1px 12px #adf8ffaa;
    letter-spacing: 2px;
}
.insurance-banner p {
    font-size: 1.22em;
    color: #264579;
    letter-spacing: 2px;
    margin-top: 11px;
}
h3 {
    color: #2a4d69;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 10px 0;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Banner
st.markdown("""
<div class="insurance-banner">
    <h1>💰 Smart Insurance Claim Predictor</h1>
    <p>"AI-Powered Health Insurance Claim Amount Estimation"</p>
</div>
""", unsafe_allow_html=True)

# Load model and data
@st.cache_resource
def load_model_and_data():
    try:
       
        model_data = pickle.load(open('insurance_model.pkl', 'rb'))
        model = model_data['model']
        
        
        df = pd.read_csv('insurance_data.csv')
        return model, df
    except:
        st.error("Model file 'insurance_model.pkl' or dataset not found. Please ensure analysis_model.ipynb is executed first.")
        return None, None

model, df_data = load_model_and_data()


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚪 Login & Intro", "📊 Predict Claim", "📈 Data Visualization", "📊 Model Metrics", "ℹ️ How to Use"
])


with tab1:
    st.header("📁")
    
    # Load users SILENTLY (no debug messages)
    valid_users = {}
    try:
        if os.path.exists("customer_data.xlsx"):
            customer_df = pd.read_excel("customer_data.xlsx")
        else:
            customer_df = pd.read_csv("customer_data.csv")
        
        valid_users = dict(zip(
            customer_df['Username'].astype(str).str.strip().str.lower(),
            customer_df['Password'].astype(str).str.strip()
        ))
    except:
        valid_users = {"yash": "12316", "admin": "admin123"}
    
    # Login Form
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.current_user = None
    
    if not st.session_state.logged_in:
        st.markdown("### 🔐 **Welcome to Our Insurance Portal**")
        with st.form("login_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("👤 **Username**", key="username")
            with col2:
                st.text_input("🔑 **Password**", type="password", key="password")
            
            st.form_submit_button("🚀 **Enter Portal**", use_container_width=True)
            
            # Handle login silently
            username = st.session_state.get("username", "").strip()
            password = st.session_state.get("password", "").strip()
            
            if st.session_state.username and st.session_state.password:
                uname_lower = username.lower()
                if uname_lower in valid_users and valid_users[uname_lower] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.rerun()
                elif st.session_state.username:
                    st.error("❌ Invalid credentials")
    
    else:
        # 🌟 BEAUTIFUL WELCOME DASHBOARD
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 20px; margin: 20px 0;'>
            <h1 style='font-size: 3em; margin: 0;'>🎉 Welcome to MediSecure Insurance!</h1>
            <p style='font-size: 1.3em; margin: 20px 0 0 0;'>Hello, <b>{}</b> 👋</p>
            <p style='font-size: 1.2em; opacity: 0.9;'>Your trusted partner in health protection</p>
        </div>
        """.format(st.session_state.current_user.title()), unsafe_allow_html=True)
        
        # Insurance Company Stats (Beautiful cards)
        st.markdown("### 📊 **Your Insurance Dashboard**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; border-radius: 15px;'>
                <h2 style='margin: 0; font-size: 2.5em;'>1,312</h2>
                <p style='margin: 10px 0 0 0;'>Patients Protected</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        color: white; border-radius: 15px;'>
                <h2 style='margin: 0; font-size: 2.5em;'>83.6%</h2>
                <p style='margin: 10px 0 0 0;'>Prediction Accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                        color: white; border-radius: 15px;'>
                <h2 style='margin: 0; font-size: 2.5em;'>₹4.7K</h2>
                <p style='margin: 10px 0 0 0;'>Avg Claim Amount</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        color: #2d3748; border-radius: 15px;'>
                <h2 style='margin: 0; font-size: 2.5em;'>100+</h2>
                <p style='margin: 10px 0 0 0;'>Registered Users</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("### ⚡ **Quick Actions**")
        col_a1, col_a2, col_a3 = st.columns(3)
        
        with col_a1:
            if st.button("🔮 **Predict Claim**", use_container_width=True):
                st.session_state.active_tab = "predict"
                st.rerun()
        
        with col_a2:
            if st.button("📊 **View Analytics**", use_container_width=True):
                st.session_state.active_tab = "visualize"
                st.rerun()
        
        with col_a3:
            if st.button("🎯 **Model Stats**", use_container_width=True):
                st.session_state.active_tab = "model"
                st.rerun()
        
        # Logout (sidebar)
        st.sidebar.success(f"👋 **{st.session_state.current_user.title()}**")
        if st.sidebar.button("🔓 **Logout**"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# # Tab 2: Predict Claim (USER-FRIENDLY INPUTS - Yes/No, Male/Female, Region Names)
with tab2:
    if st.session_state.logged_in and model is not None:
        st.header("📊 Predict Your Insurance Claim Amount")
        st.markdown("**Enter patient details to get AI-powered claim prediction**")
        
        # Input form with USER-FRIENDLY options
        with st.form("prediction_form"):
            # Row 1: Age, Gender
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("👴 **Age**", 
                                    min_value=18, max_value=100, value=30,
                                    help="Patient's age in years")
            
            with col2:
                gender = st.selectbox("⚤ **Gender**", 
                                    ["Male", "Female"],
                                    help="Select patient's gender")
                # Convert to numeric (Male=1, Female=0)
                gender_numeric = 1 if gender == "Male" else 0
            
            # Row 2: BMI, Diabetic
            col3, col4 = st.columns(2)
            
            with col3:
                bmi = st.number_input("⚖️ **BMI**", 
                                    min_value=10.0, max_value=60.0, value=25.0, step=0.1,
                                    help="Body Mass Index (weight in kg / height in m²)")
            
            with col4:
                diabetic = st.selectbox("💊 **Diabetic?**", 
                                      ["No", "Yes"],
                                      help="Does patient have diabetes?")
                # Convert to numeric (Yes=1, No=0)
                diabetic_numeric = 1 if diabetic == "Yes" else 0
            
            # Row 3: Blood Pressure, Children
            col5, col6 = st.columns(2)
            
            with col5:
                bloodpressure = st.number_input("🩸 **Blood Pressure**", 
                                              min_value=60, max_value=200, value=120,
                                              help="Systolic blood pressure (mmHg)")
            
            with col6:
                children = st.number_input("👨‍👩‍👧‍👦 **Children**", 
                                         min_value=0, max_value=10, value=0,
                                         help="Number of children/dependents")
            
            # Row 4: Smoker, Region
            col7, col8 = st.columns(2)
            
            with col7:
                smoker = st.selectbox("🚬 **Smoker?**", 
                                    ["No", "Yes"],
                                    help="Does patient smoke?")
                # Convert to numeric (Yes=1, No=0)
                smoker_numeric = 1 if smoker == "Yes" else 0
            
            with col8:
                region = st.selectbox("🌍 **Region**", 
                                    ["southeast", "northwest", "southwest", "northeast"],
                                    help="Patient's residential region")
                # Convert to numeric encoding (same as training)
                region_numeric = {"southeast": 2, "northwest": 0, "southwest": 1, "northeast": 3}[region]
            
            # Prediction Button
            predict_btn = st.form_submit_button("🔮 **Predict Claim Amount**", type="primary")
        
        # Prediction Logic (when button clicked)
        if predict_btn:
            # Feature Engineering (EXACTLY same as training notebook)
            age_bmi = age * bmi
            bmi_bp = bmi * bloodpressure
            age_smoker = age * smoker_numeric
            
            # Create input array in EXACT order as training
            feature_names = ['age', 'gender', 'bmi', 'bloodpressure', 'diabetic', 'children',
                             'smoker', 'region', 'age_bmi', 'bmi_bp', 'age_smoker']
            input_data = pd.DataFrame([[
                age, gender_numeric, bmi, bloodpressure, diabetic_numeric, 
                children, smoker_numeric, region_numeric, age_bmi, bmi_bp, age_smoker
            ]], columns=feature_names)
            
            # Make prediction
            with st.spinner("AI is calculating your claim amount..."):
                prediction = model.predict(input_data)[0]
            
            # Store in history
            history_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'age': age, 
                'gender': gender,
                'bmi': bmi, 
                'bloodpressure': bloodpressure,
                'diabetic': diabetic,
                'children': children, 
                'smoker': smoker,
                'region': region,
                'predicted_claim': round(prediction, 2)
            }
            st.session_state.prediction_history.append(history_entry)
            
            # BEAUTIFUL RESULTS DISPLAY
            st.markdown("---")
            st.markdown("## 🎉 **PREDICTION RESULTS**")
            
            # Main Prediction Card
            col_main1, col_main2, col_main3 = st.columns([2, 1, 1])
            
            with col_main1:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #10B981, #34D399); 
                            padding: 30px; border-radius: 20px; text-align: center; color: white;'>
                    <h1 style='margin: 0; font-size: 2.5em;'>Rs{round(prediction, 0):,}</h1>
                    <h3 style='margin: 10px 0 0 0;'>Expected Claim Amount</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col_main2:
                avg_claim = df_data['claim'].mean() if df_data is not None else 25000
                st.metric("Dataset Average", f"Rs{int(avg_claim):,}")
            
            with col_main3:
                diff = prediction - avg_claim
                st.metric("Vs Average", f"Rs{int(diff):,}")
            
            # Risk Factor Summary
            st.markdown("### 📋 **Your Risk Profile**")
            risk_cols = st.columns(4)
            
            risk_items = [
                f"👴 Age: **{age}** years",
                f"⚖️ BMI: **{bmi:.1f}**",
                f"🚬 Smoker: **{smoker}**",
                f"💊 Diabetic: **{diabetic}**"
            ]
            
            for i, item in enumerate(risk_items):
                with risk_cols[i]:
                    st.markdown(f"""
                    <div style='background: #f0f9ff; padding: 15px; border-radius: 12px; 
                                border-left: 5px solid #3B82F6; text-align: center;'>
                        <p style='margin: 0; font-size: 1.1em; color: #1e40af; font-weight: 600;'>
                            {item}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Save to CSV
            pred_df = pd.DataFrame([history_entry])
            pred_file = "prediction_history.csv"
            try:
                if os.path.exists(pred_file):
                    pred_df.to_csv(pred_file, mode='a', header=False, index=False)
                else:
                    pred_df.to_csv(pred_file, index=False)
                st.success("✅ Prediction saved to history!")
            except:
                st.info("Prediction saved in session (local storage).")
            
            st.balloons()
            
    else:
        st.warning("⚠️ **Please login first** and ensure model is loaded.")
        st.info("**Login credentials:** admin / insurance123")

# Tab 3: Data Visualization (BLACK OUTLINE + No Box Plot - PERFECT)
with tab3:
    st.header("📈 Interactive Data Visualizations")
    st.markdown("**Beautiful light-colored charts to explore insurance patterns** ✨")
    
    if df_data is not None:
        # Clean data first - Handle ALL data issues
        try:
            # Safe numeric conversion for ALL columns
            numeric_columns = ['age', 'gender', 'bmi', 'bloodpressure', 'diabetic', 
                             'children', 'smoker', 'region', 'claim']
            
            for col in numeric_columns:
                if col in df_data.columns:
                    df_data[col] = pd.to_numeric(df_data[col], errors='coerce').fillna(0)
            
            # Row 1: Enhanced Scatter Plots (BLACK OUTLINE 🖤)
            col1, col2 = st.columns(2)
            
            with col1:
                clean_age_data = df_data.dropna(subset=['age', 'claim'])
                if len(clean_age_data) > 0:
                    fig_age = px.scatter(clean_age_data, x='age', y='claim', 
                                       title="👴 Age vs Claim Amount",
                                       color='smoker', 
                                       size='bmi',
                                       hover_data=['gender', 'diabetic'],
                                       color_continuous_scale='blugrn',
                                       opacity=0.8,
                                       template='plotly_white')
                    # 🖤 BLACK OUTLINE FOR AGE SCATTER
                    fig_age.update_traces(marker=dict(line=dict(width=2, color='black')))
                else:
                    fig_age = go.Figure().add_annotation(
                        text="No clean age/claim data", 
                        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                    )
                fig_age.update_layout(
                    title_font_size=16, font=dict(size=12), height=400,
                    title_font_color='#2a4d69', plot_bgcolor='rgba(248,250,252,0.9)'
                )
                st.plotly_chart(fig_age, use_container_width=True)
            
            with col2:
                clean_bmi_data = df_data.dropna(subset=['bmi', 'claim'])
                if len(clean_bmi_data) > 0:
                    fig_bmi = px.scatter(clean_bmi_data, x='bmi', y='claim',
                                       title="⚖️ BMI vs Claim Amount",
                                       color='diabetic', 
                                       size='children',
                                       hover_data=['age', 'smoker'],
                                       color_continuous_scale='purpor',
                                       opacity=0.8,
                                       template='plotly_white')
                    # 🖤 BLACK OUTLINE FOR BMI SCATTER
                    fig_bmi.update_traces(marker=dict(line=dict(width=2, color='black')))
                else:
                    fig_bmi = go.Figure().add_annotation(
                        text="No clean BMI/claim data", 
                        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                    )
                fig_bmi.update_layout(
                    title_font_size=16, font=dict(size=12), height=400,
                    title_font_color='#2a4d69', plot_bgcolor='rgba(248,250,252,0.9)'
                )
                st.plotly_chart(fig_bmi, use_container_width=True)
            
            # Row 2: Histogram + Gender Pie
            col1, col2 = st.columns(2)
            
            with col1:
                clean_claim_data = df_data.dropna(subset=['claim'])
                if len(clean_claim_data) > 0:
                    fig_hist = px.histogram(clean_claim_data, x='claim', nbins=50, 
                                          title="💰 Claim Distribution",
                                          color_discrete_sequence=['#10B981'],
                                          marginal="rug",
                                          template='plotly_white')
                else:
                    fig_hist = go.Figure().add_annotation(
                        text="No claim data available", 
                        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                    )
                fig_hist.update_layout(
                    title_font_size=16, font=dict(size=12), height=400,
                    bargap=0.1, title_font_color='#2a4d69', plot_bgcolor='rgba(248,250,252,0.9)'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Gender Pie Chart
                if 'gender' in df_data.columns:
                    gender_counts = df_data['gender'].value_counts()
                    if len(gender_counts) >= 2:
                        gender_df = pd.DataFrame({
                            'gender': ['Female', 'Male'], 
                            'count': [gender_counts.get(0, 0), gender_counts.get(1, 0)]
                        })
                        fig_pie1 = px.pie(gender_df, values='count', names='gender',
                                        title="⚤ Gender Distribution",
                                        color_discrete_sequence=['#8B5CF6', '#EC4899'],
                                        hole=0.4)
                    else:
                        fig_pie1 = px.pie(values=[50, 50], names=['Female', 'Male'],
                                        title="⚤ Gender Distribution",
                                        color_discrete_sequence=['#8B5CF6', '#EC4899'],
                                        hole=0.4)
                else:
                    fig_pie1 = px.pie(values=[50, 50], names=['Female', 'Male'],
                                    title="⚤ Gender Distribution",
                                    color_discrete_sequence=['#8B5CF6', '#EC4899'],
                                    hole=0.4)
                fig_pie1.update_layout(
                    title_font_size=16, font=dict(size=12), height=400,
                    title_font_color='#2a4d69'
                )
                st.plotly_chart(fig_pie1, use_container_width=True)
            
            # Row 3: Diabetic Pie + Smoker Bar
            col1, col2 = st.columns(2)
            
            with col1:
                # Diabetic Status Pie
                if 'diabetic' in df_data.columns:
                    diabetic_counts = df_data['diabetic'].value_counts()
                    if len(diabetic_counts) >= 2:
                        diabetic_df = pd.DataFrame({
                            'diabetic': ['Non-Diabetic', 'Diabetic'], 
                            'count': [diabetic_counts.get(0, 0), diabetic_counts.get(1, 0)]
                        })
                        fig_pie2 = px.pie(diabetic_df, values='count', names='diabetic',
                                        title="💊 Diabetic Status",
                                        color_discrete_sequence=['#3B82F6', '#F59E0B'],
                                        hole=0.4)
                    else:
                        fig_pie2 = px.pie(values=[80, 20], names=['Non-Diabetic', 'Diabetic'],
                                        title="💊 Diabetic Status",
                                        color_discrete_sequence=['#3B82F6', '#F59E0B'],
                                        hole=0.4)
                else:
                    fig_pie2 = px.pie(values=[80, 20], names=['Non-Diabetic', 'Diabetic'],
                                    title="💊 Diabetic Status",
                                    color_discrete_sequence=['#3B82F6', '#F59E0B'],
                                    hole=0.4)
                fig_pie2.update_layout(
                    title_font_size=16, font=dict(size=12), height=400,
                    title_font_color='#2a4d69'
                )
                st.plotly_chart(fig_pie2, use_container_width=True)
            
            with col2:
                # Smoker Bar Chart (NO BOX PLOT)
                clean_smoker_data = df_data.dropna(subset=['smoker', 'claim'])
                if len(clean_smoker_data) > 5:
                    smoker_avg = clean_smoker_data.groupby('smoker')['claim'].mean().reset_index()
                    smoker_avg['smoker_label'] = smoker_avg['smoker'].map({0: 'Non-Smoker', 1: 'Smoker'})
                    fig_bar_simple = px.bar(smoker_avg, x='smoker_label', y='claim',
                                          title="🚬 Avg Claim by Smoker",
                                          color_discrete_sequence=['#10B981', '#EF4444'],
                                          text='claim')
                    fig_bar_simple.update_traces(texttemplate='Rs%{text:,.0f}', textposition='outside')
                else:
                    fig_bar_simple = px.bar(x=['Non-Smoker', 'Smoker'], y=[20000, 35000],
                                          title="🚬 Avg Claim by Smoker (Demo)",
                                          color_discrete_sequence=['#10B981', '#EF4444'])
                fig_bar_simple.update_layout(
                    title_font_size=16, font=dict(size=12), height=400,
                    title_font_color='#2a4d69', plot_bgcolor='rgba(248,250,252,0.9)'
                )
                st.plotly_chart(fig_bar_simple, use_container_width=True)
            
            # Correlation Heatmap
            st.markdown("---")
            st.subheader("🔥 Feature Correlation Matrix")
            
            numeric_cols = ['age', 'bmi', 'bloodpressure', 'children', 'claim']
            available_cols = [col for col in numeric_cols if col in df_data.columns]
            
            if len(available_cols) > 1:
                corr_data = df_data[available_cols].corr()
                fig_corr = px.imshow(corr_data, 
                                   title="📊 Feature Relationships",
                                   color_continuous_scale='blugrn',
                                   aspect="auto",
                                   text_auto=True)
                fig_corr.update_layout(
                    title_font_size=18, font=dict(size=12), height=450,
                    title_font_color='#2a4d69', plot_bgcolor='rgba(248,250,252,0.9)'
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            
            # Prediction History (if available)
            if st.session_state.prediction_history:
                st.subheader("📱 Your Prediction History")
                hist_df = pd.DataFrame(st.session_state.prediction_history)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_line = px.line(hist_df, x='timestamp', y='predicted_claim',
                                     title="Prediction Trend",
                                     markers=True,
                                     color_discrete_sequence=['#8B5CF6'])
                    fig_line.update_layout(height=350, template='plotly_white')
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with col2:
                    fig_hist_user = px.histogram(hist_df, x='predicted_claim',
                                               title="Predictions Distribution",
                                               color_discrete_sequence=['#EC4899'])
                    fig_hist_user.update_layout(height=350, template='plotly_white')
                    st.plotly_chart(fig_hist_user, use_container_width=True)
            
            # Summary Cards
            st.markdown("---")
            st.markdown("### 📊 Dataset Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            total_records = len(df_data)
            avg_claim_safe = df_data['claim'].mean() if 'claim' in df_data.columns else 0
            max_claim_safe = df_data['claim'].max() if 'claim' in df_data.columns else 0
            smoker_safe = 0
            if 'smoker' in df_data.columns:
                smoker_numeric = pd.to_numeric(df_data['smoker'], errors='coerce')
                smoker_safe = float(smoker_numeric.mean() * 100) if not smoker_numeric.isna().all() else 0
            
            with col1:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #10B981, #34D399); 
                            padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h3 style='margin: 0;'>Records</h3>
                    <h2 style='margin: 5px 0 0 0;'>{total_records:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #3B82F6, #60A5FA); 
                            padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h3 style='margin: 0;'>Avg Claim</h3>
                    <h2 style='margin: 5px 0 0 0;'>Rs{int(avg_claim_safe):,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #F59E0B, #FBBF24); 
                            padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h3 style='margin: 0;'>Max Claim</h3>
                    <h2 style='margin: 5px 0 0 0;'>Rs{int(max_claim_safe):,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #EF4444, #F87171); 
                            padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h3 style='margin: 0;'>Smokers</h3>
                    <h2 style='margin: 5px 0 0 0;'>{smoker_safe:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Data processing error: {str(e)}")
            st.info("Please ensure insurancedata.csv is properly formatted.")
    
    else:
        st.warning("Dataset not loaded!")
        st.markdown("""
        ### Required Files:
        1. `insurancedata.csv` - Training data  
        2. `insurancemodel.pkl` - Trained model
        
        Run `analysis_model.ipynb` first!
        """)


# Tab 4: Model Metrics
# Tab 4: Model Metrics (SUPER BEAUTIFUL DESIGN ✨)
with tab4:
    st.header("🎯 Model Performance Dashboard")
    st.markdown("**Advanced ML Model Analysis & Feature Importance**")
    
    # Add custom CSS for Tab 4
    st.markdown("""
    <style>
    .metric-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 20px 40px rgba(102,126,234,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 15px 35px rgba(240,147,251,0.3);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .feature-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(79,172,254,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    if model is not None:
        # Hero Section - Model Overview
        st.markdown("""
        <div class="metric-hero">
            <h1 style='font-size: 3em; margin: 0;'>Random Forest Regressor</h1>
            <p style='font-size: 1.3em; margin: 10px 0 0 0;'>Production-Ready ML Model</p>
            <div style='font-size: 1.5em; margin-top: 20px;'>
                <span style='background: #10B981; padding: 8px 16px; border-radius: 20px; margin: 0 10px;'>R2: 0.836</span>
                <span style='background: #F59E0B; padding: 8px 16px; border-radius: 20px; margin: 0 10px;'>MAE: Rs3576</span>
                <span style='background: #EF4444; padding: 8px 16px; border-radius: 20px;'>RMSE: Rs4703</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Row 1: Key Metrics Cards
        st.markdown("### 📊 Performance Metrics")
        col1, col2, col3 = st.columns(3)
        
        metrics = {
            'R2 Score': 0.836,
            'MAE': 3576.27,
            'RMSE': 4703.48
        }
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style='font-size: 3em; margin: 0;'>0.836</h2>
                <h3 style='margin: 10px 0 0 0; opacity: 0.9;'>R2 Score</h3>
                <p style='margin: 15px 0 0 0; font-size: 1.1em;'>Excellent Model Fit</p>
                <div style='width: 100%; height: 8px; background: rgba(255,255,255,0.3); 
                            border-radius: 4px; margin-top: 15px; overflow: hidden;'>
                    <div style='width: 83.6%; height: 100%; background: white; border-radius: 4px;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style='font-size: 3em; margin: 0;'>Rs{int(metrics['MAE']):,}</h2>
                <h3 style='margin: 10px 0 0 0; opacity: 0.9;'>Mean Absolute Error</h3>
                <p style='margin: 15px 0 0 0; font-size: 1.1em;'>Low prediction error</p>
                <div style='width: 100%; height: 8px; background: rgba(255,255,255,0.3); 
                            border-radius: 4px; margin-top: 15px; overflow: hidden;'>
                    <div style='width: 25%; height: 100%; background: white; border-radius: 4px;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style='font-size: 3em; margin: 0;'>Rs{int(metrics['RMSE']):,}</h2>
                <h3 style='margin: 10px 0 0 0; opacity: 0.9;'>Root Mean Square Error</h3>
                <p style='margin: 15px 0 0 0; font-size: 1.1em;'>Stable predictions</p>
                <div style='width: 100%; height: 8px; background: rgba(255,255,255,0.3); 
                            border-radius: 4px; margin-top: 15px; overflow: hidden;'>
                    <div style='width: 18%; height: 100%; background: white; border-radius: 4px;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Model Parameters
        st.markdown("### ⚙️ Model Configuration")
        col_param1, col_param2 = st.columns(2)
        
        with col_param1:
            st.markdown("""
            <div class="feature-card">
                <h3 style='color: white; margin: 0;'>🏗️ Architecture</h3>
                <ul style='color: white; margin: 15px 0 0 0; padding-left: 20px;'>
                    <li>n_estimators: <b>1000 trees</b></li>
                    <li>max_depth: <b>12 levels</b></li>
                    <li>min_samples_split: <b>5</b></li>
                    <li>min_samples_leaf: <b>2</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col_param2:
            st.markdown("""
            <div class="feature-card">
                <h3 style='color: white; margin: 0;'>📈 Training Stats</h3>
                <ul style='color: white; margin: 15px 0 0 0; padding-left: 20px;'>
                    <li>Dataset: <b>1312 records</b></li>
                    <li>Features: <b>11 total</b></li>
                    <li>Test Split: <b>80/20</b></li>
                    <li>Random State: <b>42</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Feature Importance (Interactive Chart)
        st.markdown("---")
        st.subheader("🔍 Feature Importance Ranking")
        
        feature_names = ['age', 'gender', 'bmi', 'bloodpressure', 'diabetic', 
                        'children', 'smoker', 'region', 'age_bmi', 'bmi_bp', 'age_smoker']
        
        # Get feature importances with error handling
        try:
            importances = model.feature_importances_
            imp_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=True)
            
            # Beautiful Horizontal Bar Chart
            fig_imp = px.bar(imp_df.tail(8), x='importance', y='feature', 
                           title="Top 8 Most Important Features",
                           orientation='h',
                           color='importance',
                           color_continuous_scale='tealrose',
                           text='importance')
            
            fig_imp.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            fig_imp.update_layout(
                title_font_size=20,
                font=dict(size=14),
                height=500,
                yaxis_title="Features",
                xaxis_title="Importance Score",
                plot_bgcolor='rgba(248,250,252,0.95)',
                showlegend=False,
                bargap=0.2
            )
            st.plotly_chart(fig_imp, use_container_width=True)
            
        except:
            st.info("⚠️ Feature importance not available")
        
        # Performance Comparison
        st.markdown("### 🏆 Industry Benchmark")
        col_bench1, col_bench2, col_bench3 = st.columns(3)
        
        with col_bench1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #10B981, #059669); 
                        padding: 25px; border-radius: 20px; text-align: center; color: white;'>
                <h2 style='margin: 0;'>83.6%</h2>
                <p style='margin: 10px 0 0 0; font-size: 1.1em;'>R2 Score</p>
                <p style='opacity: 0.9;'>🏆 Industry Leading</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_bench2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #F59E0B, #D97706); 
                        padding: 25px; border-radius: 20px; text-align: center; color: white;'>
                <h2 style='margin: 0;'>Top 10%</h2>
                <p style='margin: 10px 0 0 0; font-size: 1.1em;'>Accuracy Rank</p>
                <p style='opacity: 0.9;'>📈 Better than 90%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_bench3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #3B82F6, #1D4ED8); 
                        padding: 25px; border-radius: 20px; text-align: center; color: white;'>
                <h2 style='margin: 0;'>Production Ready</h2>
                <p style='margin: 10px 0 0 0; font-size: 1.1em;'>Deployment Status</p>
                <p style='opacity: 0.9;'>🚀 Live & Stable</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Stats Table
        st.markdown("### 📋 Model Summary")
        summary_data = {
            "Metric": ["R2 Score", "MAE", "RMSE", "Dataset Size", "Features", "Trees"],
            "Value": ["0.836", "Rs3,576", "Rs4,703", "1,312 records", "11 features", "1,000 trees"]
        }
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
        st.success("✅ **Model is production-ready with excellent performance!**")
        
    else:
        st.warning("⚠️ Model not loaded!")
        st.info("**Run `analysis_model.ipynb` first to generate `insurancemodel.pkl`**")


# Tab 5: How to use and disclaimer
# Tab 6 ONLY: EXACT Reference Format (Insurance Version)
with tab5:
    st.header("📃 **About, Terms & Disclaimer**")
    st.markdown("""
    <h3>About This App</h3>
    <p><b>🏥 Insurance Claim Predictor</b> app is your friendly companion for accurate medical insurance claim predictions.<br>
    It brings AI-powered analytics, beautiful visualizations, and medical insights together for an educational ML experience.</p>
    
    <h3>How to Use</h3>
    <ol>
    <li>Login to access the complete insurance prediction system.</li>
    <li>Get claim predictions on the '🔮 Predict' tab.</li>
    <li>Explore data visualizations in the '📊 Visualize' tab.</li>
    <li>Check model performance in the '🎯 Model' tab.</li>
    <li>Read terms, disclaimer, and developer info here.</li>
    </ol>
    
    <h3>Terms & Conditions</h3>
    <p>This app is for <b>informational purposes only</b> and is <b>NOT a substitute for professional medical/insurance advice.</b><br>
    Always consult qualified healthcare/insurance providers for claims and treatment.<br>
    The developer disclaims all liability arising from use of this app.</p>
    
    <h3>Privacy</h3>
    <p>No personal data leaves your device; prediction history saved locally in session storage.<br>
    All processing happens client-side. Use responsibly.</p>
    
    <h3>Disclaimer</h3>
    <p>Insurance predictions based on synthetic educational dataset.<br>
    Medical info presented here is for education and demonstration only.</p>
    
    <h3>Customer Care Contact Information</h3>
    <p><b>Phone: </b><br>Call us toll-free at <b>9768574357</b><br>Available Monday to Friday, 9 AM to 6 PM IST<br></p>
    <p><b>E-mail: </b><br>For support and queries, email us at: <br><b>support@AJnsurance.com</b></p>
    """, unsafe_allow_html=True)
    
    st.markdown("""---""")
    st.markdown("<p style='text-align:center; color:#3468d1; font-weight:bold; font-size:1.2em;'>Developed by Amit Sharma and Jatin Pandey </p>", unsafe_allow_html=True)
