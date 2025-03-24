"""
City and Business Dashboard Module

This module provides functions to create dashboard visualizations for the EduRishi Sales Assistant.
It includes visualizations for city distribution, business type analysis, and lead analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter, defaultdict
import random
from datetime import datetime, timedelta
import numpy as np

def create_dashboard_tabs():
    """Create tabs for different dashboard visualizations."""
    dashboard_tabs = st.tabs(["Overview", "Lead Analytics", "City-wise Distribution", "Business Type Analysis"])
    
    with dashboard_tabs[0]:
        # Overview tab
        st.markdown("### Sales Overview")
        
        # Create sample data if no real data exists
        if not st.session_state.leads:
            create_sample_data()
        
        # Create overview visualizations
        create_overview_tab()
    
    with dashboard_tabs[1]:
        # Lead Analytics tab
        create_lead_analytics_tab()
    
    with dashboard_tabs[2]:
        # City Distribution tab
        create_city_distribution_tab()
    
    with dashboard_tabs[3]:
        # Business Type tab
        create_business_type_tab()

def create_sample_data():
    """Create sample data for visualization if no real data exists."""
    # Sample leads
    if not st.session_state.leads:
        from indian_cities_data import generate_mock_lead
        
        # Generate 50 sample leads
        for _ in range(50):
            lead = generate_mock_lead()
            st.session_state.leads.append(lead)
            
            # Update lead statistics
            if lead.get("city"):
                st.session_state.leads_by_city[lead["city"]].append(lead["id"])
                st.session_state.lead_generation_stats["by_city"][lead["city"]] += 1
            
            if lead.get("state"):
                st.session_state.leads_by_state[lead["state"]].append(lead["id"])
                st.session_state.lead_generation_stats["by_state"][lead["state"]] += 1
            
            if lead.get("business_type"):
                st.session_state.leads_by_business_type[lead["business_type"]].append(lead["id"])
                st.session_state.lead_generation_stats["by_business_type"][lead["business_type"]] += 1
            
            # Add to lead sources
            st.session_state.lead_sources[lead.get("source", "Unknown")] += 1
    
    # Sample deals
    if not st.session_state.deals:
        # Convert some leads to deals
        lead_sample = random.sample(st.session_state.leads, min(15, len(st.session_state.leads)))
        
        stages = ["Lead Qualification", "Needs Assessment", "Proposal/Price Quote", 
                 "Negotiation/Review", "Closed Won", "Closed Lost"]
        
        for i, lead in enumerate(lead_sample):
            # Create a deal from this lead
            deal_id = f"deal_{i+1}"
            stage = random.choice(stages)
            
            # Set probability based on stage
            if stage == "Lead Qualification":
                probability = random.randint(10, 20)
            elif stage == "Needs Assessment":
                probability = random.randint(20, 40)
            elif stage == "Proposal/Price Quote":
                probability = random.randint(40, 60)
            elif stage == "Negotiation/Review":
                probability = random.randint(60, 80)
            elif stage == "Closed Won":
                probability = 100
            else:  # Closed Lost
                probability = 0
            
            # Create deal
            deal = {
                "id": deal_id,
                "name": f"Deal with {lead.get('name', 'Unknown')}",
                "lead_id": lead.get("id"),
                "lead_name": lead.get("name", "Unknown"),
                "amount": float(lead.get("budget", 0)) if lead.get("budget") else random.randint(50000, 500000),
                "formatted_amount": f"₹{float(lead.get('budget', 0)):,.2f}" if lead.get("budget") else f"₹{random.randint(50000, 500000):,.2f}",
                "stage": stage,
                "probability": probability,
                "expected_close_date": (datetime.now() + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d"),
                "created_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "last_activity": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d %H:%M:%S"),
                "owner": "Current User",
                "products": lead.get("product_interested", "").split(",") if lead.get("product_interested") else []
            }
            
            st.session_state.deals.append(deal)
            
            # Add to pipeline
            st.session_state.sales_pipeline["deals_by_stage"][stage].append(deal_id)

def create_overview_tab():
    """Create visualizations for the overview tab."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales Pipeline
        create_pipeline_chart()
    
    with col2:
        # Revenue Forecast
        create_revenue_forecast()
    
    # Recent Activity
    st.markdown("### Recent Activity")
    
    if not st.session_state.activity_log:
        # Create sample activity log
        activities = [
            {"description": "New lead created: ABC International School", "timestamp": "2023-06-15 09:30:45", "type": "lead_creation"},
            {"description": "Deal moved to Proposal stage: XYZ Academy", "timestamp": "2023-06-14 14:22:10", "type": "deal_update"},
            {"description": "Meeting scheduled with St. Mary's School", "timestamp": "2023-06-14 11:05:33", "type": "meeting_creation"},
            {"description": "Email sent to Global Education Institute", "timestamp": "2023-06-13 16:45:22", "type": "email_sent"},
            {"description": "Task completed: Follow up with Sunshine Kindergarten", "timestamp": "2023-06-12 10:15:00", "type": "task_completed"}
        ]
        
        for activity in activities:
            st.markdown(f"""
            <div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-bottom: 10px;">
                <strong>{activity["description"]}</strong><br>
                <small>{activity["timestamp"]}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Display actual activity log
        for activity in sorted(st.session_state.activity_log, key=lambda x: x["timestamp"], reverse=True)[:5]:
            st.markdown(f"""
            <div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-bottom: 10px;">
                <strong>{activity["description"]}</strong><br>
                <small>{activity["timestamp"]}</small>
            </div>
            """, unsafe_allow_html=True)

def create_pipeline_chart():
    """Create a sales pipeline visualization."""
    st.markdown("#### Sales Pipeline")
    
    # Prepare data
    stages = st.session_state.sales_pipeline["stages"]
    
    # Count deals in each stage
    stage_counts = []
    stage_values = []
    
    for stage in stages:
        # Get deals in this stage
        stage_deals = [deal for deal in st.session_state.deals if deal.get("stage") == stage]
        stage_counts.append(len(stage_deals))
        stage_values.append(sum(deal.get("amount", 0) for deal in stage_deals))
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=stages,
        x=stage_counts,
        textinfo="value+percent initial",
        marker={"color": ["#1E88E5", "#42A5F5", "#64B5F6", "#90CAF9", "#4CAF50", "#F44336"]}
    ))
    
    fig.update_layout(
        title="Deal Count by Stage",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create value chart
    fig2 = go.Figure(go.Bar(
        y=stages,
        x=stage_values,
        orientation='h',
        marker={"color": ["#1E88E5", "#42A5F5", "#64B5F6", "#90CAF9", "#4CAF50", "#F44336"]}
    ))
    
    fig2.update_layout(
        title="Deal Value by Stage (₹)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        xaxis_title="Value (₹)"
    )
    
    # Format x-axis labels with commas
    fig2.update_xaxes(tickformat=",.0f")
    
    st.plotly_chart(fig2, use_container_width=True)

def create_revenue_forecast():
    """Create a revenue forecast visualization."""
    st.markdown("#### Revenue Forecast")
    
    # Prepare data
    today = datetime.now().date()
    next_90_days = [today + timedelta(days=i) for i in range(90)]
    
    # Calculate expected revenue for each day
    daily_revenue = defaultdict(float)
    
    for deal in st.session_state.deals:
        if deal.get("expected_close_date") and deal.get("amount") and deal.get("probability"):
            close_date = datetime.strptime(deal["expected_close_date"], "%Y-%m-%d").date()
            
            # Only include deals expected to close in the next 90 days
            if today <= close_date <= today + timedelta(days=90):
                # Weight by probability
                weighted_amount = deal["amount"] * deal["probability"] / 100
                daily_revenue[close_date.strftime("%Y-%m-%d")] += weighted_amount
    
    # Create dataframe for visualization
    forecast_data = []
    
    cumulative_revenue = 0
    for day in next_90_days:
        day_str = day.strftime("%Y-%m-%d")
        day_revenue = daily_revenue.get(day_str, 0)
        cumulative_revenue += day_revenue
        
        forecast_data.append({
            "Date": day,
            "Daily Revenue": day_revenue,
            "Cumulative Revenue": cumulative_revenue
        })
    
    df_forecast = pd.DataFrame(forecast_data)
    
    # Create line chart
    fig = px.line(
        df_forecast, 
        x="Date", 
        y="Cumulative Revenue",
        title="Cumulative Revenue Forecast (90 Days)"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        yaxis_title="Revenue (₹)"
    )
    
    # Format y-axis labels with commas
    fig.update_yaxes(tickformat=",.0f")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create bar chart for daily revenue
    fig2 = px.bar(
        df_forecast, 
        x="Date", 
        y="Daily Revenue",
        title="Daily Expected Revenue"
    )
    
    fig2.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        yaxis_title="Revenue (₹)"
    )
    
    # Format y-axis labels with commas
    fig2.update_yaxes(tickformat=",.0f")
    
    st.plotly_chart(fig2, use_container_width=True)

def create_lead_analytics_tab():
    """Create visualizations for lead analytics."""
    st.markdown("### Lead Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Lead Source Distribution
        create_lead_source_chart()
    
    with col2:
        # Lead Status Distribution
        create_lead_status_chart()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Lead Generation Trend
        create_lead_generation_trend()
    
    with col2:
        # Lead Conversion Rate
        create_lead_conversion_chart()

def create_lead_source_chart():
    """Create a chart showing lead distribution by source."""
    st.markdown("#### Lead Source Distribution")
    
    # Count leads by source
    source_counts = Counter()
    
    for lead in st.session_state.leads:
        source = lead.get("source", "Unknown")
        source_counts[source] += 1
    
    # Create dataframe
    df_sources = pd.DataFrame({
        "Source": list(source_counts.keys()),
        "Count": list(source_counts.values())
    })
    
    # Sort by count
    df_sources = df_sources.sort_values("Count", ascending=False)
    
    # Create pie chart
    fig = px.pie(
        df_sources,
        values="Count",
        names="Source",
        title="Lead Sources"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_lead_status_chart():
    """Create a chart showing lead distribution by status."""
    st.markdown("#### Lead Status Distribution")
    
    # Count leads by status
    status_counts = Counter()
    
    for lead in st.session_state.leads:
        status = lead.get("status", "New")
        status_counts[status] += 1
    
    # Create dataframe
    df_status = pd.DataFrame({
        "Status": list(status_counts.keys()),
        "Count": list(status_counts.values())
    })
    
    # Define status order and colors
    status_order = ["Hot", "Warm", "Lukewarm", "Cool", "Cold", "New"]
    status_colors = {
        "Hot": "#FF4500",
        "Warm": "#FFA500",
        "Lukewarm": "#FFD700",
        "Cool": "#87CEEB",
        "Cold": "#ADD8E6",
        "New": "#CCCCCC"
    }
    
    # Sort by status order
    df_status["Status_Order"] = df_status["Status"].apply(lambda x: status_order.index(x) if x in status_order else 999)
    df_status = df_status.sort_values("Status_Order")
    
    # Create bar chart
    fig = px.bar(
        df_status,
        x="Status",
        y="Count",
        title="Lead Status Distribution",
        color="Status",
        color_discrete_map=status_colors
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        xaxis_title="",
        yaxis_title="Number of Leads"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_lead_generation_trend():
    """Create a chart showing lead generation trend over time."""
    st.markdown("#### Lead Generation Trend")
    
    # Get lead creation dates
    dates = []
    
    for lead in st.session_state.leads:
        if lead.get("created_date"):
            try:
                date = datetime.strptime(lead["created_date"], "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                try:
                    date = datetime.strptime(lead["created_date"], "%Y-%m-%d").date()
                except ValueError:
                    continue
            dates.append(date)
    
    # If no dates, create sample data
    if not dates:
        today = datetime.now().date()
        dates = [today - timedelta(days=random.randint(0, 30)) for _ in range(50)]
    
    # Count leads by date
    date_counts = Counter(dates)
    
    # Create dataframe
    df_dates = pd.DataFrame({
        "Date": list(date_counts.keys()),
        "Count": list(date_counts.values())
    })
    
    # Sort by date
    df_dates = df_dates.sort_values("Date")
    
    # Create line chart
    fig = px.line(
        df_dates,
        x="Date",
        y="Count",
        title="Lead Generation Over Time"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        xaxis_title="",
        yaxis_title="Number of Leads"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_lead_conversion_chart():
    """Create a chart showing lead conversion rates."""
    st.markdown("#### Lead Conversion Metrics")
    
    # Calculate conversion rates
    total_leads = len(st.session_state.leads)
    converted_to_deals = len([d for d in st.session_state.deals if d.get("lead_id")])
    won_deals = len([d for d in st.session_state.deals if d.get("stage") == "Closed Won"])
    
    # Calculate rates
    if total_leads > 0:
        deal_conversion_rate = (converted_to_deals / total_leads) * 100
    else:
        deal_conversion_rate = 0
    
    if converted_to_deals > 0:
        win_rate = (won_deals / converted_to_deals) * 100
    else:
        win_rate = 0
    
    # Create gauge charts
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=deal_conversion_rate,
        title={"text": "Lead to Deal Conversion"},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": "#1E88E5"},
            "steps": [
                {"range": [0, 30], "color": "#EF5350"},
                {"range": [30, 70], "color": "#FFCA28"},
                {"range": [70, 100], "color": "#66BB6A"}
            ]
        },
        domain={"row": 0, "column": 0}
    ))
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=win_rate,
        title={"text": "Deal Win Rate"},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": "#1E88E5"},
            "steps": [
                {"range": [0, 30], "color": "#EF5350"},
                {"range": [30, 70], "color": "#FFCA28"},
                {"range": [70, 100], "color": "#66BB6A"}
            ]
        },
        domain={"row": 0, "column": 1}
    ))
    
    fig.update_layout(
        grid={"rows": 1, "columns": 2},
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_city_distribution_tab():
    """Create visualizations for city distribution."""
    st.markdown("### City-wise Lead Distribution")
    
    # Count leads by city
    city_counts = Counter()
    
    for lead in st.session_state.leads:
        city = lead.get("city", "Unknown")
        if city and city != "Unknown":
            city_counts[city] += 1
    
    # Count leads by state
    state_counts = Counter()
    
    for lead in st.session_state.leads:
        state = lead.get("state", "Unknown")
        if state and state != "Unknown":
            state_counts[state] += 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Cities
        create_top_cities_chart(city_counts)
    
    with col2:
        # State Distribution
        create_state_distribution_chart(state_counts)
    
    # City-State Heatmap
    create_city_state_heatmap()

def create_top_cities_chart(city_counts):
    """Create a chart showing top cities by lead count."""
    st.markdown("#### Top Cities by Lead Count")
    
    # Get top 10 cities
    top_cities = dict(city_counts.most_common(10))
    
    # Create dataframe
    df_cities = pd.DataFrame({
        "City": list(top_cities.keys()),
        "Count": list(top_cities.values())
    })
    
    # Sort by count
    df_cities = df_cities.sort_values("Count", ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        df_cities,
        y="City",
        x="Count",
        title="Top 10 Cities by Lead Count",
        orientation="h"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        xaxis_title="Number of Leads",
        yaxis_title=""
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_state_distribution_chart(state_counts):
    """Create a chart showing lead distribution by state."""
    st.markdown("#### Lead Distribution by State")
    
    # Create dataframe
    df_states = pd.DataFrame({
        "State": list(state_counts.keys()),
        "Count": list(state_counts.values())
    })
    
    # Sort by count
    df_states = df_states.sort_values("Count", ascending=False)
    
    # Create pie chart
    fig = px.pie(
        df_states,
        values="Count",
        names="State",
        title="State-wise Distribution"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_city_state_heatmap():
    """Create a heatmap showing lead distribution by city and state."""
    st.markdown("#### City-State Lead Distribution")
    
    # Count leads by city and state
    city_state_counts = defaultdict(int)
    
    for lead in st.session_state.leads:
        city = lead.get("city", "Unknown")
        state = lead.get("state", "Unknown")
        
        if city != "Unknown" and state != "Unknown":
            city_state_counts[(city, state)] += 1
    
    # Create dataframe
    data = []
    
    for (city, state), count in city_state_counts.items():
        data.append({
            "City": city,
            "State": state,
            "Count": count
        })
    
    df_heatmap = pd.DataFrame(data)
    
    # If we have too few data points, add some random ones
    if len(df_heatmap) < 10:
        from indian_cities_data import get_all_cities
        
        cities = get_all_cities()
        for _ in range(20):
            city_data = random.choice(cities)
            data.append({
                "City": city_data["city"],
                "State": city_data["state"],
                "Count": random.randint(1, 10)
            })
        
        df_heatmap = pd.DataFrame(data)
    
    # Create pivot table
    pivot = df_heatmap.pivot_table(
        values="Count",
        index="State",
        columns="City",
        aggfunc="sum",
        fill_value=0
    )
    
    # Create heatmap
    fig = px.imshow(
        pivot,
        labels=dict(x="City", y="State", color="Lead Count"),
        title="Lead Distribution by City and State",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_business_type_tab():
    """Create visualizations for business type analysis."""
    st.markdown("### Business Type Analysis")
    
    # Count leads by business type
    business_counts = Counter()
    
    for lead in st.session_state.leads:
        business_type = lead.get("business_type", "Unknown")
        if business_type and business_type != "Unknown":
            business_counts[business_type] += 1
    
    # Count leads by business subcategory
    subcategory_counts = Counter()
    
    for lead in st.session_state.leads:
        subcategory = lead.get("business_subcategory", "Unknown")
        if subcategory and subcategory != "Unknown":
            subcategory_counts[subcategory] += 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Business Type Distribution
        create_business_type_chart(business_counts)
    
    with col2:
        # Subcategory Distribution
        create_subcategory_chart(subcategory_counts)
    
    # Business Type Performance
    create_business_type_performance()

def create_business_type_chart(business_counts):
    """Create a chart showing lead distribution by business type."""
    st.markdown("#### Lead Distribution by Business Type")
    
    # Create dataframe
    df_business = pd.DataFrame({
        "Business Type": list(business_counts.keys()),
        "Count": list(business_counts.values())
    })
    
    # Sort by count
    df_business = df_business.sort_values("Count", ascending=False)
    
    # Create bar chart
    fig = px.bar(
        df_business,
        x="Business Type",
        y="Count",
        title="Business Type Distribution",
        color="Business Type"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        xaxis_title="",
        yaxis_title="Number of Leads"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_subcategory_chart(subcategory_counts):
    """Create a chart showing lead distribution by business subcategory."""
    st.markdown("#### Lead Distribution by Subcategory")
    
    # Get top 10 subcategories
    top_subcategories = dict(subcategory_counts.most_common(10))
    
    # Create dataframe
    df_subcategories = pd.DataFrame({
        "Subcategory": list(top_subcategories.keys()),
        "Count": list(top_subcategories.values())
    })
    
    # Sort by count
    df_subcategories = df_subcategories.sort_values("Count", ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        df_subcategories,
        y="Subcategory",
        x="Count",
        title="Top 10 Subcategories",
        orientation="h",
        color="Count",
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        xaxis_title="Number of Leads",
        yaxis_title=""
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_business_type_performance():
    """Create a visualization showing performance metrics by business type."""
    st.markdown("#### Business Type Performance Metrics")
    
    # Calculate metrics by business type
    business_metrics = defaultdict(lambda: {"leads": 0, "deals": 0, "won_deals": 0, "total_value": 0})
    
    # Count leads by business type
    for lead in st.session_state.leads:
        business_type = lead.get("business_type", "Unknown")
        if business_type and business_type != "Unknown":
            business_metrics[business_type]["leads"] += 1
    
    # Count deals and won deals by business type
    for deal in st.session_state.deals:
        # Find the lead for this deal
        lead_id = deal.get("lead_id")
        if lead_id:
            lead = next((l for l in st.session_state.leads if l.get("id") == lead_id), None)
            if lead:
                business_type = lead.get("business_type", "Unknown")
                if business_type and business_type != "Unknown":
                    business_metrics[business_type]["deals"] += 1
                    business_metrics[business_type]["total_value"] += deal.get("amount", 0)
                    
                    if deal.get("stage") == "Closed Won":
                        business_metrics[business_type]["won_deals"] += 1
    
    # Create dataframe
    data = []
    
    for business_type, metrics in business_metrics.items():
        # Calculate conversion rate
        if metrics["leads"] > 0:
            conversion_rate = (metrics["deals"] / metrics["leads"]) * 100
        else:
            conversion_rate = 0
        
        # Calculate win rate
        if metrics["deals"] > 0:
            win_rate = (metrics["won_deals"] / metrics["deals"]) * 100
        else:
            win_rate = 0
        
        # Calculate average deal value
        if metrics["deals"] > 0:
            avg_deal_value = metrics["total_value"] / metrics["deals"]
        else:
            avg_deal_value = 0
        
        data.append({
            "Business Type": business_type,
            "Leads": metrics["leads"],
            "Deals": metrics["deals"],
            "Won Deals": metrics["won_deals"],
            "Conversion Rate": conversion_rate,
            "Win Rate": win_rate,
            "Total Value": metrics["total_value"],
            "Avg Deal Value": avg_deal_value
        })
    
    df_metrics = pd.DataFrame(data)
    
    # Create radar chart
    categories = ["Leads", "Deals", "Won Deals", "Conversion Rate", "Win Rate", "Avg Deal Value"]
    
    fig = go.Figure()
    
    for i, row in df_metrics.iterrows():
        # Normalize values for radar chart
        max_leads = df_metrics["Leads"].max() if df_metrics["Leads"].max() > 0 else 1
        max_deals = df_metrics["Deals"].max() if df_metrics["Deals"].max() > 0 else 1
        max_won = df_metrics["Won Deals"].max() if df_metrics["Won Deals"].max() > 0 else 1
        max_conv = 100  # Max conversion rate is 100%
        max_win = 100  # Max win rate is 100%
        max_avg = df_metrics["Avg Deal Value"].max() if df_metrics["Avg Deal Value"].max() > 0 else 1
        
        values = [
            row["Leads"] / max_leads * 100,
            row["Deals"] / max_deals * 100,
            row["Won Deals"] / max_won * 100,
            row["Conversion Rate"],
            row["Win Rate"],
            row["Avg Deal Value"] / max_avg * 100
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=row["Business Type"]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Business Type Performance Comparison",
        margin=dict(l=20, r=20, t=40, b=20),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display metrics table
    st.markdown("#### Business Type Metrics Table")
    
    # Format the dataframe for display
    display_df = df_metrics.copy()
    display_df["Conversion Rate"] = display_df["Conversion Rate"].round(2).astype(str) + "%"
    display_df["Win Rate"] = display_df["Win Rate"].round(2).astype(str) + "%"
    display_df["Total Value"] = display_df["Total Value"].apply(lambda x: f"₹{x:,.2f}")
    display_df["Avg Deal Value"] = display_df["Avg Deal Value"].apply(lambda x: f"₹{x:,.2f}")
    
    st.dataframe(display_df, use_container_width=True)

# Test function
if __name__ == "__main__":
    print("This module provides dashboard visualizations for the EduRishi Sales Assistant.")