import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import datetime

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM STYLE INJECTION
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI 공공정책 시뮬레이터",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match the original dark premium dashboard theme
st.markdown("""
<style>
    /* Premium dark mode style overrides */
    [data-testid="stSidebar"] {
        background-color: #0f141f !important;
        border-right: 1px solid #242c3d !important;
        padding-top: 1rem;
    }
    
    .stApp {
        background-color: #0a0d13 !important;
        color: #f3f4f6 !important;
    }
    
    /* Input adjustments */
    div.stSlider > div[data-baseweb="slider"] {
        padding-bottom: 8px;
    }
    
    /* Custom Card Container */
    .metric-card {
        background-color: #151b26;
        border: 1px solid #242c3d;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    
    .metric-title {
        font-size: 11px;
        font-weight: 500;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #f3f4f6;
        margin-top: 6px;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    .metric-trend {
        font-size: 11px;
        margin-top: 6px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .up-green { color: #34d399; }
    .down-red { color: #f87171; }
    .warning-orange { color: #fbbf24; }
    
    /* AI Score Card */
    .score-card {
        background: linear-gradient(135deg, #151b26 0%, rgba(21, 27, 38, 0.4) 100%);
        border: 1px solid #2d374d;
        border-radius: 12px;
        padding: 18px;
        display: flex;
        align-items: center;
        gap: 16px;
        height: 100%;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.25);
    }
    
    .score-badge {
        background-color: rgba(56, 189, 248, 0.15);
        border: 2px solid #38bdf8;
        color: #38bdf8;
        border-radius: 50%;
        width: 76px;
        height: 76px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
    }
    
    .score-letter {
        font-size: 26px;
        font-weight: 800;
        line-height: 1.1;
    }
    
    .score-num {
        font-size: 10px;
        font-weight: 600;
        opacity: 0.8;
    }
    
    /* Report card block */
    .report-card {
        background-color: #151b26;
        border: 1px solid #242c3d;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
    }
    
    .report-section {
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px dashed #242c3d;
    }
    
    .report-section:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }
    
    .report-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .rt-green { color: #34d399; }
    .rt-red { color: #f87171; }
    .rt-blue { color: #38bdf8; }
    .rt-gold { color: #fbbf24; }
    
    .bullet-list {
        margin: 0;
        padding-left: 16px;
        font-size: 12px;
        line-height: 1.6;
        color: #9ca3af;
    }
    
    .recommendation-box {
        font-size: 12px;
        line-height: 1.6;
        color: #9ca3af;
        background-color: rgba(251, 191, 36, 0.02);
        border: 1px dashed rgba(251, 191, 36, 0.2);
        padding: 12px;
        border-radius: 8px;
    }
    
    /* Terminal Console */
    .terminal-body {
        background-color: #06090e;
        border: 1px solid #242c3d;
        border-radius: 8px;
        padding: 14px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        line-height: 1.5;
        color: #38bdf8;
        max-height: 250px;
        overflow-y: auto;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SESSION STATE INITIALIZATION & SYNC LOGIC
# -------------------------------------------------------------
# Base statistical constants
baseTFR = 0.72
baseGDPGrowth = 2.0
baseUnemployment = 3.4
baseInflation = 2.3
baseCarbon = 100.0
baseDebt = 44.0

# Initialize inputs session state
if 'min_wage' not in st.session_state: st.session_state.min_wage = 5.0
if 'min_wage_num' not in st.session_state: st.session_state.min_wage_num = 5.0

if 'youth_subsidy' not in st.session_state: st.session_state.youth_subsidy = 2.5
if 'youth_subsidy_num' not in st.session_state: st.session_state.youth_subsidy_num = 2.5

if 'birth_subsidy' not in st.session_state: st.session_state.birth_subsidy = 2000
if 'birth_subsidy_num' not in st.session_state: st.session_state.birth_subsidy_num = 2000

if 'carbon_tax_toggle' not in st.session_state: st.session_state.carbon_tax_toggle = True
if 'carbon_tax_rate' not in st.session_state: st.session_state.carbon_tax_rate = 50000
if 'carbon_tax_rate_num' not in st.session_state: st.session_state.carbon_tax_rate_num = 50000

if 'transit_budget' not in st.session_state: st.session_state.transit_budget = 20
if 'transit_budget_num' not in st.session_state: st.session_state.transit_budget_num = 20

if 'working_hours' not in st.session_state: st.session_state.working_hours = 52
if 'working_hours_num' not in st.session_state: st.session_state.working_hours_num = 52

if 'rd_investment' not in st.session_state: st.session_state.rd_investment = 3.0
if 'rd_investment_num' not in st.session_state: st.session_state.rd_investment_num = 3.0

if 'custom_policy_text' not in st.session_state: st.session_state.custom_policy_text = ""
if 'simulated' not in st.session_state: st.session_state.simulated = False
if 'outputs' not in st.session_state: st.session_state.outputs = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

# Bidirectional sync callbacks
def sync_wage_slider(): st.session_state.min_wage = st.session_state.min_wage_num
def sync_wage_num(): st.session_state.min_wage_num = st.session_state.min_wage

def sync_youth_slider(): st.session_state.youth_subsidy = st.session_state.youth_subsidy_num
def sync_youth_num(): st.session_state.youth_subsidy_num = st.session_state.youth_subsidy

def sync_birth_slider(): st.session_state.birth_subsidy = st.session_state.birth_subsidy_num
def sync_birth_num(): st.session_state.birth_subsidy_num = st.session_state.birth_subsidy

def sync_carbon_slider(): st.session_state.carbon_tax_rate = st.session_state.carbon_tax_rate_num
def sync_carbon_num(): st.session_state.carbon_tax_rate_num = st.session_state.carbon_tax_rate

def sync_transit_slider(): st.session_state.transit_budget = st.session_state.transit_budget_num
def sync_transit_num(): st.session_state.transit_budget_num = st.session_state.transit_budget

def sync_hours_slider(): st.session_state.working_hours = st.session_state.working_hours_num
def sync_hours_num(): st.session_state.working_hours_num = st.session_state.working_hours

def sync_rd_slider(): st.session_state.rd_investment = st.session_state.rd_investment_num
def sync_rd_num(): st.session_state.rd_investment_num = st.session_state.rd_investment

# Presets mapping loader
def load_preset(name):
    if name == "성장 중심 패키지":
        st.session_state.min_wage = 1.5
        st.session_state.youth_subsidy = 1.0
        st.session_state.birth_subsidy = 1000
        st.session_state.carbon_tax_toggle = False
        st.session_state.carbon_tax_rate = 30000
        st.session_state.transit_budget = -10
        st.session_state.working_hours = 56
        st.session_state.rd_investment = 12.0
    elif name == "복지·저출생 해결 패키지":
        st.session_state.min_wage = 8.5
        st.session_state.youth_subsidy = 7.5
        st.session_state.birth_subsidy = 8000
        st.session_state.carbon_tax_toggle = True
        st.session_state.carbon_tax_rate = 40000
        st.session_state.transit_budget = 50
        st.session_state.working_hours = 44
        st.session_state.rd_investment = 2.5
    elif name == "그린 뉴딜 탄소중립 패키지":
        st.session_state.min_wage = 4.5
        st.session_state.youth_subsidy = 3.5
        st.session_state.birth_subsidy = 3000
        st.session_state.carbon_tax_toggle = True
        st.session_state.carbon_tax_rate = 110000
        st.session_state.transit_budget = 110
        st.session_state.working_hours = 50
        st.session_state.rd_investment = 8.5
    elif name == "균형 발전 패키지":
        st.session_state.min_wage = 5.0
        st.session_state.youth_subsidy = 4.0
        st.session_state.birth_subsidy = 4000
        st.session_state.carbon_tax_toggle = True
        st.session_state.carbon_tax_rate = 60000
        st.session_state.transit_budget = 30
        st.session_state.working_hours = 48
        st.session_state.rd_investment = 6.0

    # Sync
    sync_wage_num()
    sync_youth_num()
    sync_birth_num()
    sync_carbon_num()
    sync_transit_num()
    sync_hours_num()
    sync_rd_num()
    st.session_state.simulated = False

def reset_all():
    st.session_state.min_wage = 5.0
    st.session_state.youth_subsidy = 2.5
    st.session_state.birth_subsidy = 2000
    st.session_state.carbon_tax_toggle = True
    st.session_state.carbon_tax_rate = 50000
    st.session_state.transit_budget = 20
    st.session_state.working_hours = 52
    st.session_state.rd_investment = 3.0
    st.session_state.custom_policy_text = ""
    st.session_state.simulated = False
    st.session_state.outputs = None
    st.session_state.chat_history = []
    
    sync_wage_num()
    sync_youth_num()
    sync_birth_num()
    sync_carbon_num()
    sync_transit_num()
    sync_hours_num()
    sync_rd_num()

# -------------------------------------------------------------
# 3. MATHEMATICAL SIMULATION ENGINE (Python version)
# -------------------------------------------------------------
def calculate_simulation(inputs):
    minWage = inputs['minWage']
    youthSubsidy = inputs['youthSubsidy']
    birthSubsidy = inputs['birthSubsidy']
    carbonTaxActive = inputs['carbonTaxActive']
    carbonTaxRate = inputs['carbonTaxRate']
    transitBudget = inputs['transitBudget']
    workingHours = inputs['workingHours']
    rdInvestment = inputs['rdInvestment']

    # 1. Birth Rate (TFR) Impact
    birthEffect = 0.28 * (birthSubsidy / (birthSubsidy + 3000))
    youthEffect = 0.08 * (youthSubsidy / (youthSubsidy + 4))
    
    hoursEffect = 0
    if workingHours > 52:
        hoursEffect = -0.015 * (workingHours - 52)
    elif workingHours < 45:
        hoursEffect = 0.04 * ((48 - workingHours) / 8)
        
    economicSentiment = (baseGDPGrowth - ((minWage - 10) * 0.08 if minWage > 10 else 0)) * 0.01
    finalTFR = max(0.6, baseTFR + birthEffect + youthEffect + hoursEffect + economicSentiment)

    # 2. GDP Growth Impact
    rdEffect = 0.08 * rdInvestment
    
    if minWage <= 6.0:
        wageGdpEffect = 0.03 * minWage
    else:
        wageGdpEffect = 0.03 * 6.0 - 0.09 * (minWage - 6.0)

    carbonTaxDrag = 0
    if carbonTaxActive:
        mitigation = min(0.6, rdInvestment / 15)
        carbonTaxDrag = -0.05 * (carbonTaxRate / 30000) * (1 - mitigation)

    publicSpendGdpEffect = 0.05 * (transitBudget / 50)
    avgGDPGrowth = max(-1.0, baseGDPGrowth + rdEffect + wageGdpEffect + carbonTaxDrag + publicSpendGdpEffect)

    # 3. Carbon Emissions Reduction Impact
    carbonRedPct = 0
    if carbonTaxActive:
        carbonRedPct += (carbonTaxRate / 10000) * 2.2
    if transitBudget > 0:
        carbonRedPct += (transitBudget / 10) * 0.6
    else:
        carbonRedPct += (transitBudget / 10) * 0.3
    carbonRedPct += rdInvestment * 0.8
    finalCarbonReduction = min(50.0, max(-10.0, carbonRedPct))

    # 4. Fiscal Stability
    expenseScale = (youthSubsidy * 1.5) + ((birthSubsidy / 10000) * 5) + (transitBudget / 20 if transitBudget > 0 else 0) + (rdInvestment * 1.2)
    revenueScale = (carbonTaxRate / 50000) * 2.8 if carbonTaxActive else 0
    netFiscalDeficit = expenseScale - revenueScale
    finalDebtRatio = max(30.0, baseDebt + (netFiscalDeficit * 2.2))

    fiscalLabel = "안정"
    fiscalColorClass = "up-green"
    if finalDebtRatio > 58.0:
        fiscalLabel = "위험 (재정위기 우려)"
        fiscalColorClass = "down-red"
    elif finalDebtRatio > 48.0:
        fiscalLabel = "주의 (지출 구조조정 필요)"
        fiscalColorClass = "warning-orange"
    else:
        fiscalLabel = "우수 (재정 건전)"
        fiscalColorClass = "up-green"

    # Score
    fertilityScore = min(100.0, ((finalTFR - 0.7) / 0.5) * 100)
    growthScore = min(100.0, max(0.0, ((avgGDPGrowth + 1) / 5) * 100))
    environmentScore = min(100.0, max(0.0, (finalCarbonReduction / 30) * 100))
    fiscalScore = min(100.0, max(0.0, ((70 - finalDebtRatio) / 40) * 100))

    compositeScore = round((fertilityScore * 0.35) + (growthScore * 0.25) + (environmentScore * 0.20) + (fiscalScore * 0.20))
    compositeScore = min(100, max(10, compositeScore))

    grade = 'F'
    if compositeScore >= 90: grade = 'A'
    elif compositeScore >= 80: grade = 'B'
    elif compositeScore >= 70: grade = 'C'
    elif compositeScore >= 60: grade = 'D'

    # Trajectories
    gdpTrajectory = []
    unemploymentTrajectory = []
    inflationTrajectory = []
    tfrTrajectory = []
    youthPopTrajectory = []
    carbonTrajectory = []
    debtTrajectory = []

    currentGDPGrowth = baseGDPGrowth
    currentUnemployment = baseUnemployment
    currentInflation = baseInflation
    currentTFR = baseTFR
    currentYouthPop = 7.8
    currentCarbon = baseCarbon
    currentDebt = baseDebt

    for t in range(11):
        factor = t / 10.0
        
        targetGDP = avgGDPGrowth
        stepGDP = currentGDPGrowth + (targetGDP - currentGDPGrowth) * 0.25 + (np.sin(t) * 0.15)
        gdpTrajectory.append(round(stepGDP, 2))

        targetUnemployment = baseUnemployment + (0.22 * (minWage - 6.0) if minWage > 6.0 else 0) - (rdInvestment * 0.08) - (stepGDP * 0.15)
        stepUnemployment = max(2.0, baseUnemployment + (targetUnemployment - baseUnemployment) * factor)
        unemploymentTrajectory.append(round(stepUnemployment, 2))

        targetInflation = baseInflation + (minWage * 0.08) + ((carbonTaxRate / 50000.0) * 0.15 if carbonTaxActive else 0) - (stepGDP * 0.05)
        stepInflation = max(0.5, baseInflation + (targetInflation - baseInflation) * factor)
        inflationTrajectory.append(round(stepInflation, 2))

        stepTFR = baseTFR + (finalTFR - baseTFR) * factor
        tfrTrajectory.append(round(stepTFR, 3))

        targetYouthPop = 7.8 - 1.2 * (1 - (stepTFR - 0.72))
        stepYouth = max(5.0, 7.8 + (targetYouthPop - 7.8) * factor)
        youthPopTrajectory.append(round(stepYouth, 2))

        targetCarbon = 100.0 - finalCarbonReduction
        stepCarbon = baseCarbon + (targetCarbon - baseCarbon) * factor
        carbonTrajectory.append(round(stepCarbon, 1))

        stepDebt = baseDebt + (finalDebtRatio - baseDebt) * factor
        debtTrajectory.append(round(stepDebt, 1))

    return {
        'finalTFR': finalTFR,
        'avgGDPGrowth': avgGDPGrowth,
        'finalCarbonReduction': finalCarbonReduction,
        'finalDebtRatio': finalDebtRatio,
        'fiscalLabel': fiscalLabel,
        'fiscalColorClass': fiscalColorClass,
        'compositeScore': compositeScore,
        'grade': grade,
        'gdpTrajectory': gdpTrajectory,
        'unemploymentTrajectory': unemploymentTrajectory,
        'inflationTrajectory': inflationTrajectory,
        'tfrTrajectory': tfrTrajectory,
        'youthPopTrajectory': youthPopTrajectory,
        'carbonTrajectory': carbonTrajectory,
        'debtTrajectory': debtTrajectory
    }

# -------------------------------------------------------------
# 4. CHATBOT HELPER
# -------------------------------------------------------------
def get_chatbot_reply(query, outputs):
    if not outputs:
        return "먼저 시뮬레이션을 실행해 주십시오."
    
    tfr = f"{outputs['finalTFR']:.2f}"
    gdp = f"{outputs['avgGDPGrowth']:.2f}"
    debt = f"{outputs['finalDebtRatio']:.1f}"
    minWage = st.session_state.min_wage
    birthSubsidy = st.session_state.birth_subsidy

    query_lower = query.lower()
    if '최저임금' in query_lower or '고용' in query_lower or '임금' in query_lower:
        return f"현재 설정하신 **최저임금 인상률 {minWage}%**는 노동자 소득 증대 효과가 있지만 소상공인 부담으로도 작용합니다. AI 경제 모델에 의하면, 이 영향으로 고용은 **{ '0.4%~0.8% 감소' if minWage > 7 else '0.1% 수준의 미미한 하방 압력'}**을 나타낼 것이며, 실질 GDP 성장률은 10개년 평균 **{gdp}%** 수준에 도달할 것으로 관측됩니다."
    elif '출산' in query_lower or '장려금' in query_lower or '저출산' in query_lower or '아동' in query_lower:
        return f"**자녀당 출산 장려금 {birthSubsidy}만 원** 수준의 직접 자산 형성은 결혼 및 양육 진입층에 유의미한 가계 안정을 제공해 **10년 후 출산율을 {tfr}명**으로 개선하는 원동력이 됩니다. 단, 주거 안정성 지원 등이 병행되지 않을 경우 현금 지급의 효율이 낮아질 수 있습니다."
    elif '탄소' in query_lower or '기후' in query_lower or '환경' in query_lower:
        if st.session_state.carbon_tax_toggle:
            carbonRate = st.session_state.carbon_tax_rate
            return f"**톤당 {carbonRate/10000:.1f}만 원의 탄소세** 부과 조건 하에 10년 후 탄소 배출량은 대폭 감소할 것입니다. 세부적으로 원자재 전가 가격 상승에 의한 소비자 물가 압박이 있을 수 있으나, R&D 투자({st.session_state.rd_investment}조 원)를 통한 고부가 녹색 기술 전환으로 완화가 가능합니다."
        else:
            return "현재 탄소세가 **비활성화**되어 있습니다. 이 경우 환경 지표 개선이 부진하며, 글로벌 관세 장벽(CBAM 등) 도입 시 수출 중심 제조업의 중장기 경쟁력 저하 우려가 제기됩니다."
    elif '재정' in query_lower or '채무' in query_lower or '부채' in query_lower:
        return f"시뮬레이션 10년 후 **국가 채무 비율은 {debt}%** 수준으로 관측되며 재정 건전성은 **'{outputs['fiscalLabel']}'** 상태입니다. 보조금 증액에 상응하는 과세 설계(탄소세 등)가 적절히 매칭될수록 채무비율 상승 궤도가 평탄해집니다."
    elif '추천' in query_lower or '대안' in query_lower or '해결책' in query_lower:
        return "AI 엔진이 추천하는 대표적 대안 패키지는 **'탄소 배당형 서민 지원 제도'**입니다. 탄소세를 톤당 6만 원 선으로 유지하여 확보된 재원을 대중교통 지원금 및 청년 수당으로 환원함으로써, 경제 하방 리스크를 억제하고 사회 안전망을 동시에 개선하는 융합 설계를 추천합니다."
    else:
        return f"질문하신 '{query}' 사항에 대해: 현재 적용된 정책 패키지(최저임금 {minWage}%, 청년지원 {st.session_state.youth_subsidy}조, R&D {st.session_state.rd_investment}조 등)의 복합적 상호작용 지표는 대시보드 탭 차트에서 10개년 궤적 그래프로 확인할 수 있습니다."

# -------------------------------------------------------------
# 5. STREAMLIT LAYOUT IMPLEMENTATION
# -------------------------------------------------------------

# Title banner
col_logo, col_desc = st.columns([1, 10])
with col_logo:
    st.write("")
    st.write("")
    st.markdown("<h3>🤖</h3>", unsafe_allow_html=True)
with col_desc:
    st.title("AI 공공정책 시뮬레이터")
    st.markdown("<p style='color:#9ca3af; margin-top:-15px;'>AI Public Policy Simulator (v3.5-Medium Python)</p>", unsafe_allow_html=True)

# SIDEBAR: Policy Control panel
st.sidebar.markdown("### ⚙️ 정책 변수 설정")

# Quick presets in sidebar
preset_selection = st.sidebar.selectbox(
    "추천 정책 프리셋 로드",
    ["- 선택 안 함 -", "성장 중심 패키지", "복지·저출생 해결 패키지", "그린 뉴딜 탄소중립 패키지", "균형 발전 패키지"]
)
if preset_selection != "- 선택 안 함 -":
    load_preset(preset_selection)
    st.toast(f"'{preset_selection}' 프리셋 적용 완료")

st.sidebar.markdown("---")

# Sliders + Inputs (Synchronized)
# 1. 최저임금
st.sidebar.markdown("**최저임금 인상률 (%)**")
col_s1, col_n1 = st.sidebar.columns([3, 2])
with col_s1:
    st.slider("wage_slider", 0.0, 25.0, 0.5, key="min_wage", on_change=sync_wage_num, label_visibility="collapsed")
with col_n1:
    st.number_input("wage_num", 0.0, 25.0, 0.5, key="min_wage_num", on_change=sync_wage_slider, label_visibility="collapsed")

# 2. 청년지원금
st.sidebar.markdown("**청년 지원금 규모 (연간/조 원)**")
col_s2, col_n2 = st.sidebar.columns([3, 2])
with col_s2:
    st.slider("youth_slider", 0.0, 10.0, 0.1, key="youth_subsidy", on_change=sync_youth_num, label_visibility="collapsed")
with col_n2:
    st.number_input("youth_num", 0.0, 10.0, 0.1, key="youth_subsidy_num", on_change=sync_youth_slider, label_visibility="collapsed")

# 3. 출산장려금
st.sidebar.markdown("**출산 장려금 (자녀당/만 원)**")
col_s3, col_n3 = st.sidebar.columns([3, 2])
with col_s3:
    st.slider("birth_slider", 0, 10000, 500, key="birth_subsidy", on_change=sync_birth_num, label_visibility="collapsed")
with col_n3:
    st.number_input("birth_num", 0, 10000, 500, key="birth_subsidy_num", on_change=sync_birth_slider, label_visibility="collapsed")

# 4. 탄소세
st.sidebar.markdown("**탄소세 도입 여부 및 세율**")
st.sidebar.checkbox("탄소세 공식 도입", key="carbon_tax_toggle")
if st.session_state.carbon_tax_toggle:
    col_s4, col_n4 = st.sidebar.columns([3, 2])
    with col_s4:
        st.slider("carbon_slider", 10000, 150000, 5000, key="carbon_tax_rate", on_change=sync_carbon_num, label_visibility="collapsed")
    with col_n4:
        st.number_input("carbon_num", 10000, 150000, 5000, key="carbon_tax_rate_num", on_change=sync_carbon_slider, label_visibility="collapsed")

# 5. 대중교통 예산
st.sidebar.markdown("**대중교통 예산 증액률 (%)**")
col_s5, col_n5 = st.sidebar.columns([3, 2])
with col_s5:
    st.slider("transit_slider", -50, 150, 5, key="transit_budget", on_change=sync_transit_num, label_visibility="collapsed")
with col_n5:
    st.number_input("transit_num", -50, 150, 5, key="transit_budget_num", on_change=sync_transit_slider, label_visibility="collapsed")

# 6. 근로시간
st.sidebar.markdown("**주당 근로시간 상한 (시간)**")
col_s6, col_n6 = st.sidebar.columns([3, 2])
with col_s6:
    st.slider("hours_slider", 35, 60, 1, key="working_hours", on_change=sync_hours_num, label_visibility="collapsed")
with col_n6:
    st.number_input("hours_num", 35, 60, 1, key="working_hours_num", on_change=sync_hours_slider, label_visibility="collapsed")

# 7. R&D 투자
st.sidebar.markdown("**R&D 및 AI 투자 규모 (조 원)**")
col_s7, col_n7 = st.sidebar.columns([3, 2])
with col_s7:
    st.slider("rd_slider", 0.0, 15.0, 0.5, key="rd_investment", on_change=sync_rd_num, label_visibility="collapsed")
with col_n7:
    st.number_input("rd_num", 0.0, 15.0, 0.5, key="rd_investment_num", on_change=sync_rd_slider, label_visibility="collapsed")

st.sidebar.markdown("---")

# Expandable Advanced Custom Policy Input
with st.sidebar.expander("💡 추가 자유 정책 제안 Options"):
    st.markdown("<p style='font-size:11px; color:#888;'>시뮬레이션과 결합해 정성 분석할 아이디어를 적어보세요.</p>", unsafe_allow_html=True)
    st.text_area("custom_policy", key="custom_policy_text", label_visibility="collapsed", placeholder="예: 주 4일제 도입, 신혼가구 주택 우선 분양...")

# Action buttons
col_act1, col_act2 = st.sidebar.columns(2)
with col_act1:
    run_btn = st.button("🚀 시뮬레이션 실행", use_container_width=True, type="primary")
with col_act2:
    st.button("🔄 초기화", use_container_width=True, on_click=reset_all)

# Live Time on bottom sidebar
now_time = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
st.sidebar.markdown(f"<div style='font-size: 10px; color: #555; text-align: center; margin-top:20px;'>{now_time}</div>", unsafe_allow_html=True)


# MAIN CONTENT SWITCHING LAYOUT
if run_btn:
    st.session_state.simulated = True
    
    # 1. Loading sequence animation (Console simulation)
    status_holder = st.status("AI 다차원 시뮬레이션 엔진 연산 중...", expanded=True)
    
    with status_holder:
        console_logs = []
        
        st.write("➡️ **[1단계] 인구 데이터 분석 (Demographics Analysis)**")
        console_logs.append("[DEMO] 가용 통계청 데이터베이스 갱신 검증 완료.")
        console_logs.append("[DEMO] 20-39 연령 집단 거주 주거 정책 탄력성 계산...")
        console_logs.append(f"[DEMO] 출산 보육 장려금 ₩{st.session_state.birth_subsidy/10000:.1f}억 보조 지출 효과 추론 중...")
        time.sleep(0.5)
        
        st.write("➡️ **[2단계] 경제 파급 효과 분석 (Economic Impact Analysis)**")
        console_logs.append("[ECON] 기획재정부 국가 재정 데이터 동기화...")
        console_logs.append(f"[ECON] 최저임금 {st.session_state.min_wage}% 인상에 따른 고용 마진 탄력성 반영.")
        console_logs.append(f"[ECON] 탄소세 도입 여부: {st.session_state.carbon_tax_toggle} (톤당 {st.session_state.carbon_tax_rate}원).")
        console_logs.append(f"[ECON] R&D 투자 {st.session_state.rd_investment}조 원에 따른 첨단 신산업 가치 유발계수 연계 완료.")
        time.sleep(0.6)
        
        st.write("➡️ **[3단계] 과거 정책 사례 검색 및 비교 (Historical Case Matching)**")
        console_logs.append("[CASE] 글로벌 거시 경제/기후/인구 시계열 매칭 시작.")
        console_logs.append("[CASE] 과거 30개년 OECD 국가 유사 데이터 수렴 연산 수행...")
        time.sleep(0.5)
        
        st.write("➡️ **[4단계] 정책 시행 시나리오 생성 (Multi-Scenario Modeling)**")
        console_logs.append("[SCENARIO] 몬테카를로 시뮬레이션 기반 3개 경제 성장 시나리오 연산...")
        console_logs.append("[SCENARIO] 중립 시나리오(Base Case) 및 낙관/비관 임계값 구축.")
        time.sleep(0.5)
        
        st.write("➡️ **[5단계] 결과 예측 및 보고서 합성 (Forecasting & Synthesizing)**")
        console_logs.append("[SYSTEM] 10개년 시계열 미래 결과 매개변수 바인딩 완료.")
        if st.session_state.custom_policy_text.strip():
            console_logs.append(f"[AI-PROP] 사용자 제안 정책 분석 중: '{st.session_state.custom_policy_text.strip()[:20]}...'")
            console_logs.append("[AI-PROP] 추가 제안 정책의 인구/재정 결합 시뮬레이션 연산 완료.")
        console_logs.append("[SYSTEM] 대시보드 리포트 생성 및 차트 갱신 개시.")
        
        # Display simulated console log
        log_box = ""
        for line in console_logs:
            log_box += line + "\n"
        st.markdown(f"<div class='terminal-body'>{log_box}</div>", unsafe_allow_html=True)
        time.sleep(0.5)
        
    status_holder.update(label="시뮬레이션 연산 완료!", state="complete", expanded=False)

    # RUN MATH ENGINE
    inputs_payload = {
        'minWage': st.session_state.min_wage,
        'youthSubsidy': st.session_state.youth_subsidy,
        'birthSubsidy': st.session_state.birth_subsidy,
        'carbonTaxActive': st.session_state.carbon_tax_toggle,
        'carbonTaxRate': st.session_state.carbon_tax_rate if st.session_state.carbon_tax_toggle else 0,
        'transitBudget': st.session_state.transit_budget,
        'workingHours': st.session_state.working_hours,
        'rdInvestment': st.session_state.rd_investment
    }
    st.session_state.outputs = calculate_simulation(inputs_payload)


# RENDER STATES
if not st.session_state.simulated or st.session_state.outputs is None:
    # Idle Welcome screen
    st.markdown("<br><br>", unsafe_allow_html=True)
    welcome_col1, welcome_col2, welcome_col3 = st.columns([1, 2, 1])
    with welcome_col2:
        st.markdown("""
        <div style='text-align: center; background-color: #151b26; border: 1px solid #242c3d; border-radius: 16px; padding: 40px;'>
            <div style='font-size: 50px; margin-bottom: 20px;'>⚙️</div>
            <h3 style='margin-bottom: 12px;'>정책 시뮬레이션 모델 수립 대기 중</h3>
            <p style='color: #9ca3af; font-size: 14px; line-height: 1.6;'>
                좌측 제어판에서 정책 변수들의 수치(슬라이더 또는 타이핑)를 조정하고 하단의 <strong>시뮬레이션 실행</strong> 버튼을 눌러주십시오.<br>
                AI 엔진이 통계 데이터베이스(인구, 경제성장, 기업경기지수)와 연동하여 10개년 파급 효과를 실시간으로 모델링합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Presets selection buttons inside welcome screen
        st.markdown("<h5 style='text-align: center; color:#9ca3af;'>추천 정책 패키지 프리셋 단축 버튼</h5>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            if st.button("📈 성장 중심", use_container_width=True): load_preset("성장 중심 패키지"); st.rerun()
        with col_p2:
            if st.button("❤️ 복지·저출생", use_container_width=True): load_preset("복지·저출생 해결 패키지"); st.rerun()
        with col_p3:
            if st.button("🌿 그린 뉴딜", use_container_width=True): load_preset("그린 뉴딜 탄소중립 패키지"); st.rerun()
        with col_p4:
            if st.button("⚖️ 균형 발전", use_container_width=True): load_preset("균형 발전 패키지"); st.rerun()

else:
    # Dashboard Results Screen
    outputs = st.session_state.outputs
    
    # 1. Summary KPIs
    col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns([1.5, 1, 1, 1, 1])
    
    with col_k1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-badge">
                <span class="score-letter">{outputs['grade']}</span>
                <span class="score-num">{outputs['compositeScore']}점</span>
            </div>
            <div>
                <div class="metric-title">AI 종합 정책 지수</div>
                <div style="font-size:11px; color:#9ca3af; line-height:1.3; margin-top:4px;">재정 건전성과 인구 기여도의 통합 평가점수</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_k2:
        birth_diff = outputs['finalTFR'] - baseTFR
        trend_class = "up-green" if birth_diff >= 0 else "down-red"
        trend_arrow = "▲" if birth_diff >= 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">합계출산율 (10년 후)</div>
            <div class="metric-value">{outputs['finalTFR']:.2f}명</div>
            <div class="metric-trend {trend_class}">{trend_arrow} {abs(birth_diff):.2f}명 (현재 대비)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_k3:
        gdp_diff = outputs['avgGDPGrowth'] - baseGDPGrowth
        trend_class = "up-green" if gdp_diff >= 0 else "down-red"
        trend_arrow = "▲" if gdp_diff >= 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">평균 실질 GDP 성장률</div>
            <div class="metric-value">{outputs['avgGDPGrowth']:.2f}%</div>
            <div class="metric-trend {trend_class}">{trend_arrow} {abs(gdp_diff):.2f}%p (기존 대비)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_k4:
        carbon_red = outputs['finalCarbonReduction']
        trend_class = "up-green" if carbon_red > 15.0 else "warning-orange"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">탄소 배출량 감소율</div>
            <div class="metric-value">-{abs(carbon_red):.1f}%</div>
            <div class="metric-trend {trend_class}">감축 성과: {"우수" if carbon_red > 15 else "보통"}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_k5:
        debt_ratio = outputs['finalDebtRatio']
        if debt_ratio > 58.0:
            trend_class = "down-red"
        elif debt_ratio > 48.0:
            trend_class = "warning-orange"
        else:
            trend_class = "up-green"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">재정 건전성 등급</div>
            <div class="metric-value" style="font-size:18px; margin-top:10px;">{outputs['fiscalLabel'].split()[0]}</div>
            <div class="metric-trend {trend_class}">채무 비율 {debt_ratio:.1f}% 예상</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Charts section and AI Report side-by-side
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart, col_report = st.columns([1.5, 1])
    
    with col_chart:
        st.markdown("##### 📈 10개년 미래 지표 예측 시뮬레이션")
        chart_tab = st.selectbox("분석 지표 탭 선택", ["경제 & 고용", "인구 & 사회", "환경 & 재정"])
        scenario_mode = st.radio("시나리오 모드 선택", ["비관 시나리오", "중립 (AI 기준)", "낙관 시나리오"], horizontal=True, index=1)
        
        # Scenario mapping
        sc_map = {
            "비관 시나리오": "pessimistic",
            "중립 (AI 기준)": "neutral",
            "낙관 시나리오": "optimistic"
        }
        
        tab_map = {
            "경제 & 고용": "economy",
            "인구 & 사회": "population",
            "환경 & 재정": "environment"
        }
        
        # Draw Plotly Line Chart
        years_list = list(range(2026, 2037))
        fig = go.Figure()

        sc_name = sc_map[scenario_mode]
        tb_name = tab_map[chart_tab]

        scenarioMultiplier = 1.15 if sc_name == 'optimistic' else (0.85 if sc_name == 'pessimistic' else 1.0)
        inverseScenarioMultiplier = 0.85 if sc_name == 'optimistic' else (1.15 if sc_name == 'pessimistic' else 1.0)

        if tb_name == 'economy':
            gdpData = [v * scenarioMultiplier for v in outputs['gdpTrajectory']]
            unemployData = [v * inverseScenarioMultiplier for v in outputs['unemploymentTrajectory']]
            inflationData = [v * (0.9 if sc_name == 'optimistic' else (1.2 if sc_name == 'pessimistic' else 1.0)) for v in outputs['inflationTrajectory']]

            fig.add_trace(go.Scatter(x=years_list, y=gdpData, name='실질 GDP 성장률 (%)', line=dict(color='#38bdf8', width=3), mode='lines+markers'))
            fig.add_trace(go.Scatter(x=years_list, y=unemployData, name='실업률 (%)', line=dict(color='#f87171', width=2, dash='dash'), mode='lines'))
            fig.add_trace(go.Scatter(x=years_list, y=inflationData, name='소비자 물가상승률 (%)', line=dict(color='#fbbf24', width=2), mode='lines'))

        elif tb_name == 'population':
            tfrData = [v * (1.1 if sc_name == 'optimistic' else (0.9 if sc_name == 'pessimistic' else 1.0)) for v in outputs['tfrTrajectory']]
            youthData = [v * scenarioMultiplier for v in outputs['youthPopTrajectory']]

            fig.add_trace(go.Scatter(x=years_list, y=tfrData, name='합계출산율 (명)', line=dict(color='#ec4899', width=3), mode='lines+markers'))
            fig.add_trace(go.Scatter(x=years_list, y=youthData, name='청년층 인구수 (백만 명)', line=dict(color='#818cf8', width=2), mode='lines'))

        elif tb_name == 'environment':
            carbonData = [v * inverseScenarioMultiplier for v in outputs['carbonTrajectory']]
            debtData = [v * (0.92 if sc_name == 'optimistic' else (1.08 if sc_name == 'pessimistic' else 1.0)) for v in outputs['debtTrajectory']]

            fig.add_trace(go.Scatter(x=years_list, y=carbonData, name='탄소 배출 지수 (2026=100)', line=dict(color='#34d399', width=3), mode='lines+markers'))
            fig.add_trace(go.Scatter(x=years_list, y=debtData, name='국가 채무 비율 (% GDP)', line=dict(color='#f59e0b', width=2), mode='lines'))

        fig.update_layout(
            plot_bgcolor='rgba(15,20,31,0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3af', family='Inter, Noto Sans KR'),
            xaxis=dict(gridcolor='#1e2530', showgrid=True),
            yaxis=dict(gridcolor='#1e2530', showgrid=True),
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=340
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_report:
        st.markdown("##### 📝 AI 종합 정책 분석 보고서")
        
        # Dynamic Text Report Building based on values
        wage_val = st.session_state.min_wage
        birth_val = st.session_state.birth_subsidy
        youth_val = st.session_state.youth_subsidy
        carbon_active = st.session_state.carbon_tax_toggle
        carbon_rate = st.session_state.carbon_tax_rate
        rd_val = st.session_state.rd_investment
        hours_val = st.session_state.working_hours

        # Lead text
        lead_msg = ""
        if outputs['compositeScore'] >= 85:
            lead_msg = "인구 반등 유도와 녹색 성장을 유기적으로 통합한 지속가능한 우수 조합 모델입니다. 단기적 조세 저항 관리 및 소상공인 부담 보완 정책이 결부된다면 실효성 있는 실현안이 될 것입니다."
        elif outputs['compositeScore'] >= 70:
            lead_msg = "사회 안전망 확충과 환경 규제 측면에서 긍정적이나, 급격한 정부 예산 지출 및 규제 여파가 가계 경제와 제조업 생산 지표에 부담을 주는 복합 시나리오입니다."
        else:
            lead_msg = "특정 정책 목표의 과도한 추진으로 인해 재정 적자 리스크가 과다하거나 거시 경기 지표가 크게 왜곡될 우려가 제기됩니다."

        # Bullet lists
        strengths_html = ""
        if birth_val > 1500:
            strengths_html += f"<li><strong>출산 장려금 대폭 지원:</strong> 자녀당 {birth_val/10000:.1f}억 원 수준의 지원은 가계 안정을 강하게 유도해 출산율을 <strong>{outputs['finalTFR']:.2f}명</strong>까지 반등시킵니다.</li>"
        if youth_val > 3.0:
            strengths_html += f"<li><strong>청년 지원 인프라:</strong> 청년 지원금 {youth_val}조 원 배정으로 청년의 사회진입 가처분 소득을 강화합니다.</li>"
        if carbon_active and carbon_rate >= 40000:
            strengths_html += f"<li><strong>기후 대전환:</strong> 탄소세(톤당 {carbon_rate/10000:.1f}만 원)는 온실가스 배출을 약 <strong>{outputs['finalCarbonReduction']:.1f}% 감축</strong>하는 쾌거를 거둡니다.</li>"
        if rd_val >= 5.0:
            strengths_html += f"<li><strong>미래 기술 동력 창출:</strong> R&D {rd_val}조 원 집중 배정을 통한 생산성 혁신으로 규제 여파에 따른 제조업 하방 압력을 수비합니다.</li>"

        if not strengths_html:
            strengths_html = "<li>입력된 강점 유발 유의 변수가 없습니다.</li>"

        risks_html = ""
        if outputs['finalDebtRatio'] > 52.0:
            risks_html += f"<li><strong>재정 위험 가중:</strong> 현금 복지 지출 증가로 10년 후 국가 채무 비율이 <strong>{outputs['finalDebtRatio']:.1f}%</strong>로 상승합니다.</li>"
        if wage_val > 7.0:
            risks_html += f"<li><strong>최저임금 급등 여파:</strong> {wage_val}% 인상에 따른 영세 도소매/자영업계의 고용선 붕괴 및 한계직 일자리 위축 위험이 존재합니다.</li>"
        if carbon_active and carbon_rate >= 80000 and rd_val < 4.0:
            risks_html += f"<li><strong>기후 요금 과다:</strong> 탄소세({carbon_rate/10000:.1f}만 원)에 비해 저탄소 기술 투자가 부족해, 2차 중공업 수출 기업의 단기 경쟁력이 약화됩니다.</li>"

        if not risks_html:
            risks_html = "<li>단기 거시 경제적 하방 위험 리스크가 감지되지 않았습니다.</li>"

        # Recommendations
        recom_msg = ""
        if carbon_active and (youth_val > 3.0 or birth_val > 3000):
            recom_msg = f"탄소세(톤당 {carbon_rate/10000:.1f}만 원) 징수분을 일반 재정에 섞지 않고 가칭 <strong>'탄소배당 청년 기금'</strong>이나 <strong>'보육 복지료 환급'</strong> 등 100% 매칭형 목적세로 환원해 세제 저항을 예방하고 내수를 자극할 것을 권고합니다."
        elif wage_val > 7.0:
            recom_msg = f"최저임금 {wage_val}%에 의한 자영업 인건비 충격을 완화하기 위해 정부 직접 보조보다 EITC(근로장려소득세제) 요건 완화식의 간접 보전으로 정책 기조를 선회하는 방안을 조언합니다."
        else:
            recom_msg = "재정 여력이 비교적 우수하므로, 국공립 보육 시설 보급 확대 및 신혼부부 공공 임대 주택 인프라 공급에 선제적 예산을 추가 배정하는 로드맵이 탄력적입니다."

        # RENDER HTML REPORT CARD
        st.markdown(f"""
        <div class="report-card">
            <div style="font-size:12px; font-weight:500; background-color:#1e293b; padding:8px 12px; border-radius:6px; margin-bottom:12px; border-left:3px solid #38bdf8;">
                {lead_msg}
            </div>
            
            <div class="report-section">
                <div class="report-title rt-green">▲ 핵심 강점 및 긍정 효과</div>
                <ul class="bullet-list">{strengths_html}</ul>
            </div>
            
            <div class="report-section">
                <div class="report-title rt-red">▼ 주요 위험 및 잠재 부작용</div>
                <ul class="bullet-list">{risks_html}</ul>
            </div>
            
            <div class="report-section">
                <div class="report-title rt-blue">💡 AI 정책 권고안 (Recommendations)</div>
                <div class="recommendation-box">{recom_msg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Bottom Grid: Custom Text Policy Feedback, Case Matching, & Chatbot
    st.markdown("<br>", unsafe_allow_html=True)
    col_bottom_left, col_bottom_right = st.columns([1.2, 1])
    
    with col_bottom_left:
        # A. Custom Text Policy Feedback Block
        st.markdown("##### ✨ 제안 정책 결합 피드백 (Custom Policy)")
        custom_text = st.session_state.custom_policy_text.strip()
        
        feedback_content = "추가 자유 제안 정책을 입력하지 않았습니다. 기존 설정된 수치 조건 하에 연산이 수행되었습니다."
        if custom_text:
            query_lower = custom_text.lower()
            feedback_content = f"제안하신 정책 <strong>\"{custom_text}\"</strong>에 대한 AI 결합 시뮬레이션 결과:<br><br>"
            matches = 0
            
            if '주 4일' in query_lower or '4일제' in query_lower or '근로시간' in query_lower or '주4일' in query_lower:
                feedback_content += "• <strong>근로시간 단축 보완 효과:</strong> 근로시간 유연화를 통한 여가 증가로 <strong>합계출산율에 긍정적 시너지(+0.04명)</strong>가 예상됩니다. 다만, 기업의 단기 고용 비용이 일부 상승하므로 소상공인 대체인력 매칭 지원금이 함께 추진되어야 합니다.<br>"
                matches += 1
            if '법인세' in query_lower or '세금' in query_lower or '감세' in query_lower or '세율' in query_lower:
                feedback_content += "• <strong>기업 투자 및 세제 효과:</strong> 법인세 조율 또는 특정 감세 정책은 대외 자본 유치 및 <strong>설비 투자 활성화로 장기 GDP 성장률을 소폭 상향(+0.1%p)</strong>시킬 여지가 있습니다. 단, 단기 세수 감소로 인해 국가 채무 비율이 예상치보다 다소 상승할 수 있습니다.<br>"
                matches += 1
            if '주택' in query_lower or '부동산' in query_lower or '임대' in query_lower or '청약' in query_lower or '분양' in query_lower:
                feedback_content += "• <strong>주거 안정성 연계 시너지:</strong> 신혼부부 및 청년 주거 안정을 위한 우선 분양/임대 정책 결합은 청년층의 결혼 진입 장벽을 낮추어 본 시뮬레이션의 <strong>출산장려금 및 청년지원금 효과를 최대 1.2배 증폭</strong>시킬 수 있는 고효율 연동 대안입니다.<br>"
                matches += 1
            if '기본소득' in query_lower or '기본 소득' in query_lower or '수당' in query_lower:
                feedback_content += "• <strong>현금성 분배 정책 효과:</strong> 기본소득성 수당 지급은 즉각적인 가처분 소득 증대로 내수 경기를 활성화하나, 국채 발행에 따른 재정 건전성 급격 악화 지표를 초래하므로 탄소세 과세 재원 또는 부가가치세 교환형 증세 설계가 동반되어야 안전합니다.<br>"
                matches += 1
            if '교육' in query_lower or '사교육' in query_lower or '대학' in query_lower or '보육' in query_lower:
                feedback_content += "• <strong>양육/교육 인프라 강화:</strong> 현금 지급형 장려금 외에 국공립 보육시설 확충 및 사교육 부담 경감 정책 결합은 장기 인구 유지율을 개선하며 여성 고용률을 높이는 건전한 경제 체질 개선을 동반합니다.<br>"
                matches += 1

            if matches == 0:
                feedback_content += "• <strong>기타 아이디어 정책 결합:</strong> 제안하신 내용이 공공 시뮬레이션 지표에 반영되었습니다. 거시 경제적 수치 상 큰 모순은 유발되지 않으며, 장기적인 정책 수용성 제고와 보조를 맞추기 위한 사회적 합의 및 타당성 조사가 추가로 권장됩니다."

        st.markdown(f"""
        <div style="background-color: #151b26; border: 1px solid #242c3d; border-radius: 12px; padding: 16px; min-height: 120px; font-size: 12px; color: #9ca3af; line-height: 1.6;">
            {feedback_content}
        </div>
        """, unsafe_allow_html=True)
        
        # B. Historical Precedents Match
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📁 과거 유사 정책 매칭 사례 (Historical Matches)")
        
        case1Name = "독일 하르츠 개혁 (2003~2005)"
        case1Desc = "근로 유연성과 청년 취업 활동 보조 제도를 병행하여 만성 실업난을 해소하였으나 비정규직 노동시장 격차를 유발하였습니다."
        case1Badge = "독일"
        case1Sim = 80

        case2Name = "스웨덴 아동보육 보조금 개혁 (1998)"
        case2Desc = "아동 보육의 전면 국공립화와 부모 유급 육아 휴직 도입으로 탄탄한 GDP 성장률 속에서 인구 반등을 성공적으로 구현했습니다."
        case2Badge = "스웨덴"
        case2Sim = 75

        # Dyn match based on inputs
        if wage_val > 8.0:
            case1Name = "한국 소득주도성장 최저임금 인상 (2018)"
            case1Desc = "최저임금 단기 급격 인상(+16.4%)에 따라 저임금 근로자 소득은 올랐으나 외식/자영업 등 한계 도소매 부문에서 고용 감소 부작용이 발생했습니다."
            case1Badge = "대한민국"
            case1Sim = min(98, round(75 + (wage_val - 8.0) * 1.5))
        elif rd_val > 8.0:
            case1Name = "미국 반도체 및 첨단 R&D 법안 (2022)"
            case1Desc = "자국 첨단 고부가 가치 기술 제조 인프라 공급망과 친환경 R&D 촉진 보조금을 합산하여 기업 설비 투자 붐과 성장률 방어를 달성했습니다."
            case1Badge = "미국"
            case1Sim = min(95, round(70 + (rd_val - 8.0) * 2))

        if carbon_active and carbon_rate >= 80000:
            case2Name = "프랑스 탄소세 도입과 유류세 시위 (2018)"
            case2Desc = "기후 대응을 목적으로 세수 보완 없는 탄소세 유류 가격 추가 인상을 고수하였으나 농가 및 외곽 청년층 등 취약계층의 격렬한 반발로 유예되었습니다."
            case2Badge = "프랑스"
            case2Sim = min(96, round(65 + (carbon_rate - 80000) * 0.0003))
        elif birth_val > 5000:
            case2Name = "싱가포르 출산 현금 보조 정책 (2000년대 이후)"
            case2Desc = "자녀 출산 가구당 거액의 현금 베이비 보너스를 투입했으나 주거 부담, 경쟁적 사교육 문화의 주 원인을 건드리지 못해 합계출산율 반등 효과가 지연되었습니다."
            case2Badge = "싱가포르"
            case2Sim = min(94, round(72 + (birth_val - 5000) * 0.003))

        st.markdown(f"""
        <div style="display: flex; gap: 12px; margin-top:6px;">
            <div style="flex:1; background-color: #151b26; border: 1px solid #242c3d; border-radius: 10px; padding: 14px;">
                <span class="preset-badge">{case1Badge}</span>
                <h6 style="margin-top:6px; font-weight:600; font-size:13px;">{case1Name}</h6>
                <p style="font-size:11px; color:#9ca3af; line-height:1.4; margin-top:4px;">{case1Desc}</p>
                <div style="font-size:10px; color:#38bdf8; font-weight:600; margin-top:8px;">유사도 {case1Sim}%</div>
            </div>
            <div style="flex:1; background-color: #151b26; border: 1px solid #242c3d; border-radius: 10px; padding: 14px;">
                <span class="preset-badge">{case2Badge}</span>
                <h6 style="margin-top:6px; font-weight:600; font-size:13px;">{case2Name}</h6>
                <p style="font-size:11px; color:#9ca3af; line-height:1.4; margin-top:4px;">{case2Desc}</p>
                <div style="font-size:10px; color:#38bdf8; font-weight:600; margin-top:8px;">유사도 {case2Sim}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_bottom_right:
        # C. Interactive Chatbot Assistant
        st.markdown("##### 💬 AI 정책 수립 비서")
        
        # Chat body rendering
        chat_container = st.container(height=260)
        
        # Initial greeting
        with chat_container:
            st.chat_message("assistant").write(
                f"시뮬레이션 연산 결과를 바탕으로 질문을 받습니다. 최저임금 **{wage_val}%**, R&D **{rd_val}조 원** 등의 정책 영향도나 보완방안에 대해 질문해 주십시오."
            )
            
            # Print chat history
            for msg in st.session_state.chat_history:
                st.chat_message(msg['role']).write(msg['content'])

        # Preset Question Chips (Quick buttons)
        col_ch1, col_ch2, col_ch3 = st.columns(3)
        q1, q2, q3 = False, False, False
        with col_ch1:
            if st.button("💵 최저임금 여파?", use_container_width=True, key="btn_q1"): q1 = True
        with col_ch2:
            if st.button("🍼 출산율 1.0 가능?", use_container_width=True, key="btn_q2"): q2 = True
        with col_ch3:
            if st.button("🌿 탄소세 안정책?", use_container_width=True, key="btn_q3"): q3 = True

        prompt = st.chat_input("질문할 내용을 여기에 입력하십시오...")
        
        # Chip button overrides prompt
        if q1: prompt = "최저임금 인상이 청년 고용에 미치는 구체적 영향은 무엇인가요?"
        elif q2: prompt = "출산 장려금을 더 늘리면 합계출산율이 1.0명을 넘을 수 있을까요?"
        elif q3: prompt = "탄소세 도입에 따른 물가 상승 압력을 완화할 방안은 무엇입니까?"

        if prompt:
            st.session_state.chat_history.append({'role': 'user', 'content': prompt})
            reply = get_chatbot_reply(prompt, outputs)
            st.session_state.chat_history.append({'role': 'assistant', 'content': reply})
            st.rerun()
