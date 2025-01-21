import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set page config
st.set_page_config(page_title="Sales Analysis Dashboard", layout="wide")

# Title
st.title("📊 Sales Analysis Dashboard")

# Load the data
@st.cache_data
def load_data():
    try:
        # Define file paths relative to the Downloads directory
        base_dir = os.path.expanduser("~/Downloads")
        files = {
            'Palero': os.path.join(base_dir, 'extracted_report_Palero/sales_analysis_Palero_20250121_092409.csv'),
            'Rotonda': os.path.join(base_dir, 'extracted_report_Rotonda/sales_analysis_Rotonda_20250121_092234.csv'),
            'Centro': os.path.join(base_dir, 'extracted_report_Centro/sales_analysis_Centro_20250121_092059.csv')
        }
        
        # Read and combine all files
        dfs = []
        for location, file_path in files.items():
            if not os.path.exists(file_path):
                st.error(f"File not found: {file_path}")
                continue
            df = pd.read_csv(file_path)
            df['Location'] = location
            dfs.append(df)
        
        if not dfs:
            return None
            
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Remove 'Cantidad' from analysis
        if 'Cantidad' in combined_df.columns:
            combined_df = combined_df.drop('Cantidad', axis=1)
            
        return combined_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    # Sidebar for global filters
    st.sidebar.title("Global Filters")
    selected_locations = st.sidebar.multiselect(
        "Select Locations",
        options=df['Location'].unique(),
        default=df['Location'].unique()
    )
    
    # Filter data based on selected locations
    df_filtered = df[df['Location'].isin(selected_locations)]
    
    # Display basic info with metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns
    
    if len(numeric_cols) > 0:
        with col1:
            total_sales = df_filtered[numeric_cols[0]].sum()
            st.metric("Total Sales", f"${total_sales:,.2f}")
        with col2:
            avg_sales = df_filtered[numeric_cols[0]].mean()
            st.metric("Average Sales", f"${avg_sales:,.2f}")
        with col3:
            locations_count = len(selected_locations)
            st.metric("Locations Analyzed", locations_count)
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["📊 Sales Analysis", "🔍 Detailed Comparison"])
    
    with tab1:
        st.subheader("Sales Distribution by Location")
        
        # Sales distribution
        if len(numeric_cols) > 0:
            # Bar chart for sales performance
            agg_data = df_filtered.groupby('Location')[numeric_cols[0]].agg(['sum', 'mean']).reset_index()
            fig_bar = go.Figure(data=[
                go.Bar(name='Total Sales', x=agg_data['Location'], y=agg_data['sum'], marker_color='lightblue'),
                go.Bar(name='Average Sale', x=agg_data['Location'], y=agg_data['mean'], marker_color='darkblue')
            ])
            fig_bar.update_layout(
                title="Sales Performance by Location",
                barmode='group',
                xaxis_title="Location",
                yaxis_title="Amount ($)",
                template="plotly_dark"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.subheader("Location Performance Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(numeric_cols) > 0:
                # Summary statistics
                summary_stats = df_filtered.groupby('Location')[numeric_cols[0]].agg([
                    'mean', 'median', 'std', 'min', 'max', 'count'
                ]).round(2)
                
                # Format the summary statistics
                summary_stats.columns = ['Average', 'Median', 'Std Dev', 'Min', 'Max', 'Count']
                st.write("📊 Summary Statistics by Location")
                st.dataframe(summary_stats, use_container_width=True)
        
        with col2:
            # Pie chart of total sales by location
            sales_by_location = df_filtered.groupby('Location')[numeric_cols[0]].sum()
            fig_pie = px.pie(values=sales_by_location.values,
                           names=sales_by_location.index,
                           title="Sales Distribution by Location")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Get categorical columns for filtering
    categorical_cols = df_filtered.select_dtypes(include=['object']).columns.tolist()
    categorical_cols.remove('Location')
    
    # Advanced Filtering Section
    st.subheader("🔍 Advanced Data Explorer")
    col1, col2 = st.columns(2)
    
    with col1:
        if len(categorical_cols) > 0:
            filter_col = st.selectbox("Filter by:", categorical_cols)
            selected_values = st.multiselect(
                "Select values:",
                options=df_filtered[filter_col].unique()
            )
    
    # Apply filters
    if len(categorical_cols) > 0 and selected_values:
        df_filtered = df_filtered[df_filtered[filter_col].isin(selected_values)]
    
    # Show filtered data with improved formatting
    if len(df_filtered) > 0:
        st.write("📋 Filtered Data:")
        st.dataframe(
            df_filtered.style.format({
                col: "${:,.2f}" for col in numeric_cols
            }),
            use_container_width=True
        )

else:
    st.error("❌ Failed to load the data files. Please check if all files exist and are accessible.") 