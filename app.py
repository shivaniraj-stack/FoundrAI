import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Local imports
import database as db
import auth
from ai_service import ai_service
import agents
import utils

# Page Configuration
st.set_page_config(
    page_title="FoundrAI — AI Startup Co-Founder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# Load Custom CSS
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

# Ensure session state variables exist
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login" if not st.session_state.get("authenticated", False) else "dashboard"
if "selected_report_id" not in st.session_state:
    st.session_state["selected_report_id"] = None
if "active_analysis_report" not in st.session_state:
    st.session_state["active_analysis_report"] = None

# Check remembered session cookies/local state
auth.check_auth()

def render_sidebar():
    """Renders the professional dark sidebar navigation."""
    with st.sidebar:
        # Branding
        st.markdown("""
        <div class='sidebar-branding'>
            <div class='sidebar-title'>FOUNDR<span>AI</span></div>
            <div style='font-size:0.8rem; color:#9CA3AF; margin-top:0.25rem;'>Co-Founder Intelligence Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Brand Logo if available
        logo_path = "assets/images/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
            st.markdown("<br/>", unsafe_allow_html=True)
            
        # Welcome message
        user = st.session_state.get("user_info")
        if user:
            st.markdown(f"**Welcome, {user['username'].capitalize()}!**")
            st.markdown(f"<span style='font-size:0.8rem; color:#6B7280;'>{user['email']}</span>", unsafe_allow_html=True)
            st.markdown("---")
            
        # Navigation
        st.markdown("<p style='font-size:0.8rem; color:#4B5563; font-weight:600; text-transform:uppercase;'>Menu</p>", unsafe_allow_html=True)
        
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.session_state["selected_report_id"] = None
            st.session_state["active_analysis_report"] = None
            st.rerun()
            
        if st.button("🚀 New Analysis", use_container_width=True):
            st.session_state["current_page"] = "new_analysis"
            st.session_state["selected_report_id"] = None
            st.session_state["active_analysis_report"] = None
            st.rerun()
            
        if st.button("⚙️ Platform Settings", use_container_width=True):
            st.session_state["current_page"] = "settings"
            st.session_state["selected_report_id"] = None
            st.session_state["active_analysis_report"] = None
            st.rerun()
            
        st.markdown("---")
        
        # System Status
        st.markdown("<p style='font-size:0.8rem; color:#4B5563; font-weight:600; text-transform:uppercase;'>Orchestrator Engine</p>", unsafe_allow_html=True)
        if ai_service.is_gemini_available:
            st.markdown('<span class="status-badge status-badge-gemini">🟢 Online AI Mode</span>', unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.75rem; color:#9CA3AF; margin-top:0.25rem;'>Running live LLM multi-agent simulations.</p>", unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-badge-demo">🟡 Offline Demo Mode</span>', unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.75rem; color:#9CA3AF; margin-top:0.25rem;'>Using predefined expert templates.</p>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Logout Button
        if st.button("🚪 Log Out", use_container_width=True):
            auth.logout_user()

def render_footer():
    """Renders a beautiful footer with resource links and legal expanders."""
    # Footnote indicator
    footer_bottom_text = "Made with ❤️ and Gemini AI" if ai_service.is_gemini_available else "Made with ❤️ by FoundrAI"
    
    st.markdown("<div class='footer-container'>", unsafe_allow_html=True)
    
    # 4-Column Footer grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<h4 class='footer-section-title'>Resources</h4>", unsafe_allow_html=True)
        st.markdown("""
        <ul class='footer-links-list'>
            <li><a href='https://ycombinator.com/library' target='_blank'>Startup Planning Guide</a></li>
            <li><a href='https://github.com' target='_blank'>MVP Developer Hub</a></li>
            <li><a href='https://techcrunch.com' target='_blank'>Funding & Seed Rounds</a></li>
            <li><a href='https://pitch.com' target='_blank'>Investor Pitching Library</a></li>
        </ul>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("<h4 class='footer-section-title'>FoundrAI Platform</h4>", unsafe_allow_html=True)
        st.markdown("<p class='footer-text'>Your virtual incubator. Enter your concept, launch our 12 co-founder agents, and export a ready-to-run business strategy.</p>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<h4 class='footer-section-title'>Legal & Support</h4>", unsafe_allow_html=True)
        st.markdown("<p class='footer-text'>Review terms of usage, privacy frameworks, and platform contact details below.</p>", unsafe_allow_html=True)
        
    with col4:
        st.markdown("<h4 class='footer-section-title'>Engine Status</h4>", unsafe_allow_html=True)
        engine_str = "Live Gemini AI Model active" if ai_service.is_gemini_available else "Offline Template Mode active"
        st.markdown(f"<p class='footer-text'>{engine_str}<br/>Version 1.0.0 (Production)</p>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Legal expanders
    with st.expander("About FoundrAI"):
        st.markdown("""
        ### About FoundrAI
        FoundrAI is an AI-powered co-founder simulation dashboard designed for early-stage entrepreneurs. It leverages an orchestrated pipeline of 12 specialized agents to simulate critical business discussions. From initial idea validation and GTM planning to a 3-year financial forecast, FoundrAI prepares you for incubators, investor calls, and developer handoffs.
        """)
        
    with st.expander("Contact & Support"):
        st.markdown("""
        ### Contact Us
        Have questions or want to upgrade your workspace? Reach out at:
        - **Email**: support@foundrai.local
        - **Documentation**: docs.foundrai.local
        - **Community Discord**: discord.gg/foundrai
        """)
        
    with st.expander("Privacy Policy"):
        st.markdown("""
        ### Privacy Policy
        FoundrAI values your privacy. 
        - Your startup description, target audience, and business plans are stored in your local SQLite file (`foundrai.db`).
        - Data is sent to the Google Gemini API *only* when live Gemini Mode is configured via the `.env` file.
        - We do not sell or telemetry your startup ideas.
        """)
        
    with st.expander("Terms of Service"):
        st.markdown("""
        ### Terms of Service
        By using FoundrAI, you acknowledge that:
        - The outputs generated by both Demo Mode and Gemini Mode are artificial simulations.
        - Financial models and market estimates are forecasts and should be independently audited by certified CPAs and market specialists.
        - You retain 100% intellectual property ownership of your generated report documentation.
        """)

    st.markdown("""
    <div style='text-align:center; padding:1.5rem 0; border-top:1px solid #1F2937; color:#9CA3AF; font-size:0.9rem; margin-top:2rem;'>
        Made with ❤️ by Foundr AI
    </div>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    """Renders the main dashboard page."""
    user = st.session_state["user_info"]
    reports = db.get_user_reports(user["id"])
    
    # Dashboard Header Card
    st.markdown(f"""
    <div class='dashboard-header'>
        <div class='dashboard-title'>Co-Founder Workspace</div>
        <div class='dashboard-subtitle'>Welcome back, {user['username'].capitalize()}! Review your generated reports or kick off a new analysis board.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-card-val'>{len(reports)}</div>
            <div class='metric-card-label'>Generated Reports</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        engine_label = "Online AI Mode" if ai_service.is_gemini_available else "Offline Demo Mode"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-card-val' style='color: {"#10B981" if ai_service.is_gemini_available else "#9CA3AF"}'>{engine_label}</div>
            <div class='metric-card-label'>Active Model Engine</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-card-val' style='color: #38BDF8;'>SQLite3</div>
            <div class='metric-card-label'>Database Connection</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Grid: Recent reports & Intro info
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📂 Recent Startup Analyses")
        
        if reports:
            # Custom styled list header
            st.markdown("""
            <div style='display:flex; justify-content:space-between; padding:0.5rem 1rem; border-bottom:1px solid #1F2937; color:#6B7280; font-size:0.8rem; font-weight:600; text-transform:uppercase;'>
                <div style='flex: 3;'>Startup Name</div>
                <div style='flex: 2;'>Industry</div>
                <div style='flex: 2;'>Created At</div>
                <div style='flex: 2; text-align:center;'>Actions</div>
            </div>
            """, unsafe_allow_html=True)
            
            for r in reports:
                col_name, col_ind, col_date, col_actions = st.columns([3, 2, 2, 2])
                col_name.markdown(f"<div style='padding-top: 0.5rem;'><b>{r['startup_name']}</b></div>", unsafe_allow_html=True)
                col_ind.markdown(f"<div style='padding-top: 0.5rem; color:#9CA3AF;'>{r['industry']}</div>", unsafe_allow_html=True)
                # Parse date format
                dt = datetime.fromisoformat(r['created_at'].replace("Z", ""))
                date_str = dt.strftime("%b %d, %Y %H:%M")
                col_date.markdown(f"<div style='padding-top: 0.5rem; color:#9CA3AF;'>{date_str}</div>", unsafe_allow_html=True)
                
                # Action Buttons
                btn_view, btn_del = col_actions.columns(2)
                if btn_view.button("👁️ View", key=f"v_{r['id']}", use_container_width=True, help="Load report analysis"):
                    st.session_state["selected_report_id"] = r["id"]
                    st.session_state["current_page"] = "new_analysis"
                    st.rerun()
                if btn_del.button("🗑️ Del", key=f"d_{r['id']}", use_container_width=True, help="Delete report"):
                    db.delete_report(r["id"])
                    st.success(f"Report for {r['startup_name']} deleted.")
                    st.rerun()
        else:
            st.info("You haven't run any analysis yet. Launch your first co-founder board by clicking 'New Analysis' in the sidebar!")
            
    with col_right:
        st.markdown("### 💡 Interactive Co-Founder Advices")
        
        st.markdown("""
        <div class='custom-card'>
            <div class='card-title'>🎯 Focus on GTM First</div>
            <div class='card-body'>Most startups fail not because of product engineering, but because of poor distribution. Review the <b>Go-To-Market</b> agent plan.</div>
        </div>
        
        <div class='custom-card'>
            <div class='card-title'>⚡ Iterative MVP Roadmap</div>
            <div class='card-body'>Keep your initial builds lean. The <b>MVP Planner</b> designs a strict 12-week feature list. Defer complex integrations to v1.0.</div>
        </div>
        
        <div class='custom-card'>
            <div class='card-title'>🛡️ Mitigate Legal Risks</div>
            <div class='card-body'>Review the <b>Risk Assessment</b> warnings. Ensure you set up privacy terms and correct data encryptions from Day 1.</div>
        </div>
        """, unsafe_allow_html=True)

def render_report_view(report_data):
    """Renders the 12 tabs for the agent report along with download actions."""
    startup_name = report_data["startup_name"]
    industry = report_data["industry"]
    description = report_data["description"]
    audience = report_data["audience"]
    results = report_data["report_results"]
    
    st.markdown(f"## Analysis Report: **{startup_name}**")
    st.markdown(f"<p style='color:#9CA3AF;'><b>Industry:</b> {industry} | <b>Target Audience:</b> {audience}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:0.9rem;'>{description}</p>", unsafe_allow_html=True)
    
    # Download Button
    try:
        pdf_bytes = utils.create_pdf_report(startup_name, industry, description, audience, results)
        st.download_button(
            label="📥 Download Professional PDF Report",
            data=pdf_bytes,
            file_name=f"foundrai_{startup_name.lower().replace(' ', '_')}_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Could not prepare PDF download button: {e}")
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 12 Tabs for the agents
    tabs = st.tabs([
        "💡 Validation", "📊 Market Research", "⚔️ Competitors", "🛡️ SWOT",
        "🧱 Business Model", "💰 Revenue Model", "🛠️ MVP Roadmap", "📣 Go-To-Market",
        "📈 Financials", "💸 Funding Plan", "⚠️ Risks", "🎯 Investor Pitch"
    ])
    
    agent_keys = [
        ("validator", 0), ("market_research", 1), ("competitor_analysis", 2), ("swot", 3),
        ("business_model", 4), ("revenue_strategy", 5), ("mvp_planner", 6), ("gtm_strategy", 7),
        ("financial_forecast", 8), ("funding_strategy", 9), ("risk_assessment", 10), ("pitch_generator", 11)
    ]
    
    for key, tab_idx in agent_keys:
        if key not in results:
            continue
            
        with tabs[tab_idx]:
            res = results[key]
            
            # Print agent status card
            badge_class = "status-badge-gemini" if res.get("mode") == "Gemini" else "status-badge-demo"
            st.markdown(f"""
            <div style='margin-bottom: 1.5rem; text-align: right;'>
                <span class='status-badge {badge_class}'>Agent Mode: {res.get('mode', 'Demo')}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Content
            st.markdown(res["text"])
            
            # Custom components for SWOT and Financials
            if key == "swot" and res.get("structured_data"):
                swot = res["structured_data"]
                st.markdown("#### SWOT Matrix View")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.success(f"**Strengths (S)**\n\n" + "\n".join([f"- {x}" for x in swot.get("s", [])]))
                    st.info(f"**Opportunities (O)**\n\n" + "\n".join([f"- {x}" for x in swot.get("o", [])]))
                with col_s2:
                    st.error(f"**Weaknesses (W)**\n\n" + "\n".join([f"- {x}" for x in swot.get("w", [])]))
                    st.warning(f"**Threats (T)**\n\n" + "\n".join([f"- {x}" for x in swot.get("t", [])]))
                    
            elif key == "financial_forecast" and res.get("structured_data"):
                fin = res["structured_data"]
                st.markdown("#### Financial Analysis Dashboard")
                
                # Check for lists
                rev = fin.get("revenue", [0,0,0])
                exp = fin.get("expenses", [0,0,0])
                prof = fin.get("profit", [0,0,0])
                years = ["Year 1", "Year 2", "Year 3"]
                
                # Draw table
                df_fin = pd.DataFrame({
                    "Year 1": [f"${rev[0]:,}", f"${exp[0]:,}", f"${prof[0]:,}"],
                    "Year 2": [f"${rev[1]:,}", f"${exp[1]:,}", f"${prof[1]:,}"],
                    "Year 3": [f"${rev[2]:,}", f"${exp[2]:,}", f"${prof[2]:,}"]
                }, index=["Revenue", "Expenses", "Net Profit"])
                st.table(df_fin)
                
                # Draw Interactive Plotly Chart
                fig = go.Figure()
                fig.add_trace(go.Bar(x=years, y=rev, name="Gross Revenue", marker_color="#10B981"))
                fig.add_trace(go.Bar(x=years, y=exp, name="Expenses", marker_color="#EF4444"))
                fig.add_trace(go.Bar(x=years, y=prof, name="Net Profit", marker_color="#38BDF8"))
                
                fig.update_layout(
                    title="3-Year Financial Forecast Model",
                    barmode="group",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#F3F4F6",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="USD ($)"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)

def render_new_analysis():
    """Renders the multi-agent wizard or loaded report."""
    user = st.session_state["user_info"]
    
    # 1. Check if a report was selected from history
    selected_id = st.session_state.get("selected_report_id")
    if selected_id:
        report = db.get_report_by_id(selected_id)
        if report:
            # Reconstruct the dict structure
            report_data = {
                "startup_name": report["startup_name"],
                "industry": report["industry"],
                "description": report["description"],
                "audience": "Target Market Segment", # Default audience placeholder for legacy DB rows
                "report_results": report["report_data"]
            }
            # Look up audience if we can parse description or if saved
            if isinstance(report["report_data"], dict) and "validator" in report["report_data"]:
                # Attempt to extract if present
                pass
            render_report_view(report_data)
            return
            
    # 2. Check if there is a running/active report in session memory
    active_report = st.session_state.get("active_analysis_report")
    if active_report:
        render_report_view(active_report)
        # Add button to reset and run another
        if st.button("⬅️ Run Another Analysis", use_container_width=True):
            st.session_state["active_analysis_report"] = None
            st.rerun()
        return

    # 3. Otherwise, render the Form to start a new analysis
    st.markdown("## Launch New Co-Founder Board")
    st.markdown("Fill in the startup concept below. Our 12 specialized agents will analyze your project in parallel.")
    
    with st.form("new_analysis_form"):
        col1, col2 = st.columns(2)
        with col1:
            startup_name_input = st.text_input("Startup Name", placeholder="e.g. HealthSync AI")
            
            # Common industries dropdown with Custom option
            industry_options = [
                "SaaS / Cloud Software",
                "FinTech / Payments & Web3",
                "HealthTech / Biotech & Wellness",
                "E-Commerce / Retail Marketplace",
                "AI & DeepTech / Robotics",
                "CleanEnergy & Sustainability",
                "Other / Custom Vertical"
            ]
            selected_ind_opt = st.selectbox("Industry Vertical", options=industry_options)
            
            if selected_ind_opt == "Other / Custom Vertical":
                industry_input = st.text_input("Specify Industry", placeholder="e.g. EdTech / VR classrooms")
            else:
                industry_input = selected_ind_opt
                
        with col2:
            audience_input = st.text_input("Target Audience", placeholder="e.g. Small clinics, busy founders, students")
            desc_input = st.text_area("Product Description & Core Idea", height=115, placeholder="Describe your product, its features, and how it solves the pain point.")
            
        submit_btn = st.form_submit_button("🚀 Assemble Board & Run Analyses", use_container_width=True)
        
    if submit_btn:
        if not startup_name_input or not industry_input or not audience_input or not desc_input:
            st.error("Please fill in all the input fields to begin.")
            return
            
        # UI Placeholder for running agents
        st.markdown("### 🧠 AI Co-Founder Orchestration Simulation")
        st.markdown("Simulating Board Meetings and analysis... Please do not refresh the page.")
        
        # We will create a list of status rows in session state
        progress_bar = st.progress(0.0)
        
        status_placeholders = []
        agent_names = [
            "Startup Idea Validator", "Market Research Agent", "Competitor Analysis Agent", 
            "SWOT Analysis Agent", "Business Model Generator", "Revenue Strategy Agent", 
            "MVP Planner", "Go-To-Market Strategy Agent", "Financial Forecast Agent", 
            "Funding Strategy Agent", "Risk Assessment Agent", "Investor Pitch Generator"
        ]
        
        # Display rows in pending status
        for name in agent_names:
            row = st.markdown(f"""
            <div class='agent-progress-row'>
                <span class='agent-progress-name'>🤖 {name}</span>
                <span class='agent-progress-status status-pending'>⏳ Pending</span>
            </div>
            """, unsafe_allow_html=True)
            status_placeholders.append(row)
            
        # Orchestrator Callback function to update UI in real-time
        def progress_cb(idx, name_str, status_str):
            pct = float(idx) / len(agent_names)
            progress_bar.progress(pct)
            
            # Map status style
            if status_str == "Running...":
                icon = "⚙️"
                cls = "status-running"
                val = "⚡ Active"
            elif status_str == "Completed":
                icon = "🟢"
                cls = "status-completed"
                val = "✔ Completed"
            elif status_str == "Failed":
                icon = "🔴"
                cls = "status-failed"
                val = "✖ Failed"
            else:
                icon = "⏳"
                cls = "status-pending"
                val = status_str
                
            # Replace placeholder row
            status_placeholders[min(idx, len(agent_names)-1)].markdown(f"""
            <div class='agent-progress-row'>
                <span class='agent-progress-name'>{icon} {name_str}</span>
                <span class='agent-progress-status {cls}'>{val}</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Run Orchestrator
        with st.spinner("All 12 agents are collaborating in the FoundrAI board room..."):
            results = agents.run_startup_orchestrator(
                name=startup_name_input,
                description=desc_input,
                industry=industry_input,
                audience=audience_input,
                progress_callback=progress_cb
            )
            
        progress_bar.progress(1.0)
        st.success("🎉 Platform Orchestrator completed successfully! Analysis report saved.")
        
        # Save to SQLite database
        report_id = db.save_report(
            user_id=user["id"],
            startup_name=startup_name_input,
            industry=industry_input,
            description=desc_input,
            report_data=results
        )
        
        # Save in session memory to view immediately
        st.session_state["active_analysis_report"] = {
            "startup_name": startup_name_input,
            "industry": industry_input,
            "description": desc_input,
            "audience": audience_input,
            "report_results": results
        }
        
        st.rerun()

def render_settings():
    """Renders settings and API diagnostics."""
    user = st.session_state["user_info"]
    st.markdown("## Platform Settings & Diagnostics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 User Information")
        st.markdown(f"""
        - **Username**: `{user['username']}`
        - **Email**: `{user['email']}`
        - **Registered Since**: `{user.get('created_at', 'N/A')}`
        """)
        
    with col2:
        st.markdown("### ⚙️ Engine Diagnostics")
        is_live = ai_service.is_gemini_available
        mode_str = "🟢 Online Mode" if is_live else "🟡 Offline Demo Mode"
        st.markdown(f"**Current Status:** `{mode_str}`")
        
        if is_live:
            st.info("FoundrAI has successfully authenticated with your GEMINI_API_KEY. All queries will be simulated with live model generation.")
        else:
            st.warning("FoundrAI is running in Offline Demo Mode. If you want to enable live AI queries, create a `.env` file in the root folder with: `GEMINI_API_KEY=YOUR_GEMINI_API_KEY` and restart the application.")
            
        # Test connection button
        if st.button("🔄 Test API Key Connectivity", use_container_width=True):
            if is_live:
                try:
                    res = ai_service.generate_text("Verify connection. Respond in 3 words.")
                    if res:
                        st.success(f"Connection Verified: '{res.strip()}'")
                    else:
                        st.error("Received empty response from API.")
                except Exception as test_err:
                    st.error(f"API Diagnostics failed: {test_err}")
            else:
                st.error("No API key loaded. Fill in GEMINI_API_KEY in .env to test.")

# --- MAIN EXECUTION ROUTER ---
def main():
    st.markdown("""
    <h1 style="text-align:center; color:#00E5FF; font-size:56px; font-family:'Outfit',sans-serif; margin-bottom:1rem; margin-top: 1rem;">
        Foundr <span style="color:#FFFFFF;">AI</span>
    </h1>
    """, unsafe_allow_html=True)
    
    is_authenticated = st.session_state.get("authenticated", False)
    current_page = st.session_state.get("current_page", "login")
    
    # If no user is logged in, redirect every protected page to the Login page.
    if not is_authenticated:
        if current_page != "login":
            st.session_state["current_page"] = "login"
            st.rerun()
            
        st.markdown("<div style='min-height: 50vh;'>", unsafe_allow_html=True)
        auth.render_auth_ui()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Center footer for auth page
        st.markdown("""
        <div style='text-align:center; padding:2rem 0; border-top:1px solid rgba(55,65,81,0.3); color:#9CA3AF; font-size:0.9rem; margin-top:3rem;'>
            Made with ❤️ by Foundr AI
        </div>
        """, unsafe_allow_html=True)
    else:
        # If user is authenticated and somehow still on the login page, redirect to dashboard
        if current_page == "login":
            st.session_state["current_page"] = "dashboard"
            st.rerun()
            
        render_sidebar()
        
        # Route main content area
        page = st.session_state.get("current_page", "dashboard")
        
        st.markdown("<div style='min-height: 70vh;'>", unsafe_allow_html=True)
        if page == "dashboard":
            render_dashboard()
        elif page == "new_analysis":
            render_new_analysis()
        elif page == "settings":
            render_settings()
        st.markdown("</div>", unsafe_allow_html=True)
        
        render_footer()

if __name__ == "__main__":
    main()
