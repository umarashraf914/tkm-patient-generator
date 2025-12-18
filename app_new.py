"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - Main Streamlit Application
한의 임상 가상환자 시나리오 생성기

Updated UI with sidebar controls and main content area with collapsible sections.
═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import google.generativeai as genai

# Import from modular files
from config import API_KEY, init_session_state
from constants import (
    KCD_CODES, DISEASE_PATTERNS, FREQUENT_TKM_SYMPTOMS, FREQUENT_COMORBIDITIES,
    PAST_COLD_PROBLEM_AREAS, AGGRAVATING_FACTORS, RELIEVING_FACTORS,
    COLD_CHIEF_TYPES, COLD_EXAM_OPTIONS,
    get_pattern_info, get_kcd_info, get_all_symptom_options
)
from constraint_rules import apply_constraint_rules, apply_symptom_correlation_rules
from symptom_correlations import get_correlation_summary, validate_correlation_consistency
from randomizer import randomize_inputs
from patient_generator import generate_patient

# --- API KEY CONFIGURATION ---
if API_KEY == "PASTE_YOUR_API_KEY_HERE" or not API_KEY:
    st.error("⚠️ Please open config.py and paste your API Key!")
else:
    genai.configure(api_key=API_KEY)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="TKM Clinical Scenario Generator", layout="wide")

# --- INITIALIZE SESSION STATE ---
init_session_state(st)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Controls (조작)")
    
    # Randomize Button
    if st.button("🎲 Randomize (랜덤 생성)", use_container_width=True, type="primary"):
        randomize_inputs(st)
        st.rerun()
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DIAGNOSIS SECTION IN SIDEBAR
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### 📋 Diagnosis (진단명)")
    
    # Disease Selection
    st.markdown("**Disease (질환명)**")
    disease_opts = [
        "Common Cold (감기/급성상기도감염)", 
        "Allergic Rhinitis (알레르기비염)", 
        "Back Pain (요통)", 
        "Functional Dyspepsia (기능성소화불량)"
    ]
    st.selectbox("Disease", disease_opts, key="disease", label_visibility="collapsed")
    
    # Pattern Selection based on disease
    disease_key = None
    if "Cold" in st.session_state.disease:
        disease_key = "감기"
    elif "Rhinitis" in st.session_state.disease:
        disease_key = "알레르기비염"
    elif "Back Pain" in st.session_state.disease:
        disease_key = "요통"
    elif "Dyspepsia" in st.session_state.disease:
        disease_key = "기능성소화불량"

    if disease_key and disease_key in DISEASE_PATTERNS:
        patterns = DISEASE_PATTERNS[disease_key]["patterns"]
        pattern_display = [f"{p['name']} → {', '.join(p['prescriptions'])}" for p in patterns]
        
        if st.session_state.pattern_idx >= len(pattern_display):
            st.session_state.pattern_idx = 0
        
        st.markdown("**Pattern/Prescription (변증/처방)**")
        selected_pattern = st.selectbox(
            "Pattern", 
            pattern_display, 
            index=st.session_state.pattern_idx,
            label_visibility="collapsed"
        )
        st.session_state.pattern_idx = pattern_display.index(selected_pattern)
        
        # Display KCD code info
        kcd_info = get_kcd_info(disease_key)
        if kcd_info:
            st.caption(f"📋 KCD (한국표준질병사인분류): {kcd_info['main_code']}")
            with st.expander("KCD Details (KCD 상세정보 - Page 21-22)"):
                st.markdown(f"**Main Code:** {kcd_info['main_code']}")
                st.markdown("**Included:**")
                for code, desc in kcd_info['sub_codes'].items():
                    st.markdown(f"- {code}: {desc}")
                st.markdown("**Excluded:**")
                for excl in kcd_info['exclusions']:
                    st.markdown(f"- ❌ {excl}")
    


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT AREA
# ═══════════════════════════════════════════════════════════════════════════════

st.title("📋 TKM Clinical Scenario Generator (한의 임상시나리오 생성기)")
st.caption("한의 임상정보 항목 기반 가상환자 생성 시스템 · Pages 15-19, 21-23 Compliant")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Demographics & Vitals
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Demographics & Vitals (인구학적정보 및 활력징후) - KTAS Safety Enforced", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.number_input("Age (나이)", 1, 100, key="age")
        st.selectbox("Sex (성별)", ["Male (남)", "Female (여)"], key="sex")
        st.selectbox("Job (직업)", ["Student (학생)", "Office (사무직)", "Labor (현장직)", "Housewife (가사)"], key="job")
    with c2:
        st.number_input("SBP (수축기혈압 mmHg)", 90, 180, key="sbp")
        st.number_input("Pulse (맥박 회/분)", 50, 130, key="pulse_rate")
        st.number_input("Temp (체온 °C)", 35.0, 40.5, step=0.1, key="temp")
    with c3:
        st.selectbox("Onset (발현시점)", ["1 day ago (1일 전)", "2-3 days ago (2-3일 전)", "1 week ago (1주 전)", "Chronic >3mo (만성 3개월 이상)"], key="onset")
        st.selectbox("Course (경과)", ["Worsening (악화중)", "Improving (호전중)", "Fluctuating (비슷/오르내림)"], key="course")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Medical History & Lifestyle
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Medical History & Lifestyle (병력 및 생활습관)", expanded=False):
    h1, h2 = st.columns(2)
    with h1:
        st.multiselect("현병력 (Current Medical History)", ["고혈압", "당뇨", "이상지질혈증", "기타"], key="history_conditions")
        st.multiselect("약물력 (Medications)", ["혈압약", "당뇨약", "이상지질혈증약", "수면제", "항우울제", "항불안제"], key="meds_specific")
        st.multiselect("가족력 (Family History)", ["고혈압", "당뇨", "이상지질혈증", "심장병", "중풍", "기타"], key="family_hx")
    with h2:
        st.selectbox("음주 (Alcohol)", ["None (비음주)", "Week (주간)", "Daily (매일)"], key="social_alcohol_freq")
        st.number_input("흡연 (개피/일)", 0.0, 50.0, key="social_smoke_daily")
        st.selectbox("운동강도 (Exercise)", ["Low (저)", "Medium (중)", "High (고)"], key="social_exercise_int")

    if st.session_state.sex == "Female (여)":
        st.markdown("**Women's Health (여성력)**")
        if st.session_state.mens_duration < 1:
            st.session_state.mens_duration = 5
        if st.session_state.mens_cycle < 1:
            st.session_state.mens_cycle = 28
        w1, w2, w3, w4 = st.columns(4)
        with w1: st.selectbox("Cycle (생리규칙성)", ["Regular (규칙)", "Irregular (불규칙)", "Menopause (폐경)"], key="mens_regular")
        with w2: st.number_input("Duration (생리기간 일)", 1, 10, key="mens_duration")
        with w3: st.slider("Pain Score (생리통 0-10)", 0, 10, key="mens_pain_score")
        with w4: st.selectbox("Color (생리혈 색)", ["Pale (연함)", "Red (적색)", "Dark (흑자색)"], key="mens_color")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Excretion & Diet
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Excretion & Diet (배설 및 식사)", expanded=False):
    d1, d2, d3 = st.columns(3)
    with d1:
        st.number_input("Urine Day (주간뇨 횟수)", 1, 15, key="urine_freq_day")
        st.selectbox("Urine Color (소변 색)", ["Clear (맑음)", "Yellow (황색)", "Reddish (적색/혈뇨)"], key="urine_color")
    with d2:
        st.selectbox("Stool Freq (대변 횟수)", ["1/day (1회/일)", "2-3/day (2-3회/일)", "Constipation (변비)"], key="stool_freq")
        st.selectbox("Stool Color (대변 색)", ["Yellow (황색)", "Brown (황갈색)", "Black (흑색)", "Green (녹색)"], key="stool_color")
        st.selectbox("Form (대변 굵기/형태)", ["Normal (보통)", "Loose (묽음/연변)", "Hard (굳음/경변)"], key="stool_form")
    with d3:
        st.selectbox("Meal Freq (식사횟수/일)", [1, 2, 3, 4], key="diet_freq")
        st.selectbox("Regularity (식사규칙성)", ["Regular (규칙적)", "Irregular (불규칙)"], key="diet_regular")
        st.selectbox("Water Intake (음수량)", ["<0.5L (0.5L 미만)", "0.5-1L", "1-2L", ">2L (2L 이상)"], key="water_intake")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Sleep, Sweat, Cold/Heat
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Sleep, Sweat, Cold/Heat (수면, 땀, 한열경향)", expanded=False):
    s1, s2, s3 = st.columns(3)
    with s1:
        st.selectbox("Waking State (기상시 상쾌도)", ["Refreshed (개운함)", "Tired (피곤함)", "Heavy (무거움)"], key="sleep_waking_state")
        st.selectbox("Sleep Depth (수면 깊이)", ["Deep (깊음)", "Shallow/Light (얕음)"], key="sleep_depth")
        st.checkbox("Insomnia - Onset (입면장애)", key="insomnia_onset")
    with s2:
        st.selectbox("Sweat Area (땀나는 부위)", ["General (전신)", "Head (두부)", "Night (야간/도한)"], key="sweat_area")
        st.selectbox("Sweat Feel (땀 후 느낌)", ["Refreshed (상쾌)", "Tired/Cold (피곤/냉함)", "Hot (열감)"], key="sweat_feeling")
    with s3:
        st.selectbox("Temp Pref (한열경향)", ["Cold Sens (오한/추위탐)", "Balanced (보통)", "Heat Sens (열감/더위탐)"], key="cold_heat_pref")
        st.selectbox("Drink Temp (음료온도 선호)", ["Icy (냉수)", "Warm (온수)", "Hot (열수)"], key="drink_temp")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Mental State & Physical Inspection
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Mental State & Physical Inspection (정신상태 및 신체검진)", expanded=False):
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Mental State (정신상태)**")
        st.selectbox("Memory (기억력)", ["Good (좋음)", "Forgetful (건망)", "Bad (나쁨)"], key="memory")
        st.selectbox("Motivation (의욕)", ["High (높음)", "Normal (보통)", "Low (낮음)", "Apathetic (무기력)"], key="motivation")
        st.selectbox("Stress Coping (스트레스 대처력)", ["Good (좋음)", "Average (보통)", "Poor (나쁨)"], key="stress_coping")
    with m2:
        st.markdown("**Physical Inspection (신체검진)**")
        st.selectbox("Edema (부종)", ["None (없음)", "Face (안면)", "Legs (하지)", "General (전신)"], key="edema")
        st.selectbox("Bruising (멍듦)", ["Normal (정상)", "Easy (잘듦)", "Spontaneous (절로 생김)"], key="bruising")
        c_a, c_b = st.columns(2)
        with c_a: st.checkbox("Limb Weakness (사지무력감)", key="limb_weakness")
        with c_b: st.checkbox("Vision Blackout (눈앞캄캄함)", key="vision_blackout")
        st.markdown("---")
        st.selectbox("Skin Dryness (피부 건조도)", ["Normal (정상)", "Dry (건조)", "Scaly (각질)"], key="skin_dry")
        st.checkbox("Skin Itch (피부 가려움)", key="skin_itch")
        st.slider("Tinnitus Severity (이명 강도)", 0, 5, key="tinnitus_sev", help="0=없음, 1-2=경미, 3-4=중등도, 5=심함")
        st.slider("Hearing Issue Severity (난청/이롱 강도)", 0, 5, key="hearing_sev", help="0=없음, 1-2=경미, 3-4=중등도, 5=심함")
        st.slider("Dizziness Severity (어지러움/두훈 강도)", 0, 5, key="dizziness_sev", help="0=없음, 1-2=경미, 3-4=중등도, 5=심함")
        st.selectbox("Face Color (면색/얼굴 색)", ["Normal (정상)", "Pale (창백)", "Red (홍조)", "Yellow (황달)", "Dark (암색)"], key="face_color")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Pulse & Tongue Diagnosis
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Pulse & Tongue Diagnosis (맥진 및 설진)", expanded=False):
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("**Pulse (맥진)**")
        st.selectbox("Pulse Depth (맥 부침)", ["Floating (부맥)", "Middle (중맥)", "Sinking (침맥)"], key="pulse_depth")
        st.selectbox("Pulse Width (맥 대세/폭)", ["Thin (세맥)", "Medium (대맥)", "Wide (홍맥)"], key="pulse_width")
        st.selectbox("Pulse Strength (맥 유력/무력)", ["Weak (무력)", "Moderate (유력)", "Strong (강력)"], key="pulse_strength")
        st.selectbox("Pulse Smooth (맥 활삽)", ["Smooth (활맥)", "Normal (완맥)", "Rough (삽맥)"], key="pulse_smooth")
    with p2:
        st.markdown("**Tongue (설진)**")
        st.selectbox("Tongue Color (설질 색)", ["Pale (담백)", "Pale Red (담홍)", "Red (홍설)", "Dark Red (강홍/자설)"], key="tongue_color")
        st.selectbox("Coat Color (설태 색)", ["White (백태)", "Yellow (황태)", "Grey (회태)"], key="tongue_coat_color")
        st.selectbox("Coat Thickness (설태 두께)", ["Thin (박태)", "Thick (후태)", "Greasy (니태)"], key="tongue_coat_thick")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: ROS Pain Grid
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ ROS Pain Grid (통증 부위별 Review of Systems)", expanded=False):
    st.caption("Freq (빈도 0-5) / Int (강도 0-10)")
    cols = st.columns(3)
    parts = [("Neck (경항부)", "pain_neck"), ("Back (요배부)", "pain_back"), ("Knee (슬부)", "pain_knee"), ("Shldr (견부)", "pain_shoulder"), ("Elbow (주관절)", "pain_elbow"), ("Hand (수부)", "pain_hand")]
    for l, k in parts:
        with cols[0]: st.text(l)
        with cols[1]: st.number_input(f"{l} F (빈도)", 0, 5, key=f"{k}_f", label_visibility="collapsed")
        with cols[2]: st.number_input(f"{l} I (강도)", 0, 10, key=f"{k}_i", label_visibility="collapsed")
        st.session_state[k] = [st.session_state[f"{k}_f"], st.session_state[f"{k}_i"]]
    st.checkbox("Cold Hands/Feet (수족냉증)", key="cold_hands_feet")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Chief Complaint Specifics
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("### 8. Chief Complaint Specifics (주소증 상세 - 변증지표)")
st.caption("감기환자 변증지표 (Page 15 - 임상진료지침 기준)")

# Disease-specific symptom inputs
if "Cold" in st.session_state.disease:
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Fever Level (발열 강도: 1-5)", 1, 5, key="fever_sev", help="1=미열/무열, 5=고열 壯熱")
        st.slider("Chills Level (오한 강도: 1-5)", 1, 5, key="chills_sev", help="1=경미, 5=惡寒重")
    with c2:
        st.slider("Runny Nose (콧물 양: 1-5)", 1, 5, key="snot_sev", help="1=경미, 5=콧물 줄줄")
        st.slider("Cough (기침 강도: 1-5)", 1, 5, key="cough_sev", help="1=경미, 5=기침 심함")
    
    cold_opts = ["무한 (無汗) - 풍한", "황담 (黃痰) - 풍열", "희박담 (稀薄白痰) - 풍한", "인후건조 (咽乾) - 풍조", "골절동통 (骨節疼痛) - 풍한", "객담소 (咳嗽少痰) - 풍조"]
    st.multiselect("Cold Symptoms (감기 증상 - Page 15)", cold_opts, key="cold_symptoms_spec")
    
    with st.expander("📋 Page 39-40: 감기 가상환자 주증정보 필수항목", expanded=False):
        st.multiselect("감기주소증 유형 (최소 1개 이상)", COLD_CHIEF_TYPES, key="cold_chief_type")
        
        onset_opts = ["1일 전", "2일 전", "3일 전", "4일 전", "5일 전", "1주일 전", "2주일 전", "3주일 전"]
        st.selectbox("발병일 (O/S 구체적)", onset_opts, key="cold_onset_specific")
        
        cold_col1, cold_col2, cold_col3 = st.columns(3)
        with cold_col1:
            st.checkbox("인후통 (Sore throat)", key="sore_throat")
            st.checkbox("몸살 (Body ache)", key="body_ache_cold")
            st.checkbox("신중/몸 무거움 (Body heaviness)", key="body_heaviness_cold")
        with cold_col2:
            st.checkbox("두통 (Headache)", key="headache_cold")
            st.checkbox("경항통 (Neck pain)", key="neck_pain_cold")
            st.checkbox("숨이 가쁨 (Dyspnea)", key="cold_dyspnea")
        with cold_col3:
            st.checkbox("땀 유무 (Sweating check)", key="cold_sweating_check")
            st.slider("후각감퇴 (Smell reduction 0-5)", 0, 5, key="smell_reduction")
        
        st.slider("가래 양 (Phlegm amount 0-5)", 0, 5, key="phlegm_amt")
        if st.session_state.get("phlegm_amt", 0) >= 2:
            st.selectbox("가래 색 (Phlegm color)", ["Clear (맑음)", "White (백색)", "Yellow (황색)", "Green (녹색)"], key="phlegm_color")
        
        if st.session_state.get("snot_sev", 1) >= 2:
            st.selectbox("콧물 색 (Snot color)", ["None", "Clear (맑음/투명)", "White (백색)", "Yellow (황색)", "Green (녹색)"], key="snot_color")
        
        st.slider("한열왕래 (Alternating chills-fever 0-5)", 0, 5, key="alternating_chills_fever")
        
        st.markdown("**진찰 및 검사소견 (Page 40)**")
        exam_col1, exam_col2 = st.columns(2)
        with exam_col1:
            st.selectbox("청진기 호흡음 (Stethoscope)", COLD_EXAM_OPTIONS["stethoscope"], key="exam_stethoscope")
            st.selectbox("인후부 망진/촉진", COLD_EXAM_OPTIONS["throat_visual"], key="exam_throat_visual")
        with exam_col2:
            st.selectbox("설압자 편도 소견", COLD_EXAM_OPTIONS["tongue_depressor"], key="exam_tongue_depressor")
            st.selectbox("비경 소견", COLD_EXAM_OPTIONS["rhinoscope"], key="exam_rhinoscope_finding")

elif "Rhinitis" in st.session_state.disease:
    st.caption("알레르기비염 변증지표 (Page 23 - 수체형)")
    r1, r2 = st.columns(2)
    with r1:
        st.slider("재채기 (嚏噴 1-5)", 1, 5, key="sneeze_sev")
        st.slider("코막힘 (鼻塞 1-5)", 1, 5, key="nose_block_sev")
    with r2:
        st.slider("코가려움 (鼻癢 1-5)", 1, 5, key="nose_itch_sev")
        st.slider("콧물 양 (鼻涕 1-5)", 1, 5, key="snot_sev")
    st.selectbox("콧물 성상 (Snot Type)", ["청수양 (淸水樣) - 맑은 콧물", "백점액 (白粘) - 희고 끈적", "황농성 (黃膿) - 누렇고 찐득"], key="snot_type")

elif "Dyspepsia" in st.session_state.disease:
    st.caption("기능성소화불량 변증지표 (Pages 16-17 - 한열허실 팔강변증)")
    st.slider("복만/복통 강도 (1-5)", 1, 5, key="pain_sev")
    dys_opts = ["신물 (吞酸) - 간위불화/식적", "트림 (噯氣) - 기체/식적", "구역/구토 (惡心嘔吐) - 습열", "구고 (口苦) - 열증/습열", "부패취 (噯氣腐臭) - 식적", "수족냉증 (四肢厥冷) - 한증/허증", "식후복만 (食後腹脹) - 비위허약", "사지권태 (四肢倦怠) - 기허"]
    st.multiselect("소화불량 증상 (Page 16/17)", dys_opts, key="dyspepsia_spec")

elif "Back Pain" in st.session_state.disease:
    st.caption("요통 변증지표 (Pages 15-16 - 한열허실 팔강변증)")
    st.slider("통증 강도 (NRS 1-10)", 1, 10, key="pain_sev", help="1=경미, 10=극심 (KTAS: 7 이하 권장)")
    pain_opts = ["유주통 (遊走痛) - 풍/담음", "자통 (刺痛) - 어혈", "한통 (寒痛) - 한", "득온즉감 (得溫則減) - 한", "야간통 (夜甚) - 어혈", "중통 (重痛) - 습", "구립즉심 (久立則甚) - 기", "신허요통 (腎虛腰痛) - 신허"]
    st.multiselect("통증 양상 (Page 15/16)", pain_opts, key="pain_nature")

# ═══════════════════════════════════════════════════════════════════════════════
# Additional Symptoms & Correlations (Collapsed by default)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➤ Additional Symptoms & Comorbidities (추가 증상 및 동반질환 - Pages 24-25)", expanded=False):
    st.caption("한의원 다빈도 증상 중 무작위 1-2개가 현실성을 위해 추가됩니다.")
    col_add1, col_add2 = st.columns(2)
    with col_add1:
        st.multiselect("추가 증상 (Additional Symptoms)", get_all_symptom_options(), key="additional_symptoms")
    with col_add2:
        st.multiselect("추가 동반질환 (Additional Comorbidities)", FREQUENT_COMORBIDITIES, key="additional_comorbidities")

with st.expander("➤ 📊 Symptom Correlations (증상간 상관관계 - Pages 36-38)", expanded=False):
    st.caption("**400명 임상한의사 차트리뷰 결과에 기반한 증상간 상관관계 규칙**")
    
    correlation_summary = get_correlation_summary()
    
    col_pos, col_neg = st.columns(2)
    with col_pos:
        st.markdown("**✅ Positive Correlations (양의 상관관계)**")
        for rule in correlation_summary["positive_correlations"]:
            st.markdown(f"- {rule}")
    
    with col_neg:
        st.markdown("**❌ Negative Correlations (음의 상관관계 - 배제규칙)**")
        for rule in correlation_summary["negative_correlations"]:
            st.markdown(f"- {rule}")
    
    st.caption(f"*출처: {correlation_summary['source']}*")
    
    # Validate current patient for correlation consistency
    validation_issues = validate_correlation_consistency(st.session_state)
    if validation_issues:
        st.warning("⚠️ **상관관계 검증 경고:**")
        for issue in validation_issues:
            st.markdown(f"- {issue}")
    else:
        st.success("✅ 현재 환자 데이터가 상관관계 규칙과 일치합니다.")

# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE BUTTON (at the end of main content)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
if st.button("✨ 가상환자 시나리오 생성", type="primary", use_container_width=True):
    generate_patient(st, genai)
