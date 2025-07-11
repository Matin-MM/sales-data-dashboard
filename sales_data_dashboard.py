import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configure page
st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide", page_icon="📊")

# Set seed for reproducibility
np.random.seed(42)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_sales_data(n=5000):
    """Generate synthetic sales dataset"""
    start = datetime(2024, 1, 1)
    categories = ['Electronics','Clothing','Home','Beauty','Sports']
    regions = ['North','South','East','West']
    records = []
    
    for i in range(n):
        sale_id = i + 1
        category = np.random.choice(categories, p=[0.25,0.2,0.25,0.15,0.15])
        region = np.random.choice(regions)
        date = start + timedelta(days=np.random.randint(0, 180))
        price = np.random.uniform(5, 500)
        quantity = np.random.randint(1, 10)
        discount = np.random.uniform(0, 0.3)
        revenue = price * quantity * (1 - discount)
        returned = int(np.random.rand() < 0.05)
        
        records.append({
            'sale_id': sale_id,
            'category': category,
            'region': region,
            'date': date,
            'price': price,
            'quantity': quantity,
            'discount': discount,
            'revenue': revenue,
            'returned': returned
        })
    
    df = pd.DataFrame(records)
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['return_status'] = df['returned'].map({0: 'Not Returned', 1: 'Returned'})
    return df

def apply_filters(df):
    """Apply sidebar filters to the dataframe"""
    st.sidebar.header("🔧 Filter Options")
    
    # Category filter
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("📦 Select Category:", categories)
    
    # Region filter
    regions = ['All'] + sorted(df['region'].unique().tolist())
    selected_region = st.sidebar.selectbox("🌍 Select Region:", regions)
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    # Fix date_input to handle single date selection
    try:
        date_range = st.sidebar.date_input(
            "📅 Select Date Range:",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        # Ensure date_range is always a tuple/list with 2 elements
        if isinstance(date_range, (list, tuple)) and len(date_range) == 1:
            date_range = [date_range[0], date_range[0]]
        elif not isinstance(date_range, (list, tuple)):
            date_range = [date_range, date_range]
    except:
        date_range = [min_date, max_date]
    
    # Price range filter
    min_price, max_price = st.sidebar.slider(
        "💰 Price Range ($):",
        min_value=float(df['price'].min()),
        max_value=float(df['price'].max()),
        value=(float(df['price'].min()), float(df['price'].max())),
        step=10.0
    )
    
    # Return status filter
    return_options = ['All', 'Returned', 'Not Returned']
    selected_return = st.sidebar.selectbox("📋 Return Status:", return_options)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    # Fix date range filtering
    if len(date_range) >= 2:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) & 
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    elif len(date_range) == 1:
        filtered_df = filtered_df[filtered_df['date'].dt.date == date_range[0]]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= min_price) & 
        (filtered_df['price'] <= max_price)
    ]
    
    if selected_return != 'All':
        filtered_df = filtered_df[filtered_df['return_status'] == selected_return]
    
    return filtered_df

def calculate_kpis(df):
    """Calculate key performance indicators"""
    if len(df) == 0:
        return {
            'total_sales': 0,
            'total_revenue': 0,
            'avg_order_value': 0,
            'return_rate': 0,
            'avg_discount': 0,
            'total_quantity': 0
        }
    
    total_sales = len(df)
    total_revenue = df['revenue'].sum()
    avg_order_value = df['revenue'].mean()
    return_rate = (df['returned'].sum() / len(df)) * 100
    avg_discount = df['discount'].mean() * 100
    total_quantity = df['quantity'].sum()
    
    return {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'return_rate': return_rate,
        'avg_discount': avg_discount,
        'total_quantity': total_quantity
    }

def display_kpis(kpis):
    """Display KPIs in a nice layout"""
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    with col1:
        st.metric("🛒 Total Sales", f"{kpis['total_sales']:,}")
    
    with col2:
        st.metric("💰 Total Revenue", f"${kpis['total_revenue']:,.2f}")
    
    with col3:
        st.metric("📊 Avg Order Value", f"${kpis['avg_order_value']:.2f}")
    
    with col4:
        st.metric("📦 Total Quantity", f"{kpis['total_quantity']:,}")
    
    with col5:
        st.metric("🏷️ Avg Discount", f"{kpis['avg_discount']:.1f}%")
    
    with col6:
        st.metric("↩️ Return Rate", f"{kpis['return_rate']:.1f}%")

def create_visualizations(df):
    """Create all visualizations using Plotly only"""
    st.markdown("---")
    st.header("📊 Sales Analytics Visualizations")
    
    # Check if DataFrame is empty
    if len(df) == 0:
        st.warning("⚠️ No data available for visualization.")
        return
    
    # Dark theme configuration
    dark_theme = {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': 'white'},
        'xaxis': {'gridcolor': '#444', 'linecolor': '#444', 'tickcolor': 'white'},
        'yaxis': {'gridcolor': '#444', 'linecolor': '#444', 'tickcolor': 'white'},
        'title': {'font': {'color': 'white'}}
    }
    
    # Row 1: Revenue trends and category performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly Revenue Trend")
        if len(df) > 0:
            monthly_rev = df.groupby('month')['revenue'].sum().reset_index()
            if len(monthly_rev) > 0:
                fig_line = px.line(
                    monthly_rev, 
                    x='month', 
                    y='revenue', 
                    title='Monthly Sales Revenue',
                    color_discrete_sequence=['#00d4ff']
                )
                fig_line.update_layout(
                    xaxis_title='Month', 
                    yaxis_title='Revenue ($)',
                    hovermode='x unified',
                    **dark_theme
                )
                fig_line.update_traces(
                    mode='lines+markers',
                    line=dict(width=3),
                    marker=dict(size=8)
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No monthly data available")
    
    with col2:
        st.subheader("🏆 Revenue by Category")
        if len(df) > 0:
            rev_by_cat = df.groupby('category')['revenue'].sum().sort_values(ascending=False).reset_index()
            if len(rev_by_cat) > 0:
                fig_bar = px.bar(
                    rev_by_cat, 
                    x='category', 
                    y='revenue',
                    title='Total Revenue by Category',
                    color='revenue',
                    color_continuous_scale='plasma'
                )
                fig_bar.update_layout(
                    xaxis_title='Category', 
                    yaxis_title='Revenue ($)',
                    **dark_theme
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No category data available")
    
    # Row 2: Distribution plots
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Price Distribution")
        if len(df) > 0:
            fig_hist = px.histogram(
                df, 
                x='price', 
                nbins=30, 
                title='Distribution of Sale Prices',
                color_discrete_sequence=['#ff6b6b']
            )
            fig_hist.update_layout(
                xaxis_title='Price ($)', 
                yaxis_title='Count',
                **dark_theme
            )
            fig_hist.update_traces(opacity=0.8)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("📦 Price by Category")
        if len(df) > 0:
            fig_box = px.box(
                df, 
                x='category', 
                y='price',
                title='Price Distribution by Category',
                color='category',
                color_discrete_sequence=['#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd']
            )
            fig_box.update_layout(
                xaxis_title='Category', 
                yaxis_title='Price ($)',
                **dark_theme
            )
            st.plotly_chart(fig_box, use_container_width=True)
    
    # Row 3: Regional and discount analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Sales by Region")
        if len(df) > 0:
            region_counts = df['region'].value_counts().reset_index()
            region_counts.columns = ['region', 'count']
            if len(region_counts) > 0:
                fig_pie = px.pie(
                    region_counts, 
                    names='region', 
                    values='count',
                    title='Sales Distribution by Region',
                    color_discrete_sequence=['#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3']
                )
                fig_pie.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    textfont=dict(color='white', size=12)
                )
                fig_pie.update_layout(
                    **dark_theme,
                    showlegend=True,
                    legend=dict(font=dict(color='white'))
                )
                st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("💰 Discount vs Revenue")
        if len(df) > 0:
            fig_scatter = px.scatter(
                df, 
                x='discount', 
                y='revenue', 
                color='category', 
                size='quantity',
                title='Discount vs Revenue by Category',
                opacity=0.7,
                color_discrete_sequence=['#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff6b6b']
            )
            fig_scatter.update_layout(
                xaxis_title='Discount (%)', 
                yaxis_title='Revenue ($)',
                **dark_theme,
                legend=dict(font=dict(color='white'))
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Row 4: Advanced analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Return Analysis")
        if len(df) > 0:
            return_by_cat = df.groupby('category')['returned'].sum().sort_values(ascending=False).reset_index()
            if len(return_by_cat) > 0:
                fig_return = px.bar(
                    return_by_cat, 
                    x='category', 
                    y='returned',
                    title='Returns by Category',
                    color='returned',
                    color_continuous_scale='hot'
                )
                fig_return.update_layout(
                    xaxis_title='Category', 
                    yaxis_title='Number of Returns',
                    **dark_theme
                )
                st.plotly_chart(fig_return, use_container_width=True)
    
    with col2:
        st.subheader("📊 Quantity Distribution")
        if len(df) > 0:
            fig_qty = px.histogram(
                df, 
                x='quantity', 
                nbins=15,
                title='Quantity Sold per Transaction',
                color_discrete_sequence=['#00ff88']
            )
            fig_qty.update_layout(
                xaxis_title='Quantity', 
                yaxis_title='Count',
                **dark_theme
            )
            fig_qty.update_traces(opacity=0.8)
            st.plotly_chart(fig_qty, use_container_width=True)
    
    # Row 5: Time series analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Daily Sales Trend")
        if len(df) > 0:
            daily_sales = df.groupby(df['date'].dt.date).size().reset_index()
            daily_sales.columns = ['date', 'sales_count']
            if len(daily_sales) > 0:
                fig_daily = px.line(
                    daily_sales,
                    x='date',
                    y='sales_count',
                    title='Daily Sales Volume',
                    color_discrete_sequence=['#ff4757']
                )
                fig_daily.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Number of Sales',
                    **dark_theme
                )
                fig_daily.update_traces(mode='lines+markers', line=dict(width=2))
                st.plotly_chart(fig_daily, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Category Performance")
        if len(df) > 0:
            cat_performance = df.groupby('category').agg({
                'revenue': 'sum',
                'quantity': 'sum',
                'returned': 'sum'
            }).reset_index()
            
            if len(cat_performance) > 0:
                fig_cat_perf = go.Figure()
                fig_cat_perf.add_trace(go.Bar(
                    name='Revenue',
                    x=cat_performance['category'],
                    y=cat_performance['revenue'],
                    yaxis='y',
                    marker_color='#00d4ff'
                ))
                fig_cat_perf.add_trace(go.Scatter(
                    name='Returns',
                    x=cat_performance['category'],
                    y=cat_performance['returned'],
                    yaxis='y2',
                    mode='lines+markers',
                    marker_color='#ff6b6b',
                    line=dict(width=3)
                ))
                
                fig_cat_perf.update_layout(
                    title='Category Performance: Revenue vs Returns',
                    xaxis_title='Category',
                    yaxis=dict(title='Revenue ($)', side='left', color='white', gridcolor='#444', linecolor='#444', tickcolor='white'),
                    yaxis2=dict(title='Returns', side='right', overlaying='y', color='white'),
                    legend=dict(x=0.7, y=1, font=dict(color='white')),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    xaxis={'gridcolor': '#444', 'linecolor': '#444', 'tickcolor': 'white'}
                )
                st.plotly_chart(fig_cat_perf, use_container_width=True)
    
    # Correlation heatmap
    st.subheader("🔗 Correlation Matrix")
    if len(df) > 0:
        num_cols = ['price', 'quantity', 'discount', 'revenue']
        # Check if all columns exist in the dataframe
        available_cols = [col for col in num_cols if col in df.columns]
        if len(available_cols) >= 2:
            corr_matrix = df[available_cols].corr()
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='plasma',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate="%{text}",
                textfont={"size": 14, "color": "white"},
                hoverongaps=False
            ))
            fig_heatmap.update_layout(
                title='Correlation Matrix of Sales Metrics',
                width=600,
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                xaxis={'gridcolor': '#444', 'linecolor': '#444', 'tickcolor': 'white'},
                yaxis={'gridcolor': '#444', 'linecolor': '#444', 'tickcolor': 'white'}
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Advanced visualization: Sunburst chart
    st.subheader("☀️ Revenue Breakdown: Region → Category")
    if len(df) > 0:
        sunburst_data = df.groupby(['region', 'category'])['revenue'].sum().reset_index()
        if len(sunburst_data) > 0:
            fig_sunburst = px.sunburst(
                sunburst_data,
                path=['region', 'category'],
                values='revenue',
                title='Revenue Distribution by Region and Category',
                color='revenue',
                color_continuous_scale='plasma'
            )
            fig_sunburst.update_layout(
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'}
            )
            st.plotly_chart(fig_sunburst, use_container_width=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Sales Analytics Dashboard</h1>
        <p>Comprehensive sales data analysis and insights - Powered by Plotly</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate data
    df = generate_sales_data(5000)
    
    # Apply filters
    filtered_df = apply_filters(df)
    
    # Show filter summary
    st.success(f"📋 Showing {len(filtered_df):,} records out of {len(df):,} total records")
    
    # Calculate and display KPIs
    kpis = calculate_kpis(filtered_df)
    display_kpis(kpis)
    
    # Data export functionality
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Download filtered data
        if len(filtered_df) > 0:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Data",
                data=csv,
                file_name=f'sales_data_filtered_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv',
                help="Download the currently filtered dataset"
            )
    
    with col2:
        # Download full dataset
        csv_full = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv_full,
            file_name=f'sales_data_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
            help="Download the complete dataset"
        )
    
    # Show raw data option
    if st.sidebar.checkbox("👁️ Show Raw Data"):
        st.markdown("### 📄 Raw Data Preview")
        if len(filtered_df) > 0:
            st.dataframe(filtered_df, use_container_width=True, height=300)
        else:
            st.info("No data to display with current filters")
    
    # Create visualizations
    if len(filtered_df) > 0:
        create_visualizations(filtered_df)
    else:
        st.warning("⚠️ No data available with current filters. Please adjust your filter criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit & Plotly | Sales Analytics Dashboard v2.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()