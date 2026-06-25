import json
import re
import logging
from ai_service import ai_service

logger = logging.getLogger(__name__)

# Normalize industry categories
def get_industry_category(industry):
    ind = industry.lower()
    if any(k in ind for k in ["saas", "software", "cloud", "b2b", "crm", "enterprise"]):
        return "SaaS"
    elif any(k in ind for k in ["fintech", "finance", "banking", "payment", "crypto", "blockchain", "lending"]):
        return "Fintech"
    elif any(k in ind for k in ["health", "medtech", "medical", "wellness", "clinical", "biotech"]):
        return "Healthtech"
    elif any(k in ind for k in ["commerce", "retail", "shop", "marketplace", "e-commerce", "d2c"]):
        return "E-commerce"
    elif any(k in ind for k in ["ai", "deeptech", "robotics", "machine learning", "ml", "computer vision"]):
        return "AI/Deeptech"
    elif any(k in ind for k in ["clean", "green", "energy", "solar", "sustainability", "climate", "carbon"]):
        return "CleanEnergy"
    else:
        return "Generic"

# Generic execution handler
def execute_agent(agent_key, name, description, industry, audience, system_prompt, user_prompt, demo_func):
    """
    Tries to execute via Gemini, and falls back to demo_func if not active or failing.
    Returns a dict with 'text' and 'structured_data'.
    """
    logger.info(f"Running agent: {agent_key}")
    
    # Try Gemini Mode
    if ai_service.is_gemini_available:
        try:
            response_text = ai_service.generate_text(user_prompt, system_prompt)
            if response_text:
                structured = parse_json_from_text(response_text)
                return {
                    "text": response_text,
                    "structured_data": structured,
                    "mode": "Gemini"
                }
        except Exception as e:
            logger.error(f"Gemini failed for {agent_key}: {e}. Falling back to Demo Mode.")
            
    # Demo Mode Fallback
    text, structured = demo_func(name, description, industry, audience)
    return {
        "text": text,
        "structured_data": structured,
        "mode": "Demo"
    }

def parse_json_from_text(text):
    """Helper to extract a JSON block if the model outputs one."""
    try:
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try raw JSON parsing
        return json.loads(text)
    except:
        return None

# --- AGENT DEMO GENERATORS ---

# 1. Startup Idea Validator
def demo_idea_validator(name, desc, industry, audience):
    category = get_industry_category(industry)
    scores = {"SaaS": 8.7, "Fintech": 8.4, "Healthtech": 8.9, "E-commerce": 8.1, "AI/Deeptech": 9.1, "CleanEnergy": 8.6, "Generic": 8.2}
    score = scores.get(category, 8.5)
    
    text = f"""### 🚀 FoundrAI Validation Report: **{name}**
**Overall Feasibility Score: {score}/10**

#### 1. Core Value Proposition
- **High-Impact Solution**: {name} directly addresses a critical pain point in the {industry} sector by offering a simplified, automated approach.
- **Efficiency Gains**: Optimizes standard workflows, saving time and reducing friction for users.
- **Cost Reduction**: Replaces expensive manual processes or fragmented tooling with a unified system.

#### 2. Customer Pain Points Addressed
- **Complexity & Friction**: Target audience ({audience}) currently struggles with slow, manually coordinated operations.
- **Lack of Integration**: Existing tools are siloed and fail to communicate data effectively.
- **High Entry Barrier**: Difficult learning curves and expensive custom software requirements.

#### 3. Market Fit & Demand Validation
- **Audience Resonance**: High resonance among {audience} who are actively seeking digital tools to streamline their day-to-day work.
- **Willingness to Pay**: Strong indicators of budget allocation in this category, as solutions directly impact productivity or cost savings.
- **Retention Potential**: Low churn potential due to high operational dependency once adopted.

#### 4. Feasibility & Risk Analysis
- **Technical Feasibility**: Highly feasible. Can be developed using modern web stacks and secure APIs.
- **Operational Feasibility**: Moderate. Requires strategic partnerships or clean datasets depending on exact scaling needs.
"""
    return text, {"score": score}

# 2. Market Research Agent
def demo_market_research(name, desc, industry, audience):
    category = get_industry_category(industry)
    data = {
        "SaaS": {"tam": "$45B", "sam": "$12B", "som": "$450M", "cagr": "14.2%"},
        "Fintech": {"tam": "$120B", "sam": "$30B", "som": "$1.2B", "cagr": "18.5%"},
        "Healthtech": {"tam": "$85B", "sam": "$22B", "som": "$750M", "cagr": "16.8%"},
        "E-commerce": {"tam": "$250B", "sam": "$50B", "som": "$1.5B", "cagr": "9.8%"},
        "AI/Deeptech": {"tam": "$180B", "sam": "$45B", "som": "$1.8B", "cagr": "24.5%"},
        "CleanEnergy": {"tam": "$95B", "sam": "$28B", "som": "$900M", "cagr": "19.2%"},
        "Generic": {"tam": "$35B", "sam": "$8B", "som": "$300M", "cagr": "11.5%"}
    }
    m = data.get(category, data["Generic"])
    
    text = f"""### 📊 Market Opportunity: **{name}**
**Industry Sector:** {industry}
**Market CAGR:** {m['cagr']} annually (Forecast 2026 - 2031)

#### 1. Market Size Estimates
- **TAM (Total Addressable Market)**: **{m['tam']}** (The entire global opportunity for software solutions in {industry}).
- **SAM (Serviceable Addressable Market)**: **{m['sam']}** (The core portion of the TAM that fits our business model and target geography).
- **SOM (Serviceable Obtainable Market)**: **{m['som']}** (Our realistic target market share in the next 3-5 years with initial marketing budgets).

#### 2. Key Growth Drivers
- **Digital Acceleration**: Accelerated migration to cloud platforms and automated intelligence in the {industry} space.
- **Data-Driven Decision Making**: Growing demand among {audience} for real-time analytics to improve outcomes.
- **Regulatory Pressure / Security**: Stricter standards forcing companies to modernize old software.

#### 3. Demographic & Target Persona
- **Primary Segment**: Modern professionals and decision-makers within the {audience} demographic.
- **Buying Behavior**: Prefers self-serve SaaS dashboards, value-based pricing, and fast onboarding with minimal training.
"""
    return text, m

# 3. Competitor Analysis Agent
def demo_competitor_analysis(name, desc, industry, audience):
    category = get_industry_category(industry)
    competitors = {
        "SaaS": ["Salesforce/HubSpot (Incumbents)", "ClickUp (Generic Project Tool)", "Monday.com (Work Management)"],
        "Fintech": ["Stripe (Payments standard)", "Adyen (Global scale)", "Revolut Business (Digital bank)"],
        "Healthtech": ["Epic Systems (Legacy EHR)", "Veeva Systems (Life sciences)", "Oscar Health (Modern provider)"],
        "E-commerce": ["Shopify (Platform standard)", "WooCommerce (WordPress integration)", "Amazon Marketplace (Platform host)"],
        "AI/Deeptech": ["OpenAI (Foundation models)", "Anthropic (API standard)", "HuggingFace (Community models)"],
        "CleanEnergy": ["Enphase Energy (Solar standard)", "Tesla Energy (Battery storage)", "Watershed (Carbon tracking)"],
        "Generic": ["Competitor A (Legacy tool)", "Competitor B (Specialized player)", "Competitor C (Manual Excel workarounds)"]
    }
    comp_list = competitors.get(category, competitors["Generic"])
    
    text = f"""### ⚔️ Competitive Analysis: **{name}**

#### 1. Direct Competitors
1. **{comp_list[0]}**
   - *Strengths*: Huge brand trust, extensive feature set, large capital reserves.
   - *Weaknesses*: High pricing, bloated UI, slow development cycle for niche features.
2. **{comp_list[1]}**
   - *Strengths*: Highly flexible, strong automation tools, modern aesthetic.
   - *Weaknesses*: Steeper learning curve, generic templates lack specialized features for {industry}.
3. **{comp_list[2]}**
   - *Strengths*: Good team collaboration tools, popular interface.
   - *Weaknesses*: Weak data analysis capabilities, high integrations configuration friction.

#### 2. FoundrAI Competitive Moat
- **Hyper-Verticalization**: Tailor-made workflows designed specifically for the unique challenges of {audience}.
- **Integrated AI Layer**: Built-in intelligence that automates complex decision-making, rather than just storing data.
- **Fast Onboarding**: Takes minutes to configure compared to days or weeks with enterprise incumbents.

#### 3. Market Gaps Addressed
- **Underserved Mid-Market**: Legacy tools target enterprise clients, leaving mid-market players with overpriced options.
- **Collaboration Friction**: Current solutions lack secure, simple cross-organizational collaboration features.
"""
    return text, {"competitors": comp_list}

# 4. SWOT Analysis Agent
def demo_swot_analysis(name, desc, industry, audience):
    category = get_industry_category(industry)
    swot_items = {
        "SaaS": {
            "s": ["Highly scalable cloud infrastructure", "Vertical focus allows fast iteration", "Proprietary workflow tools"],
            "w": ["High dependency on server costs", "Low initial brand authority", "Small marketing budget"],
            "o": ["Expansion into international markets", "Integration ecosystem with popular APIs", "Upselling enterprise features"],
            "t": ["Rapid replication by well-funded competitors", "Security breaches risk", "Economic downturns impacting budgets"]
        },
        "AI/Deeptech": {
            "s": ["State of the art proprietary LLM orchestration", "Rapid execution speed", "Experienced technical team"],
            "w": ["High API/computing costs", "Continuous model changes require maintenance", "Difficulty hiring AI talent"],
            "o": ["Enterprise customization contracts", "API access monetization", "Patenting core algorithms"],
            "t": ["Big tech launching free built-in features", "IP infringement claims", "Evolving AI regulations"]
        },
        "Generic": {
            "s": ["Agile development and pivoting speed", "Strong customer-centric value", "Low overhead cost"],
            "w": ["Limited marketing reach initially", "Small customer support bandwidth", "Undifferentiated tech stack"],
            "o": ["First-mover advantage in specialized niche", "Partnership with industry platforms", "Organic community growth"],
            "t": ["Changing customer preferences", "Larger competitors moving down-market", "Regulatory compliance changes"]
        }
    }
    items = swot_items.get(category, swot_items["Generic"]) if category in swot_items else swot_items["Generic"]
    
    text = f"""### 🛡️ SWOT Analysis: **{name}**

| Strengths (S) | Weaknesses (W) |
|---|---|
| • {items['s'][0]}<br>• {items['s'][1]}<br>• {items['s'][2]} | • {items['w'][0]}<br>• {items['w'][1]}<br>• {items['w'][2]} |

| Opportunities (O) | Threats (T) |
|---|---|
| • {items['o'][0]}<br>• {items['o'][1]}<br>• {items['o'][2]} | • {items['t'][0]}<br>• {items['t'][1]}<br>• {items['t'][2]} |

#### 🔑 Strategy for Success
- **Mitigate Weaknesses**: Focus heavily on organic developer/user advocacy channels to bypass high initial advertising costs.
- **Leverage Strengths**: Exploit the vertical specialization to land quick wins in underserved segments of the {audience} market.
"""
    return text, items

# 5. Business Model Generator
def demo_business_model(name, desc, industry, audience):
    text = f"""### 🧱 Business Model Canvas: **{name}**

#### 1. Value Propositions
- automated tools tailored for the {industry} sector.
- Streamlined processes saving {audience} up to 15 hours per week.
- Clean dashboards for management reporting and metrics tracking.

#### 2. Key Partners
- **Infrastructure Providers**: AWS/GCP, Stripe for billing, Twilio for communication.
- **Integration Partners**: Major CRM and productivity tools (HubSpot, Slack, Notion).
- **Industry Influencers**: Key opinion leaders in the {industry} sector to drive trust.

#### 3. Key Activities
- Continuous platform development and UI refinement.
- Technical support and onboarding documentation.
- Content marketing and developer relations.

#### 4. Key Resources
- Core software codebase and intellectual property.
- Scalable cloud infrastructure and security systems.
- Domain-expert advisory board.

#### 5. Customer Relationships
- **Self-Serve Model**: Free trials and automated, frictionless signups.
- **Dedicated Support**: Premium support channels for Enterprise clients.
- **Community Forum**: User-to-user support and feature feedback loops.

#### 6. Channels
- **Direct Search & SEO**: High-intent search optimized landing pages.
- **Product Led Growth (PLG)**: Word of mouth referrals and sharing features.
- **B2B Outbound**: Targeted outreach to founders and executives in {audience}.
"""
    return text, None

# 6. Revenue Strategy Agent
def demo_revenue_strategy(name, desc, industry, audience):
    category = get_industry_category(industry)
    tiers = {
        "SaaS": [
            {"name": "Starter", "price": "$29/mo", "features": "Basic tools, 3 users, standard support"},
            {"name": "Growth", "price": "$79/mo", "features": "Advanced workflows, 10 users, priority support, API access"},
            {"name": "Enterprise", "price": "Custom (from $299/mo)", "features": "Unlimited users, dedicated support, custom integrations, SLA"}
        ],
        "Fintech": [
            {"name": "Free", "price": "0.5% transaction fee", "features": "Basic payment routing, 1 account"},
            {"name": "Pro", "price": "$49/mo + 0.2%", "features": "Multi-currency accounts, advanced treasury APIs, standard support"},
            {"name": "Enterprise", "price": "Volume pricing", "features": "Custom settlement cycles, fraud protection, dedicated manager"}
        ],
        "Generic": [
            {"name": "Standard", "price": "$19/mo", "features": "Core functionality for individuals"},
            {"name": "Professional", "price": "$49/mo", "features": "Advanced feature set for growing teams"},
            {"name": "Enterprise", "price": "Custom", "features": "Custom setup, training, and integrations"}
        ]
    }
    t = tiers.get(category, tiers["Generic"]) if category in tiers else tiers["Generic"]
    
    text = f"""### 💰 Revenue Model & Strategy: **{name}**

#### 1. Core Monetization Strategy
We recommend a **Value-Based Subscription Model (SaaS)** combined with usage tiers, aligning price directly with customer value.

#### 2. Pricing Tiers
- **{t[0]['name']} Tier ({t[0]['price']})**: Perfect for early-stage or individual users. Includes {t[0]['features']}.
- **{t[1]['name']} Tier ({t[1]['price']})**: Designed for growing organizations. Includes {t[1]['features']}.
- **{t[2]['name']} Tier ({t[2]['price']})**: Custom contracts tailored to enterprise scale. Includes {t[2]['features']}.

#### 3. Financial Metrics Strategy
- **Target LTV (Lifetime Value)**: $1,200 (Assumes 24-month retention at $50 Average Revenue Per Account).
- **Target CAC (Customer Acquisition Cost)**: $300 (Maintains a healthy 4:1 LTV/CAC ratio).
- **Payback Period**: 6 Months (Recovers acquisition costs quickly to reinvest in engineering).
"""
    return text, t

# 7. MVP Planner
def demo_mvp_planner(name, desc, industry, audience):
    text = f"""### 🛠️ MVP Roadmap: **{name}**

#### 1. Core MVP Features (Must-Haves)
- **User Authentication**: Secure signup/login and account management.
- **Workflow Builder**: Main dashboard for configuring industry tasks.
- **Analytics Panel**: Simple, interactive tables to show operational stats.
- **Export Engine**: Ability to download reports in PDF or CSV formats.

#### 2. Features Deferred to V1.0 (Nice-to-Haves)
- **Integrations Engine**: Automated connections to Slack and HubSpot.
- **Collaborative Workspaces**: Live co-editing and comments for teams.
- **Advanced Forecasting**: AI-driven scenario modeling tools.

#### 3. Recommended Technology Stack
- **Frontend**: Streamlit / React (for highly custom layout needs).
- **Backend**: Python (FastAPI / Streamlit) for rapid prototyping and AI scripts.
- **Database**: SQLite (Development) / PostgreSQL (Production, hosted on Supabase/RDS).
- **Hosting**: Streamlit Community Cloud / Vercel (Frontend) and Render / Fly.io (Backend).

#### 4. 12-Week Roadmap
- **Weeks 1-3 (Foundation)**: Setup database, authentication, and core schema.
- **Weeks 4-6 (Core Features)**: Build out workflows, AI agent connectors, and dashboard UI.
- **Weeks 7-9 (Integrations & Output)**: Implement exporting (PDF), simple charts, and UI styling.
- **Weeks 10-12 (Testing & Launch)**: Run beta testing, fix bugs, deploy to Streamlit Cloud, and launch.
"""
    return text, None

# 8. Go-To-Market Strategy Agent
def demo_gtm_strategy(name, desc, industry, audience):
    text = f"""### 📣 Go-To-Market (GTM) Strategy: **{name}**

#### 1. Positioning & Core Messaging
- **Tagline**: The smartest way to automate workflows for {audience}.
- **Message**: Stop wasting hours on manual processes in the {industry} space. {name} gives you the insights and automated workflows to scale your business.

#### 2. Customer Acquisition Channels
- **Content Marketing (SEO)**: Write detailed guides and case studies addressing problems faced by {audience}.
- **Product-Led Growth (PLG)**: Offer a free trial tier with shareable report URLs to create a natural referral loop.
- **Niche Communities**: Engage on Reddit (r/startups), Product Hunt, HackerNews, and industry-specific Slack groups.
- **Targeted Outbound**: Reaching out to operations executives with custom teaser analysis reports.

#### 3. 30-60-90 Day Action Plan
- **Days 1-30 (Warm-up)**: Build landing page, collect emails for beta access, and publish 5 SEO-focused blog posts.
- **Days 31-60 (Beta Launch)**: Launch beta to 100 users, gather feedback, and launch on Product Hunt.
- **Days 61-90 (Scale)**: Introduce paid tiers, start cold outreach, and launch affiliate/referral programs.
"""
    return text, None

# 9. Financial Forecast Agent
def demo_financial_forecast(name, desc, industry, audience):
    category = get_industry_category(industry)
    # Revenue bases for Year 1, 2, 3
    bases = {
        "SaaS": {"rev": [120000, 480000, 1500000], "exp": [90000, 280000, 750000]},
        "Fintech": {"rev": [150000, 650000, 2200000], "exp": [120000, 420000, 1100000]},
        "Healthtech": {"rev": [100000, 450000, 1600000], "exp": [110000, 350000, 900000]},
        "E-commerce": {"rev": [250000, 900000, 2800000], "exp": [220000, 720000, 2100000]},
        "AI/Deeptech": {"rev": [140000, 700000, 2400000], "exp": [150000, 480000, 1300000]},
        "CleanEnergy": {"rev": [80000, 380000, 1400000], "exp": [95000, 290000, 800000]},
        "Generic": {"rev": [100000, 400000, 1200000], "exp": [85000, 260000, 650000]}
    }
    
    b = bases.get(category, bases["Generic"])
    rev = b["rev"]
    exp = b["exp"]
    prof = [r - e for r, e in zip(rev, exp)]
    
    text = f"""### 📈 Financial Forecast: **{name}**
This forecast illustrates a 3-year projection based on standard scaling structures in the {industry} market.

#### 1. Projections Summary Table

| Metric | Year 1 | Year 2 | Year 3 |
| :--- | :---: | :---: | :---: |
| **Gross Revenue** | ${rev[0]:,} | ${rev[1]:,} | ${rev[2]:,} |
| **Total Expenses** | ${exp[0]:,} | ${exp[1]:,} | ${exp[2]:,} |
| **Net Profit / (Loss)** | ${prof[0]:,} | ${prof[1]:,} | ${prof[2]:,} |
| **Margin (%)** | {int(prof[0]/rev[0]*100)}% | {int(prof[1]/rev[1]*100)}% | {int(prof[2]/rev[2]*100)}% |

#### 2. Key Expense Breakdown
- **R&D (Engineering)**: 50% of budget in Year 1, scaling down to 35% by Year 3.
- **Sales & Marketing**: 30% of budget in Year 1, scaling up to 45% in Year 3 to accelerate user acquisition.
- **G&A (Ops & Hosting)**: Flat 20% across all years.

#### 3. Break-Even Analysis
- **Monthly Burn Rate (Y1)**: Approximately ${int(exp[0]/12):,} / month.
- **Break-Even Month**: Forecasted in **Month 10** of operation as customer subscription revenue covers active expenses.
"""
    return text, {
        "revenue": rev,
        "expenses": exp,
        "profit": prof
    }

# 10. Funding Strategy Agent
def demo_funding_strategy(name, desc, industry, audience):
    text = f"""### 💸 Funding & Capital Plan: **{name}**

#### 1. Current Stage & Valuation
- **Current Stage**: Pre-Seed / Bootstrap.
- **Pre-Money Valuation (Estimate)**: $1.5M - $2.0M based on early prototype and founder expertise.

#### 2. Funding Requirements
- **Target Capital**: **$250,000** for seed runway.
- **Runway Duration**: 18 Months of development, testing, and GTM launch.

#### 3. Suggested Funding Instruments
- **SAFE (Simple Agreement for Future Equity)**: Recommended for fast closure with angel investors, using a $2.5M valuation cap.
- **Bootstrap / Grants**: Leverage government R&D tax credits or founder equity for the initial MVP build.

#### 4. Allocation of Funds
- **Engineering & Product**: 60% (Hire 2 developers, cover hosting and API costs).
- **Marketing & Launch**: 25% (Ad spend, GTM tools, SEO campaigns).
- **Operations & Legal**: 15% (Incorporation, IP trademarks, bookkeeping).
"""
    return text, None

# 11. Risk Assessment Agent
def demo_risk_assessment(name, desc, industry, audience):
    text = f"""### ⚠️ Risk Assessment & Mitigation: **{name}**

#### 1. Technical & Product Risks
- **Risk**: API reliability, latency, or model changes breaking core agent systems.
- **Mitigation**: Implement robust local fallback systems (such as the Demo Mode engine) and cache recurring query templates.

#### 2. Market & Adoption Risks
- **Risk**: Target audience ({audience}) showing high friction during onboarding and low willingness to pay.
- **Mitigation**: Conduct customer interviews early, launch a generous free-trial tier, and continuously refine value metrics.

#### 3. Financial Risks
- **Risk**: Startup running out of capital before reaching product-market fit (PMF).
- **Mitigation**: Keep burn rate low by using contractor teams, avoiding permanent overhead, and prioritizing revenue-generating features.

#### 4. Regulatory & Legal Risks
- **Risk**: Compliance challenges with GDPR/CCPA when analyzing user datasets in the {industry} space.
- **Mitigation**: Enforce data encryption at rest and in transit. Provide a clear privacy policy and clear data delete buttons.
"""
    return text, None

# 12. Investor Pitch Generator
def demo_pitch_generator(name, desc, industry, audience):
    text = f"""### 🎯 Investor Pitch Deck Outline: **{name}**

#### 1. Elevator Pitch
> "{name} is an intelligent platform designed to help {audience} automate complex workflows in the {industry} industry. By replacing manual friction with automated vertical intelligence, we help our users save hours of effort every week and reduce operations costs by up to 40%."

#### 2. 10-Slide Deck Structure
1. **Slide 1: Title Slide** - Logo, tagline, and founders' contact info.
2. **Slide 2: The Problem** - Highlight the massive friction and manual coordination struggles in the {industry} sector.
3. **Slide 3: The Solution** - Introduce {name} as a centralized vertical solution.
4. **Slide 4: Market Size** - Show TAM, SAM, SOM (highlighting the multi-billion dollar opportunity).
5. **Slide 5: Product Demo** - Visual screens of the dashboard, analytics, and workflow automation.
6. **Slide 6: Business Model** - Subscriptions, price tiers, and average contract values.
7. **Slide 7: Go-To-Market** - Product-led growth loops and targeted B2B outbound campaign strategy.
8. **Slide 8: Competition** - Showcase your 2x2 grid displaying {name} as the specialized, affordable choice.
9. **Slide 9: Financials & Traction** - 3-year projected revenue scale and current beta signups.
10. **Slide 10: The Ask** - Raising $250k on a SAFE to hit 100 enterprise contracts in 18 months.
"""
    return text, None

# --- PUBLIC AGENT EXECUTIONS ---

def run_idea_validator(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Startup Idea Validator. You evaluate startup ideas for viability, feasibility, pain point alignment, and initial value proposition."
    user_prompt = f"Analyze the startup '{name}' in the '{industry}' industry.\nDescription: '{description}'\nTarget Audience: '{audience}'\nProvide: 1. Idea Feasibility Score (X/10), 2. Core Value Proposition, 3. Customer Pain Points Addressed, 4. Target Market Fit Analysis."
    return execute_agent("validator", name, description, industry, audience, system_prompt, user_prompt, demo_idea_validator)

def run_market_research(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Market Research Agent. You analyze market sizes (TAM, SAM, SOM), target demographics, and growth trends."
    user_prompt = f"Analyze the market for '{name}' in the '{industry}' industry.\nDescription: '{description}'\nAudience: '{audience}'\nProvide: 1. Market Size Estimates (TAM, SAM, SOM), 2. Key Growth Drivers, 3. Market Growth CAGR%, 4. Target Customer Demographics & Behavior."
    return execute_agent("market_research", name, description, industry, audience, system_prompt, user_prompt, demo_market_research)

def run_competitor_analysis(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Competitor Analysis Agent. You map out competitors, identify market gaps, and find unique advantages."
    user_prompt = f"Analyze competitors for '{name}' ('{industry}').\nDescription: '{description}'\nProvide: 1. Top 3 Direct Competitors & Top 2 Indirect Competitors, 2. Competitor Strengths & Weaknesses, 3. FoundrAI Competitive Advantage (Moat), 4. Key Unaddressed Gaps in the Market."
    return execute_agent("competitor_analysis", name, description, industry, audience, system_prompt, user_prompt, demo_competitor_analysis)

def run_swot_analysis(name, description, industry, audience):
    system_prompt = "You are FoundrAI's SWOT Analysis Agent. You perform detailed SWOT analysis with action items."
    user_prompt = f"Generate a SWOT analysis for '{name}' in the '{industry}' industry.\nDescription: '{description}'\nProvide a complete breakdown of Strengths, Weaknesses, Opportunities, and Threats, and how to leverage strengths to mitigate threats."
    return execute_agent("swot", name, description, industry, audience, system_prompt, user_prompt, demo_swot_analysis)

def run_business_model_generator(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Business Model Generator. You structure the Business Model Canvas details."
    user_prompt = f"Develop a business model for '{name}' in the '{industry}' industry.\nDescription: '{description}'\nDetail: Key Partners, Key Activities, Key Resources, Customer Relationships, Channels, Cost Structure, and Value Propositions."
    return execute_agent("business_model", name, description, industry, audience, system_prompt, user_prompt, demo_business_model)

def run_revenue_strategy(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Revenue Strategy Agent. You define pricing and monetization strategies."
    user_prompt = f"Develop a revenue model for '{name}' ('{industry}').\nDescription: '{description}'\nProvide: 1. Recommended Monetization Model (e.g. SaaS, marketplace, transactional), 2. Proposed Pricing Tiers, 3. Average Contract Value / Customer Lifetime Value estimates, 4. Sales and Distribution Channels."
    return execute_agent("revenue_strategy", name, description, industry, audience, system_prompt, user_prompt, demo_revenue_strategy)

def run_mvp_planner(name, description, industry, audience):
    system_prompt = "You are FoundrAI's MVP Planner. You create feature scopes and development roadmaps."
    user_prompt = f"Create an MVP plan for '{name}' in the '{industry}' industry.\nDescription: '{description}'\nDetail: 1. Core 'Must-Have' MVP Features, 2. Features Deferred to V1.0, 3. Recommended Tech Stack (Frontend, Backend, Database, Host), 4. 12-week development timeline (milestones)."
    return execute_agent("mvp_planner", name, description, industry, audience, system_prompt, user_prompt, demo_mvp_planner)

def run_gtm_strategy(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Go-To-Market Strategy Agent. You design launch plans and marketing strategies."
    user_prompt = f"Design a Go-To-Market plan for '{name}' ('{industry}').\nDescription: '{description}'\nDetail: 1. Launch positioning, 2. Core Acquisition Channels (Organic/Paid/Viral), 3. Initial 30-60-90 Day Action Plan, 4. Budget Allocation recommendations."
    return execute_agent("gtm_strategy", name, description, industry, audience, system_prompt, user_prompt, demo_gtm_strategy)

def run_financial_forecast(name, description, industry, audience):
    system_prompt = ("You are FoundrAI's Financial Forecast Agent. You generate 3-year financial projections and metrics. "
                     "Output a text section, then at the very end of your response, output a raw JSON block with keys 'revenue', 'expenses', 'profit', "
                     "each containing a list of 3 numbers for Year 1, 2, and 3. Ensure the JSON is valid and inside Markdown code ticks: ```json {...} ```.")
    user_prompt = f"Create a 3-year financial forecast for '{name}' in the '{industry}' industry.\nDescription: '{description}'\nDetail: Revenue, Expenses, Net Profit/Loss, and margins."
    
    # Custom runner to handle parsing JSON in Gemini mode if possible
    res = execute_agent("financial_forecast", name, description, industry, audience, system_prompt, user_prompt, demo_financial_forecast)
    
    # If Gemini returned data but failed to parse JSON in default parser, try a custom regex
    if res.get("mode") == "Gemini" and not res.get("structured_data"):
        try:
            # Look for keys in raw text
            text = res["text"]
            match = re.search(r'\"revenue\"\s*:\s*\[(.*?)\].*?\"expenses\"\s*:\s*\[(.*?)\].*?\"profit\"\s*:\s*\[(.*?)\]', text, re.DOTALL)
            if match:
                rev = [float(x.strip()) for x in match.group(1).split(",")]
                exp = [float(x.strip()) for x in match.group(2).split(",")]
                prof = [float(x.strip()) for x in match.group(3).split(",")]
                res["structured_data"] = {"revenue": rev, "expenses": exp, "profit": prof}
        except Exception as e:
            logger.warning(f"Failed to parse custom financial JSON: {e}")
            
        # If still None, fall back to calculated demo arrays to prevent UI crash
        if not res.get("structured_data"):
            _, demo_struct = demo_financial_forecast(name, description, industry, audience)
            res["structured_data"] = demo_struct
            
    return res

def run_funding_strategy(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Funding Strategy Agent. You recommend funding types and equity structures."
    user_prompt = f"Recommend a funding strategy for '{name}' ('{industry}').\nDescription: '{description}'\nOutline: 1. Current Stage (Bootstrap vs Pre-Seed/Seed), 2. Required Capital, 3. Target Investors (Angel vs VC vs Grants), 4. Suggested Equity Dilution and Use of Funds."
    return execute_agent("funding_strategy", name, description, industry, audience, system_prompt, user_prompt, demo_funding_strategy)

def run_risk_assessment(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Risk Assessment Agent. You analyze risks and mitigation plans."
    user_prompt = f"Perform a risk assessment for '{name}' ('{industry}').\nDescription: '{description}'\nDetail: 1. Operational Risks & Mitigation, 2. Financial Risks & Mitigation, 3. Regulatory/Legal Risks & Mitigation, 4. Market/Adoption Risks & Mitigation."
    return execute_agent("risk_assessment", name, description, industry, audience, system_prompt, user_prompt, demo_risk_assessment)

def run_pitch_generator(name, description, industry, audience):
    system_prompt = "You are FoundrAI's Investor Pitch Generator. You write slide outlines and pitch scripts."
    user_prompt = f"Generate an investor pitch deck outline (10 slides) and verbal elevator pitch for '{name}' ('{industry}').\nDescription: '{description}'."
    return execute_agent("pitch_generator", name, description, industry, audience, system_prompt, user_prompt, demo_pitch_generator)

# --- AGENT ORCHESTRATOR ---

def run_startup_orchestrator(name, description, industry, audience, progress_callback=None):
    """
    Orchestrates execution of all 12 agents.
    progress_callback: a callable that takes (agent_index, agent_name, status)
    """
    agents_list = [
        ("validator", "Startup Idea Validator", run_idea_validator),
        ("market_research", "Market Research Agent", run_market_research),
        ("competitor_analysis", "Competitor Analysis Agent", run_competitor_analysis),
        ("swot", "SWOT Analysis Agent", run_swot_analysis),
        ("business_model", "Business Model Generator", run_business_model_generator),
        ("revenue_strategy", "Revenue Strategy Agent", run_revenue_strategy),
        ("mvp_planner", "MVP Planner", run_mvp_planner),
        ("gtm_strategy", "Go-To-Market Strategy Agent", run_gtm_strategy),
        ("financial_forecast", "Financial Forecast Agent", run_financial_forecast),
        ("funding_strategy", "Funding Strategy Agent", run_funding_strategy),
        ("risk_assessment", "Risk Assessment Agent", run_risk_assessment),
        ("pitch_generator", "Investor Pitch Generator", run_pitch_generator),
    ]
    
    results = {}
    for idx, (key, name_str, agent_func) in enumerate(agents_list):
        if progress_callback:
            progress_callback(idx, name_str, "Running...")
            
        try:
            results[key] = agent_func(name, description, industry, audience)
            if progress_callback:
                progress_callback(idx + 1, name_str, "Completed")
        except Exception as e:
            logger.error(f"Error executing agent {name_str}: {e}")
            # Safe fallback text
            results[key] = {
                "text": f"Error running agent {name_str}: {e}",
                "structured_data": None,
                "mode": "Error"
            }
            if progress_callback:
                progress_callback(idx + 1, name_str, "Failed")
                
    return results
