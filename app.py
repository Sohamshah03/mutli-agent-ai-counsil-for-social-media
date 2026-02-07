"""
AI Marketing Council - Streamlit Dashboard
Interactive UI for the autonomous multi-agent marketing system
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime

# Add src to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.debate import DebateOrchestrator
from src.agents import load_agents


# Page configuration
st.set_page_config(
    page_title="AI Marketing Council",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #ddd;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'iterations' not in st.session_state:
    st.session_state.iterations = []
if 'agents_loaded' not in st.session_state:
    st.session_state.agents_loaded = False


def initialize_system():
    """Initialize the agent system"""
    if not st.session_state.agents_loaded:
        with st.spinner("🤖 Loading AI agents..."):
            try:
                st.session_state.orchestrator = DebateOrchestrator()
                st.session_state.agents_loaded = True
                st.success("✅ Agents loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading agents: {str(e)}")
                return False
    return True


def main():
    """Main app function"""
    
    # Header
    st.markdown('<div class="main-header">🤖 AI Marketing Council</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Autonomous Multi-Agent Social Media Strategy System</div>', unsafe_allow_html=True)
    
    # Initialize system
    if not initialize_system():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=AI+Council", use_container_width=True)
        
        st.markdown("## ⚙️ System Status")
        
        if st.session_state.agents_loaded:
            st.success("🟢 Agents Online")
            st.metric("Iterations Run", len(st.session_state.iterations))
        
        st.markdown("---")
        
        st.markdown("## 🎯 Agent Weights")
        if st.session_state.orchestrator:
            agents = st.session_state.orchestrator.agents
            for agent_id, agent in agents.items():
                if agent_id != "arbitrator":
                    st.metric(
                        agent.name,
                        f"{agent.voting_weight:.2f}",
                        delta=None,
                        delta_color="normal"
                    )
        
        st.markdown("---")
        
        if st.button("🔄 Reset System", use_container_width=True):
            st.session_state.orchestrator = DebateOrchestrator()
            st.session_state.iterations = []
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Input",
        "🗣️ Debate",
        "📄 Content",
        "📊 Analytics",
        "🔄 Comparison"
    ])
    
    # TAB 1: INPUT
    with tab1:
        st.header("Campaign Input")
        
        col1, col2 = st.columns(2)
        
        with col1:
            brand_name = st.text_input(
                "Brand Name",
                value="TechFlow AI",
                help="Your company or brand name"
            )
            
            industry = st.selectbox(
                "Industry",
                ["Technology / SaaS", "E-commerce", "Finance", "Healthcare", "Education", "Other"]
            )
            
            target_audience = st.text_area(
                "Target Audience",
                value="Busy professionals, startup founders, tech enthusiasts aged 25-45",
                height=100
            )
        
        with col2:
            product_info = st.text_area(
                "Product/Campaign Info",
                value="Smart Scheduling Assistant - AI-powered calendar optimization that saves 5 hours per week",
                height=100
            )
            
            use_api_trends = st.checkbox(
                "Fetch Real-Time Trends",
                value=False,
                help="Use Google Trends and Reddit APIs (slower)"
            )
            
            generate_image = st.checkbox(
                "Generate Post Image",
                value=False,
                help="Generate AI image (takes ~30 seconds)"
            )
        
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("🚀 Run Campaign", type="primary", use_container_width=True):
                context = {
                    "brand_name": brand_name,
                    "industry": industry,
                    "product_info": product_info,
                    "target_audience": target_audience
                }
                
                with st.spinner("🤖 Running campaign iteration..."):
                    try:
                        result = st.session_state.orchestrator.run_campaign_iteration(
                            context,
                            use_api_trends=use_api_trends,
                            generate_image=generate_image
                        )
                        st.session_state.iterations.append(result)
                        st.success(f"✅ Iteration {len(st.session_state.iterations)} complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col_btn2:
            if st.button("📋 Load Example", use_container_width=True):
                st.info("Example campaign loaded!")
    
    # TAB 2: DEBATE
    with tab2:
        st.header("Agent Debate Transcript")
        
        if not st.session_state.iterations:
            st.info("👈 Run a campaign from the Input tab to see the debate")
        else:
            # Select iteration
            iteration_num = st.selectbox(
                "Select Iteration",
                range(1, len(st.session_state.iterations) + 1),
                format_func=lambda x: f"Iteration {x}"
            )
            
            iteration = st.session_state.iterations[iteration_num - 1]
            
            # Trends
            st.subheader("📊 Trending Topics")
            trends = iteration.get('trends', [])
            if trends:
                trend_cols = st.columns(5)
                for i, trend in enumerate(trends[:5]):
                    with trend_cols[i]:
                        st.metric(
                            trend.get('topic', 'Unknown')[:20],
                            trend.get('volume', 'N/A')
                        )
            
            st.markdown("---")
            
            # Proposals
            st.subheader("💡 Agent Proposals")
            proposals = iteration.get('proposals', {})
            
            for agent_id, proposal in proposals.items():
                agent = st.session_state.orchestrator.agents.get(agent_id)
                if agent:
                    with st.expander(f"🤖 {agent.name} - Proposal", expanded=True):
                        st.markdown(f"**Voting Weight:** {agent.voting_weight:.2f}")
                        st.markdown(proposal)
            
            st.markdown("---")
            
            # Critiques
            st.subheader("🗣️ Agent Critiques")
            critiques = iteration.get('critiques', {})
            
            for agent_id, critique in critiques.items():
                agent = st.session_state.orchestrator.agents.get(agent_id)
                if agent:
                    with st.expander(f"🤖 {agent.name} - Critique"):
                        st.markdown(critique)
            
            st.markdown("---")
            
            # Decision
            st.subheader("⚖️ Arbitrator Decision")
            decision = iteration.get('decision', {})
            
            col_dec1, col_dec2, col_dec3 = st.columns(3)
            with col_dec1:
                st.metric("Winner", decision.get('winner', 'N/A').replace('_', ' ').title())
            with col_dec2:
                st.metric("Confidence", f"{decision.get('confidence', 'N/A')}/10")
            with col_dec3:
                engagement = iteration.get('engagement', {})
                st.metric("Engagement Score", f"{engagement.get('overall_score', 0):.1f}/10")
            
            st.markdown("**Reasoning:**")
            st.info(decision.get('reasoning', 'No reasoning provided'))
            
            st.markdown("**Implementation:**")
            st.success(decision.get('implementation', 'No implementation details'))
    
    # TAB 3: CONTENT
    with tab3:
        st.header("Generated Content")
        
        if not st.session_state.iterations:
            st.info("👈 Run a campaign from the Input tab to see generated content")
        else:
            # Select iteration
            iteration_num = st.selectbox(
                "Select Iteration ",
                range(1, len(st.session_state.iterations) + 1),
                format_func=lambda x: f"Iteration {x}",
                key="content_iter"
            )
            
            iteration = st.session_state.iterations[iteration_num - 1]
            content = iteration.get('content', {})
            
            col_c1, col_c2 = st.columns([1, 1])
            
            with col_c1:
                st.subheader("📝 Post Details")
                
                st.markdown(f"**Platform:** {content.get('platform', 'N/A').upper()}")
                st.markdown(f"**Posting Time:** {content.get('posting_time', 'N/A')}")
                st.markdown(f"**Character Count:** {content.get('char_count', 0)}")
                
                st.markdown("---")
                
                st.markdown("**Caption:**")
                st.code(content.get('caption', 'No caption generated'), language=None)
                
                st.markdown("**Hashtags:**")
                hashtags = content.get('hashtags', [])
                if hashtags:
                    st.write(" ".join(hashtags))
                else:
                    st.write("No hashtags")
            
            with col_c2:
                st.subheader("🖼️ Generated Image")
                
                image_path = content.get('image_path')
                if image_path and os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
                else:
                    st.info("No image generated for this iteration")
            
            st.markdown("---")
            
            # Engagement metrics
            st.subheader("📈 Simulated Engagement")
            engagement = iteration.get('engagement', {})
            
            col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            with col_e1:
                st.metric("Likes", f"{engagement.get('likes', 0):,}")
            with col_e2:
                st.metric("Shares", f"{engagement.get('shares', 0):,}")
            with col_e3:
                st.metric("Comments", f"{engagement.get('comments', 0):,}")
            with col_e4:
                sentiment = engagement.get('sentiment', 0)
                st.metric("Sentiment", f"{sentiment:.0%}")
    
    # TAB 4: ANALYTICS
    with tab4:
        st.header("Analytics & Learning")
        
        if len(st.session_state.iterations) < 1:
            st.info("👈 Run at least one campaign to see analytics")
        else:
            # Agent weights over time
            st.subheader("🎯 Agent Voting Weights Evolution")
            
            weight_history = st.session_state.orchestrator.get_weight_history()
            
            if weight_history:
                # Create dataframe
                iterations_range = range(1, len(st.session_state.iterations) + 1)
                
                fig_weights = go.Figure()
                
                for agent_id, weights in weight_history.items():
                    if weights:
                        agent = st.session_state.orchestrator.agents.get(agent_id)
                        fig_weights.add_trace(go.Scatter(
                            x=list(iterations_range)[:len(weights)],
                            y=weights,
                            mode='lines+markers',
                            name=agent.name if agent else agent_id,
                            line=dict(width=3)
                        ))
                
                fig_weights.update_layout(
                    xaxis_title="Iteration",
                    yaxis_title="Voting Weight",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_weights, use_container_width=True)
            
            st.markdown("---")
            
            # Engagement over iterations
            st.subheader("📊 Engagement Performance")
            
            engagement_data = []
            for i, iteration in enumerate(st.session_state.iterations, 1):
                eng = iteration.get('engagement', {})
                engagement_data.append({
                    'Iteration': i,
                    'Overall Score': eng.get('overall_score', 0),
                    'Likes': eng.get('likes', 0),
                    'Shares': eng.get('shares', 0),
                    'Comments': eng.get('comments', 0)
                })
            
            df_engagement = pd.DataFrame(engagement_data)
            
            fig_engagement = px.bar(
                df_engagement,
                x='Iteration',
                y='Overall Score',
                title='Engagement Score per Iteration',
                color='Overall Score',
                color_continuous_scale='blues'
            )
            
            st.plotly_chart(fig_engagement, use_container_width=True)
            
            st.markdown("---")
            
            # Winner distribution
            st.subheader("🏆 Winning Agent Distribution")
            
            winners = [
                iteration.get('decision', {}).get('winner', 'unknown')
                for iteration in st.session_state.iterations
            ]
            
            winner_counts = pd.Series(winners).value_counts()
            
            fig_winners = px.pie(
                values=winner_counts.values,
                names=[name.replace('_', ' ').title() for name in winner_counts.index],
                title='Decision Distribution'
            )
            
            st.plotly_chart(fig_winners, use_container_width=True)
    
    # TAB 5: COMPARISON
    with tab5:
        st.header("Iteration Comparison")
        
        if len(st.session_state.iterations) < 2:
            st.info("👈 Run at least 2 campaigns to compare iterations")
        else:
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                iter1 = st.selectbox(
                    "First Iteration",
                    range(1, len(st.session_state.iterations) + 1),
                    format_func=lambda x: f"Iteration {x}"
                )
            
            with col_comp2:
                iter2 = st.selectbox(
                    "Second Iteration",
                    range(1, len(st.session_state.iterations) + 1),
                    index=min(1, len(st.session_state.iterations) - 1),
                    format_func=lambda x: f"Iteration {x}"
                )
            
            if iter1 != iter2:
                comparison = st.session_state.orchestrator.compare_iterations(iter1 - 1, iter2 - 1)
                
                st.subheader("📊 Comparison Results")
                
                # Metrics comparison
                col_m1, col_m2, col_m3 = st.columns(3)
                
                with col_m1:
                    st.metric(
                        "Winner Changed",
                        "Yes" if comparison['changes']['winner_changed'] else "No"
                    )
                
                with col_m2:
                    eng_diff = comparison['changes']['engagement_diff']
                    st.metric(
                        "Engagement Change",
                        f"{abs(eng_diff):.1f}",
                        delta=f"{eng_diff:+.1f}",
                        delta_color="normal"
                    )
                
                with col_m3:
                    st.metric(
                        "Learning Active",
                        "Yes" if abs(eng_diff) > 0.5 else "Stable"
                    )
                
                st.markdown("---")
                
                # Side-by-side comparison
                col_side1, col_side2 = st.columns(2)
                
                with col_side1:
                    st.subheader(f"Iteration {iter1}")
                    iter1_data = st.session_state.iterations[iter1 - 1]
                    
                    st.markdown(f"**Winner:** {comparison['iteration_1']['winner'].replace('_', ' ').title()}")
                    st.markdown(f"**Engagement:** {comparison['iteration_1']['engagement']:.1f}/10")
                    
                    st.markdown("**Agent Weights:**")
                    for agent_id, weight in comparison['iteration_1']['weights'].items():
                        st.write(f"- {agent_id.replace('_', ' ').title()}: {weight:.2f}")
                    
                    content1 = iter1_data.get('content', {})
                    st.markdown("**Caption:**")
                    st.code(content1.get('caption', 'N/A')[:200] + "...", language=None)
                
                with col_side2:
                    st.subheader(f"Iteration {iter2}")
                    iter2_data = st.session_state.iterations[iter2 - 1]
                    
                    st.markdown(f"**Winner:** {comparison['iteration_2']['winner'].replace('_', ' ').title()}")
                    st.markdown(f"**Engagement:** {comparison['iteration_2']['engagement']:.1f}/10")
                    
                    st.markdown("**Agent Weights:**")
                    for agent_id, weight in comparison['iteration_2']['weights'].items():
                        st.write(f"- {agent_id.replace('_', ' ').title()}: {weight:.2f}")
                    
                    content2 = iter2_data.get('content', {})
                    st.markdown("**Caption:**")
                    st.code(content2.get('caption', 'N/A')[:200] + "...", language=None)


if __name__ == "__main__":
    main()