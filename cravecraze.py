import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard",
    page_icon="🌸",
    layout="wide"
)

# --- Title and Header ---
st.title("🌸 Interactive Media Intelligence Dashboard")
st.write("Upload your CSV file to visualize and analyze media performance.")

# --- Data Cleaning Function ---
@st.cache_data
def clean_data(df):
    """
    Cleans and preprocesses the uploaded DataFrame.
    - Normalizes column names
    - Converts 'Date' to datetime
    - Fills missing 'Engagements' with 0
    """
    # Normalize column names
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # --- Column Validation ---
    required_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Error: The following required columns are missing from your CSV file: {', '.join(missing_columns)}")
        return None

    # --- Data Type Conversion and Cleaning ---
    try:
        df['date'] = pd.to_datetime(df['date'])
        df['engagements'] = pd.to_numeric(df['engagements']).fillna(0)
    except Exception as e:
        st.error(f"Error processing data: {e}. Please check the format of your 'Date' and 'Engagements' columns.")
        return None
        
    return df

# --- Insight Generation Functions ---
def get_sentiment_insights(df):
    if df.empty:
        return []
    sentiment_counts = df['sentiment'].value_counts()
    sorted_sentiments = sentiment_counts.sort_values(ascending=False)
    total_posts = len(df)
    insights = []
    if not sorted_sentiments.empty:
        dominant = sorted_sentiments.index[0]
        dominant_pct = (sorted_sentiments.iloc[0] / total_posts) * 100
        insights.append(f"**Dominant Sentiment:** The audience reception is largely **{dominant}**, accounting for {dominant_pct:.1f}% of all posts.")
    if len(sorted_sentiments) > 2:
        minority = sorted_sentiments.index[-1]
        insights.append(f"**Data Anomaly:** The **{minority}** sentiment is a significant minority, suggesting a need to investigate specific posts driving this feeling.")
    insights.append("**Strategic Trend:** The current sentiment mix indicates the overall tone of the content. Efforts should focus on increasing positive interactions.")
    return insights

def get_engagement_trend_insights(df):
    if df.empty or len(df) < 2:
        return []
    engagement_by_date = df.groupby('date')['engagements'].sum()
    if engagement_by_date.empty:
        return []
    peak_date = engagement_by_date.idxmax()
    average_engagement = engagement_by_date.mean()
    insights = [
        f"**Peak Engagement:** The highest engagement was on **{peak_date.strftime('%B %d, %Y')}**, suggesting a highly successful post or event that should be analyzed.",
        f"**Emerging Trend:** The engagement trend shows a general **{'upward' if engagement_by_date.iloc[-1] > engagement_by_date.iloc[0] else 'stable or declining'}** trajectory.",
        f"**Performance Context:** The average engagement per day is **{average_engagement:,.0f}**, serving as a baseline for future content."
    ]
    return insights

def get_platform_insights(df):
    if df.empty:
        return []
    platform_engagements = df.groupby('platform')['engagements'].sum().sort_values(ascending=False)
    total_engagements = platform_engagements.sum()
    insights = []
    if not platform_engagements.empty:
        top_platform = platform_engagements.index[0]
        top_pct = (platform_engagements.iloc[0] / total_engagements) * 100
        insights.append(f"**Key Finding:** **{top_platform}** is the primary engagement driver, accounting for **{top_pct:.1f}%** of the total.")
    if len(platform_engagements) > 1:
        insights.append("**Performance Gap:** There is a clear performance difference between platforms, highlighting where resources are most effective.")
    insights.append("**Strategic Implication:** Content and ad spend should be prioritized towards the most engaging platforms.")
    return insights
    
def get_media_type_insights(df):
    if df.empty:
        return []
    media_type_counts = df['media_type'].value_counts().sort_values(ascending=False)
    insights = []
    if not media_type_counts.empty:
        insights.append(f"**Dominant Format:** The content strategy is heavily reliant on **{media_type_counts.index[0]}**.")
    if len(media_type_counts) > 1:
        insights.append(f"**Untapped Potential:** The least used format, **{media_type_counts.index[-1]}**, could be an area for growth and audience diversification.")
    insights.append("**Content Mix:** The visual balance suggests the diversity of the content portfolio. A balanced mix is key to reaching different audience segments.")
    return insights

def get_location_insights(df):
    if df.empty or 'location' not in df.columns or df['location'].isnull().all():
        return []
    location_engagements = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5)
    insights = []
    if not location_engagements.empty:
        insights.append(f"**Primary Market:** Engagement is heavily concentrated in **{location_engagements.index[0]}**.")
    if len(location_engagements) > 1:
        insights.append("**Audience Concentration:** A noticeable drop-off in engagement after the top location indicates a hyper-concentrated audience.")
    insights.append("**Geo-Targeting Opportunity:** The top locations are clear candidates for geo-targeted campaigns and localized content.")
    return insights


# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    cleaned_df = clean_data(df.copy())

    if cleaned_df is not None:
        st.success("CSV file uploaded and processed successfully!")

        # --- Sidebar Filters ---
        st.sidebar.header("Filter Data")

        min_date = cleaned_df['date'].min().date()
        max_date = cleaned_df['date'].max().date()
        
        start_date = st.sidebar.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("End date", max_date, min_value=min_date, max_value=max_date)

        if start_date > end_date:
            st.sidebar.error("Error: End date must be after start date.")
            st.stop()
            
        platform_options = ['All'] + sorted(cleaned_df['platform'].unique().tolist())
        selected_platform = st.sidebar.selectbox("Platform", platform_options)
        
        sentiment_options = ['All'] + sorted(cleaned_df['sentiment'].unique().tolist())
        selected_sentiment = st.sidebar.selectbox("Sentiment", sentiment_options)

        media_type_options = ['All'] + sorted(cleaned_df['media_type'].unique().tolist())
        selected_media_type = st.sidebar.selectbox("Media Type", media_type_options)

        # --- Filtering Logic ---
        filtered_df = cleaned_df[
            (cleaned_df['date'].dt.date >= start_date) &
            (cleaned_df['date'].dt.date <= end_date)
        ]
        if selected_platform != 'All':
            filtered_df = filtered_df[filtered_df['platform'] == selected_platform]
        if selected_sentiment != 'All':
            filtered_df = filtered_df[filtered_df['sentiment'] == selected_sentiment]
        if selected_media_type != 'All':
            filtered_df = filtered_df[filtered_df['media_type'] == selected_media_type]

        if filtered_df.empty:
            st.warning("No data available for the selected filters. Please adjust your filter settings.")
        else:
            # --- Dashboard Layout ---
            st.header("Visualizations & Insights")
            
            col1, col2 = st.columns(2)

            # --- Chart 1: Sentiment Breakdown ---
            with col1:
                st.subheader("Sentiment Breakdown")
                sentiment_counts = filtered_df['sentiment'].value_counts()
                fig_sentiment = px.pie(
                    values=sentiment_counts.values, 
                    names=sentiment_counts.index, 
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Greys_r
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
                st.markdown("#### Key Insights")
                for insight in get_sentiment_insights(filtered_df):
                    st.markdown(f"- {insight}")

            # --- Chart 2: Engagement Trend ---
            with col2:
                st.subheader("Engagement Trend Over Time")
                engagement_by_date = filtered_df.groupby('date')['engagements'].sum().reset_index()
                fig_trend = px.line(
                    engagement_by_date, 
                    x='date', 
                    y='engagements',
                    markers=True
                )
                fig_trend.update_traces(line=dict(color='#2d3748'))
                st.plotly_chart(fig_trend, use_container_width=True)
                st.markdown("#### Key Insights")
                for insight in get_engagement_trend_insights(filtered_df):
                    st.markdown(f"- {insight}")

            # --- Chart 3: Platform Engagements ---
            with col1:
                st.subheader("Engagements by Platform")
                platform_engagements = filtered_df.groupby('platform')['engagements'].sum().reset_index().sort_values(by='engagements', ascending=False)
                fig_platform = px.bar(
                    platform_engagements,
                    x='platform',
                    y='engagements',
                    color_discrete_sequence=['#4a5568']
                )
                st.plotly_chart(fig_platform, use_container_width=True)
                st.markdown("#### Key Insights")
                for insight in get_platform_insights(filtered_df):
                    st.markdown(f"- {insight}")
            
            # --- Chart 4: Media Type Mix ---
            with col2:
                st.subheader("Media Type Mix")
                media_type_counts = filtered_df['media_type'].value_counts()
                fig_media = px.pie(
                    values=media_type_counts.values,
                    names=media_type_counts.index,
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Greys_r
                )
                st.plotly_chart(fig_media, use_container_width=True)
                st.markdown("#### Key Insights")
                for insight in get_media_type_insights(filtered_df):
                    st.markdown(f"- {insight}")

            # --- Chart 5: Top Locations ---
            st.subheader("Top 5 Locations by Engagement")
            location_engagements = filtered_df.groupby('location')['engagements'].sum().nlargest(5).reset_index()
            if not location_engagements.empty:
                fig_location = px.bar(
                    location_engagements,
                    x='location',
                    y='engagements',
                    color_discrete_sequence=['#718096']
                )
                st.plotly_chart(fig_location, use_container_width=True)
                st.markdown("#### Key Insights")
                for insight in get_location_insights(filtered_df):
                    st.markdown(f"- {insight}")
            else:
                st.info("Not enough location data to display this chart.")

else:
    st.info("Awaiting CSV file upload.")

