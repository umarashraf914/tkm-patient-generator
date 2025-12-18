"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - Randomization Functions
═══════════════════════════════════════════════════════════════════════════════
"""

import random
from data_mappings import get_weights
from constants import (
    DISEASE_PATTERNS, PAST_COLD_PROBLEM_AREAS, AGGRAVATING_FACTORS,
    RELIEVING_FACTORS
)
from constraint_rules import apply_constraint_rules, apply_symptom_correlation_rules

# Import CSV-based generation rules
try:
    from generation_rules import (
        load_rules, 
        generate_patient_from_rules,
        get_patterns_for_disease,
        CSV_PATHS
    )
    CSV_RULES_AVAILABLE = True
except ImportError:
    CSV_RULES_AVAILABLE = False
    print("Warning: generation_rules module not available, using fallback randomization")


# ============================================================================
# CSV-BASED RANDOMIZATION (NEW)
# ============================================================================

def randomize_from_csv_rules(st, disease_name: str, pattern: str = None):
    """
    Randomize patient inputs using CSV-based generation rules.
    
    Args:
        st: Streamlit module with session_state
        disease_name: Disease name in Korean (감기 or 알레르기비염)
        pattern: Optional pattern name for pattern-specific probabilities
    
    Returns:
        True if successful, False if fallback is needed
    """
    if not CSV_RULES_AVAILABLE:
        return False
    
    try:
        # Generate patient data from CSV rules
        patient_data = generate_patient_from_rules(disease_name, pattern)
        
        if not patient_data:
            return False
        
        session = st.session_state
        
        # Map CSV symptom keys to session state variables
        # This mapping converts CSV rule outputs to the expected session state format
        
        # Demographics
        if "인구학적 정보__성별" in patient_data:
            opt = patient_data["인구학적 정보__성별"]["option_number"]
            session.sex = "Male (남)" if opt == 1 else "Female (여)"
        
        if "인구학적 정보__나이" in patient_data:
            opt = patient_data["인구학적 정보__나이"]["option_number"]
            # Map age category to actual age range
            age_ranges = {1: (10, 19), 2: (20, 39), 3: (40, 54), 4: (55, 69), 5: (70, 85)}
            age_range = age_ranges.get(opt, (20, 80))
            session.age = random.randint(age_range[0], age_range[1])
        
        if "인구학적 정보__직업" in patient_data:
            opt = patient_data["인구학적 정보__직업"]["option_number"]
            job_map = {
                1: "Manager (관리직)", 2: "Professional (전문직)", 
                3: "Office (사무직)", 4: "Service (서비스직)",
                5: "Sales (판매직)", 6: "Agriculture (농/어업)",
                7: "Technical (기능직)", 8: "Operator (조립직)",
                9: "Labor (단순노무)", 10: "Military (군인)",
                11: "Other (기타)"
            }
            session.job = job_map.get(opt, "Other (기타)")
        
        # Height/Weight from category
        if "인구학적 정보__키" in patient_data:
            opt = patient_data["인구학적 정보__키"]["option_number"]
            # Map to approximate height ranges
            height_ranges = {1: (150, 155), 2: (156, 162), 3: (163, 178), 4: (179, 186), 5: (187, 195)}
            h_range = height_ranges.get(opt, (160, 180))
            session.height = random.randint(h_range[0], h_range[1])
        
        if "인구학적 정보__몸무게" in patient_data:
            opt = patient_data["인구학적 정보__몸무게"]["option_number"]
            weight_ranges = {1: (45, 55), 2: (56, 63), 3: (64, 76), 4: (77, 85), 5: (86, 100)}
            w_range = weight_ranges.get(opt, (55, 85))
            session.weight = random.randint(w_range[0], w_range[1])
        
        # Vitals
        if "활력징후__체온" in patient_data:
            opt = patient_data["활력징후__체온"]["option_number"]
            temp_ranges = {1: (34.5, 35.5), 2: (36.0, 37.3), 3: (37.4, 37.9), 4: (38.0, 39.9), 5: (40.0, 41.0)}
            t_range = temp_ranges.get(opt, (36.0, 37.5))
            session.temp = round(random.uniform(t_range[0], t_range[1]), 1)
        
        if "활력징후__맥박" in patient_data:
            opt = patient_data["활력징후__맥박"]["option_number"]
            pulse_ranges = {1: (45, 50), 2: (50, 60), 3: (60, 80), 4: (80, 100), 5: (100, 120)}
            p_range = pulse_ranges.get(opt, (60, 90))
            session.pulse_rate = random.randint(p_range[0], p_range[1])
        
        if "활력징후__호흡" in patient_data:
            opt = patient_data["활력징후__호흡"]["option_number"]
            resp_ranges = {1: (8, 12), 2: (12, 20), 3: (21, 28)}
            r_range = resp_ranges.get(opt, (12, 20))
            session.resp = random.randint(r_range[0], r_range[1])
        
        if "활력징후__혈압" in patient_data:
            opt = patient_data["활력징후__혈압"]["option_number"]
            bp_ranges = {
                1: ((80, 90), (50, 60)),      # 저혈압
                2: ((100, 119), (60, 79)),    # 정상
                3: ((120, 139), (80, 89)),    # 고혈압전단계
                4: ((140, 159), (90, 99)),    # 고혈압1기
                5: ((160, 179), (100, 109))   # 고혈압2기
            }
            sbp_range, dbp_range = bp_ranges.get(opt, ((100, 140), (60, 90)))
            session.sbp = random.randint(sbp_range[0], sbp_range[1])
            session.dbp = random.randint(dbp_range[0], dbp_range[1])
        
        # Cold-specific symptoms
        if disease_name == "감기":
            _apply_cold_symptoms(session, patient_data)
        elif disease_name == "알레르기비염":
            _apply_rhinitis_symptoms(session, patient_data)
        
        # Common symptoms (diet, stool, urine, sleep, etc.)
        _apply_common_symptoms(session, patient_data)
        
        return True
        
    except Exception as e:
        print(f"Error in CSV-based randomization: {e}")
        import traceback
        traceback.print_exc()
        return False


def _apply_cold_symptoms(session, patient_data):
    """Apply cold-specific symptoms from CSV data."""
    
    # Onset
    if "감기환자_O/S_감기증상 발현시점" in patient_data:
        opt = patient_data["감기환자_O/S_감기증상 발현시점"]["option_number"]
        onset_map = {
            1: "1 day ago (1일 전)", 
            2: "2-3 days ago (2-3일 전)", 
            3: "1 week ago (1주 전)",
            4: "2 weeks ago (2주 전)",
            5: "1 month ago (1개월 전)",
            6: "Chronic >3mo (만성 3개월 이상)"
        }
        session.onset = onset_map.get(opt, "2-3 days ago (2-3일 전)")
    
    # Fever severity - map to temp if not already set
    if "감기환자_감기주소증 유형_발열" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_발열"]["option_number"]
        # Store as severity level for UI display
        session.fever_sev = opt
    
    # Chills severity
    if "감기환자_감기주소증 유형_오한" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_오한"]["option_number"]
        session.chills_sev = opt
    
    # Nasal discharge amount
    if "감기환자_감기주소증 유형_콧물 감기" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_콧물 감기"]["option_number"]
        session.snot_sev = opt
    
    # Nasal discharge color
    if "감기환자_감기주소증 유형_콧물 색" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_콧물 색"]["option_number"]
        session.snot_color = opt
    
    # Nasal congestion
    if "감기환자_감기주소증 유형_코막힘" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_코막힘"]["option_number"]
        session.nasal_congestion = opt
    
    # Sore throat
    if "감기환자_감기주소증 유형_인후통" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_인후통"]["option_number"]
        session.sore_throat = opt
    
    # Sneezing
    if "감기환자_감기주소증 유형_재채기" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_재채기"]["option_number"]
        session.sneeze_sev = opt
    
    # Cough
    if "감기환자_감기주소증 유형_기침" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_기침"]["option_number"]
        session.cough_sev = opt
    
    # Phlegm amount
    if "감기환자_감기주소증 유형_담(가래) 양" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_담(가래) 양"]["option_number"]
        session.phlegm_amt = opt
    
    # Phlegm color
    if "감기환자_감기주소증 유형_담(가래) 색" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_담(가래) 색"]["option_number"]
        session.phlegm_color = opt
    
    # Body ache
    if "감기환자_감기주소증 유형_몸살, 신체통, 근육통" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_몸살, 신체통, 근육통"]["option_number"]
        session.body_ache = opt
    
    # Body heaviness
    if "감기환자_감기주소증 유형_신중(身重)" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_신중(身重)"]["option_number"]
        session.body_heavy = opt
    
    # Headache
    if "감기환자_감기주소증 유형_두부, 뒷목 불편감(강도)" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_두부, 뒷목 불편감(강도)"]["option_number"]
        session.headache = opt
    
    # Sweating during cold
    if "감기환자_감기주소증 유형_감기 시 땀 유무" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_감기 시 땀 유무"]["option_number"]
        session.sweat_during_cold = opt
        # Also set sweat amount based on this
        sweat_map = {1: "None (무한 無汗)", 2: "Normal (보통)", 3: "Normal (보통)", 4: "Excessive (다한 多汗)", 5: "Excessive (다한 多汗)"}
        session.sweat_amt = sweat_map.get(opt, "Normal (보통)")
    
    # Throat exam
    if "감기환자_한의사 진찰 및 검사소견_인후부 진찰" in patient_data:
        opt = patient_data["감기환자_한의사 진찰 및 검사소견_인후부 진찰"]["option_number"]
        session.throat_redness = opt
    
    # Tonsil exam
    if "감기환자_한의사 진찰 및 검사소견_편도진찰" in patient_data:
        opt = patient_data["감기환자_한의사 진찰 및 검사소견_편도진찰"]["option_number"]
        session.tonsil_swelling = opt


def _apply_rhinitis_symptoms(session, patient_data):
    """Apply allergic rhinitis-specific symptoms from CSV data."""
    
    # Onset
    if "알러지비염가상환자_O/S_알러지비염 발현시점" in patient_data:
        opt = patient_data["알러지비염가상환자_O/S_알러지비염 발현시점"]["option_number"]
        onset_map = {
            1: "1 week ago (1주 전)",
            2: "2-3 weeks ago (2-3주 전)", 
            3: "1 month ago (1개월 전)",
            4: "3 months ago (3개월 전)",
            5: "6 months ago (6개월 전)",
            6: "Chronic >1yr (만성 1년 이상)"
        }
        session.onset = onset_map.get(opt, "1 month ago (1개월 전)")
    
    # Nasal discharge amount
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_콧물 량" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_콧물 량"]["option_number"]
        session.snot_sev = opt
    
    # Nasal discharge color
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_콧물 색" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_콧물 색"]["option_number"]
        session.snot_color = opt
    
    # Nasal congestion
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_코막힘" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_코막힘"]["option_number"]
        session.nasal_congestion = opt
    
    # Sneezing intensity
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(정도)" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(정도)"]["option_number"]
        session.sneeze_intensity = opt
    
    # Sneezing frequency
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(빈도)" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(빈도)"]["option_number"]
        session.sneeze_sev = opt
    
    # Nose itching
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_코 가려움" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_코 가려움"]["option_number"]
        session.nose_itch = opt


def _apply_common_symptoms(session, patient_data):
    """Apply common symptoms that are shared across diseases."""
    
    # History conditions
    hx_conditions = []
    if "현병력__고혈압" in patient_data:
        if patient_data["현병력__고혈압"]["option_number"] == 2:
            hx_conditions.append("고혈압")
    if "현병력__당뇨" in patient_data:
        if patient_data["현병력__당뇨"]["option_number"] == 2:
            hx_conditions.append("당뇨")
    if "현병력__이상지질혈증" in patient_data:
        if patient_data["현병력__이상지질혈증"]["option_number"] == 2:
            hx_conditions.append("이상지질혈증")
    session.history_conditions = hx_conditions
    
    # Medications
    meds = []
    if "약물력__혈압약" in patient_data:
        if patient_data["약물력__혈압약"]["option_number"] == 2:
            meds.append("혈압약")
    if "약물력__당뇨약" in patient_data:
        if patient_data["약물력__당뇨약"]["option_number"] == 2:
            meds.append("당뇨약")
    if "약물력__이상지질혈증약" in patient_data:
        if patient_data["약물력__이상지질혈증약"]["option_number"] == 2:
            meds.append("이상지질혈증약")
    if "약물력__수면제" in patient_data:
        if patient_data["약물력__수면제"]["option_number"] == 2:
            meds.append("수면제")
    session.meds_specific = meds
    
    # Family history
    fam_hx = []
    if "가족력__고혈압" in patient_data:
        if patient_data["가족력__고혈압"]["option_number"] == 2:
            fam_hx.append("고혈압")
    if "가족력__당뇨" in patient_data:
        if patient_data["가족력__당뇨"]["option_number"] == 2:
            fam_hx.append("당뇨")
    if "가족력__심장병" in patient_data:
        if patient_data["가족력__심장병"]["option_number"] == 2:
            fam_hx.append("심장병")
    if "가족력__중풍" in patient_data:
        if patient_data["가족력__중풍"]["option_number"] == 2:
            fam_hx.append("중풍")
    session.family_hx = fam_hx
    
    # Alcohol - find correct key pattern
    for key in patient_data:
        if "월간 음주 횟수" in key:
            opt = patient_data[key]["option_number"]
            freq_map = {1: "None (비음주)", 2: "Occasional (가끔)", 3: "Week (주간)", 4: "Frequent (자주)", 5: "Daily (매일)"}
            session.social_alcohol_freq = freq_map.get(opt, "None (비음주)")
            break
    
    for key in patient_data:
        if "1회당 음주량" in key:
            opt = patient_data[key]["option_number"]
            # Map to approximate amount
            if session.social_alcohol_freq == "None (비음주)":
                session.social_alcohol_amt = 0.0
            else:
                amt_map = {1: 0.5, 2: 1.0, 3: 2.0, 4: 3.0, 5: 4.0}
                session.social_alcohol_amt = amt_map.get(opt, 1.0)
            break
    
    # Smoking
    for key in patient_data:
        if "일간 개피" in key:
            opt = patient_data[key]["option_number"]
            smoke_map = {1: 0.0, 2: 5.0, 3: 15.0, 4: 25.0, 5: 35.0}
            session.social_smoke_daily = smoke_map.get(opt, 0.0)
            break
    
    # Exercise
    for key in patient_data:
        if "운동 강도" in key:
            opt = patient_data[key]["option_number"]
            intensity_map = {1: "Low (저)", 2: "Low (저)", 3: "Medium (중)", 4: "High (고)", 5: "High (고)"}
            session.social_exercise_int = intensity_map.get(opt, "Medium (중)")
            break
    
    for key in patient_data:
        if "1회당 평균 운동 시간" in key:
            opt = patient_data[key]["option_number"]
            time_map = {1: 0, 2: 10, 3: 30, 4: 50, 5: 75}
            session.social_exercise_time = time_map.get(opt, 30)
            break
    
    # Diet
    for key in patient_data:
        if "1회 평균식사시간" in key:
            opt = patient_data[key]["option_number"]
            speed_map = {1: "Fast <10min (빠름)", 2: "Fast <10min (빠름)", 3: "Normal 20min (보통)", 4: "Slow >30min (느림)", 5: "Slow >30min (느림)"}
            session.diet_speed = speed_map.get(opt, "Normal 20min (보통)")
            break
    
    for key in patient_data:
        if "입맛" in key:
            opt = patient_data[key]["option_number"]
            appetite_map = {1: "None (없음)", 2: "Low (저하)", 3: "Normal (보통)", 4: "High (항진)", 5: "High (항진)"}
            session.appetite = appetite_map.get(opt, "Normal (보통)")
            break
    
    for key in patient_data:
        if "1일 식사횟수" in key:
            opt = patient_data[key]["option_number"]
            session.diet_freq = min(opt, 4)
            break
    
    for key in patient_data:
        if "식사 규칙성" in key:
            opt = patient_data[key]["option_number"]
            regular_map = {1: "Regular (규칙적)", 2: "Regular (규칙적)", 3: "Irregular (불규칙)", 4: "Irregular (불규칙)", 5: "Irregular (불규칙)"}
            session.diet_regular = regular_map.get(opt, "Regular (규칙적)")
            break
    
    # Stool
    for key in patient_data:
        if "대변 횟수" in key:
            opt = patient_data[key]["option_number"]
            freq_map = {1: "Constipation (변비)", 2: "Constipation (변비)", 3: "1/day (1회/일)", 4: "2-3/day (2-3회/일)", 5: "2-3/day (2-3회/일)"}
            session.stool_freq = freq_map.get(opt, "1/day (1회/일)")
            break
    
    for key in patient_data:
        if "대변 굳기" in key:
            opt = patient_data[key]["option_number"]
            form_map = {1: "Hard (굳음/경변)", 2: "Hard (굳음/경변)", 3: "Normal (보통)", 4: "Normal (보통)", 5: "Loose (묽음/연변)", 6: "Loose (묽음/연변)", 7: "Loose (묽음/연변)"}
            session.stool_form = form_map.get(opt, "Normal (보통)")
            break
    
    # Urine
    for key in patient_data:
        if "1일 소변 횟수" in key:
            opt = patient_data[key]["option_number"]
            urine_freq_map = {1: 2, 2: 4, 3: 6, 4: 9, 5: 12}
            session.urine_freq_day = urine_freq_map.get(opt, 6)
            break
    
    for key in patient_data:
        if "야간뇨 횟수" in key:
            opt = patient_data[key]["option_number"]
            night_map = {1: 0, 2: 1, 3: 2, 4: 3, 5: 5}
            session.urine_freq_night = night_map.get(opt, 0)
            break
    
    for key in patient_data:
        if "소변 굵기" in key:
            opt = patient_data[key]["option_number"]
            stream_map = {1: "Weak (약함)", 2: "Weak (약함)", 3: "Normal (정상)", 4: "Normal (정상)", 5: "Normal (정상)"}
            session.urine_stream = stream_map.get(opt, "Normal (정상)")
            break
    
    # Sleep
    for key in patient_data:
        if "수면 시간" in key:
            opt = patient_data[key]["option_number"]
            hours_map = {1: 3, 2: 5, 3: 7, 4: 10, 5: 12}
            session.sleep_hours = hours_map.get(opt, 7)
            break
    
    for key in patient_data:
        if "기상시 상쾌도" in key:
            opt = patient_data[key]["option_number"]
            waking_map = {1: "Heavy (무거움)", 2: "Tired (피곤함)", 3: "Tired (피곤함)", 4: "Refreshed (개운함)", 5: "Refreshed (개운함)"}
            session.sleep_waking_state = waking_map.get(opt, "Tired (피곤함)")
            break
    
    for key in patient_data:
        if "수면 깊이" in key:
            opt = patient_data[key]["option_number"]
            depth_map = {1: "Shallow/Light (얕음)", 2: "Shallow/Light (얕음)", 3: "Deep (깊음)", 4: "Deep (깊음)", 5: "Deep (깊음)"}
            session.sleep_depth = depth_map.get(opt, "Deep (깊음)")
            break
    
    for key in patient_data:
        if "불면 빈도" in key:
            opt = patient_data[key]["option_number"]
            # Set insomnia flags based on frequency
            session.insomnia_onset = opt >= 3
            session.insomnia_maintain = opt >= 4
            session.insomnia_reentry = opt >= 4
            break
    
    for key in patient_data:
        if "꿈의 빈도" in key:
            opt = patient_data[key]["option_number"]
            dreams_map = {1: "Rare (거의 없음)", 2: "Sometimes (가끔)", 3: "Frequent (자주)", 4: "Nightmares (악몽)", 5: "Nightmares (악몽)"}
            session.dreams = dreams_map.get(opt, "Sometimes (가끔)")
            break


# ============================================================================
# ORIGINAL RANDOMIZATION (Keep for fallback/other diseases)
# ============================================================================

def get_weighted_level(variable_key, pattern_key, levels=None):
    """
    Select a level (1-5) based on weighted probabilities from CLINICAL_DATA.
    
    Args:
        variable_key: The variable name in CLINICAL_DATA (e.g., 'fever_sev')
        pattern_key: The pattern identifier (e.g., 'Cold_WC', 'R_Minor')
        levels: Optional list of levels to choose from (default: [1,2,3,4,5])
    
    Returns:
        A single level value selected based on probability weights
    """
    if levels is None:
        levels = [1, 2, 3, 4, 5]
    
    weights = []
    for lvl in levels:
        w_dict = get_weights(variable_key, lvl)
        # Get weight for specific pattern, default to 0.1 for uniform fallback
        weights.append(w_dict.get(pattern_key, 0.1))
    
    # Ensure at least some weight exists to avoid error
    if sum(weights) == 0:
        weights = [1] * len(levels)  # Uniform fallback
    
    return random.choices(levels, weights=weights, k=1)[0]


def randomize_inputs(st):
    """Randomize all patient input fields."""
    session = st.session_state
    
    # ===========================================
    # 1. DEMOGRAPHICS (인구학적정보)
    # ===========================================
    session.age = random.randint(20, 80)
    session.sex = random.choice(["Male (남)", "Female (여)"])
    session.job = random.choice(["Student (학생)", "Office (사무직)", "Labor (현장직)", "Housewife (가사)"])
    session.height = random.randint(150, 190)
    session.weight = random.randint(45, 100)
    
    # ===========================================
    # 2. VITALS (SAFETY RULES - Keep within safe clinical ranges)
    # ===========================================
    session.sbp = random.randint(95, 170)
    session.dbp = random.randint(60, 100)
    if session.dbp >= session.sbp:
        session.dbp = session.sbp - random.randint(20, 40)
    session.pulse_rate = random.randint(55, 120)
    session.temp = round(random.uniform(36.0, 40.0), 1)
    session.resp = random.randint(12, 24)
    
    # ===========================================
    # 3. HISTORY & ONSET (병력 및 경과)
    # ===========================================
    session.onset = random.choice(["1 day ago (1일 전)", "2-3 days ago (2-3일 전)", "1 week ago (1주 전)", "Chronic >3mo (만성 3개월 이상)"])
    session.course = random.choice(["Worsening (악화중)", "Improving (호전중)", "Fluctuating (비슷/오르내림)"])
    session.history_conditions = random.sample(["고혈압", "당뇨", "이상지질혈증", "기타"], k=random.randint(0, 2))
    session.meds_specific = random.sample(["혈압약", "당뇨약", "이상지질혈증약", "수면제", "항우울제", "항불안제"], k=random.randint(0, 3))
    session.family_hx = random.sample(["고혈압", "당뇨", "이상지질혈증", "심장병", "중풍", "기타"], k=random.randint(0, 2))
    session.past_cold_problem_area = random.sample(PAST_COLD_PROBLEM_AREAS, k=random.randint(0, 2))
    session.aggravating_factors = random.sample(AGGRAVATING_FACTORS, k=random.randint(0, 3))
    session.relieving_factors = random.sample(RELIEVING_FACTORS, k=random.randint(0, 2))
    
    # Social History (사회력)
    session.social_alcohol_freq = random.choice(["None (비음주)", "Week (주간)", "Daily (매일)"])
    session.social_alcohol_amt = round(random.uniform(0, 5), 1) if session.social_alcohol_freq != "None (비음주)" else 0.0
    session.social_smoke_daily = round(random.uniform(0, 20), 1)
    session.social_exercise_int = random.choice(["Low (저)", "Medium (중)", "High (고)"])
    session.social_exercise_time = random.randint(0, 120)
    
    # ===========================================
    # 4. WOMEN'S HEALTH (여성력)
    # ===========================================
    if session.sex == "Female (여)":
        session.mens_cycle = random.randint(21, 35)
        session.mens_regular = random.choice(["Regular (규칙)", "Irregular (불규칙)", "Menopause (폐경)"])
        session.mens_amt = random.choice(["Light (적음)", "Normal (보통)", "Heavy (많음)"])
        session.mens_clot = random.choice([True, False])
        session.mens_color = random.choice(["Pale (연함)", "Red (적색)", "Dark (흑자색)"])
        session.mens_duration = random.randint(3, 7)
        session.mens_pain_score = random.randint(0, 10)
    
    # ===========================================
    # 5. EXCRETION & DIET (배설 및 식사)
    # ===========================================
    session.diet_speed = random.choice(["Fast <10min (빠름)", "Normal 20min (보통)", "Slow >30min (느림)"])
    session.appetite = random.choice(["None (없음)", "Low (저하)", "Normal (보통)", "High (항진)"])
    session.diet_freq = random.choice([1, 2, 3, 4])
    session.diet_regular = random.choice(["Regular (규칙적)", "Irregular (불규칙)"])
    session.water_intake = random.choice(["<0.5L (0.5L 미만)", "0.5-1L", "1-2L", ">2L (2L 이상)"])
    
    session.stool_freq = random.choice(["1/day (1회/일)", "2-3/day (2-3회/일)", "Constipation (변비)"])
    session.stool_form = random.choice(["Normal (보통)", "Loose (묽음/연변)", "Hard (굳음/경변)"])
    session.stool_discomfort = random.choice([True, False])
    session.stool_color = random.choice(["Yellow (황색)", "Brown (황갈색)", "Black (흑색)", "Green (녹색)"])
    
    session.urine_freq_day = random.randint(3, 12)
    session.urine_freq_night = random.randint(0, 4)
    session.urine_stream = random.choice(["Normal (정상)", "Weak (약함)", "Intermittent (끊김)"])
    session.urine_residual = random.choice([True, False])
    session.urine_incontinence = random.choice([True, False])
    session.urine_color = random.choice(["Clear (맑음)", "Yellow (황색)", "Reddish (적색/혈뇨)"])
    
    # ===========================================
    # 6. SLEEP, SWEAT, COLD/HEAT (수면, 땀, 한열)
    # ===========================================
    session.sleep_hours = random.randint(4, 10)
    session.sleep_waking_state = random.choice(["Refreshed (개운함)", "Tired (피곤함)", "Heavy (무거움)"])
    session.sleep_depth = random.choice(["Deep (깊음)", "Shallow/Light (얕음)"])
    session.insomnia_onset = random.choice([True, False])
    session.insomnia_maintain = random.choice([True, False])
    session.insomnia_reentry = random.choice([True, False])
    session.dreams = random.choice(["Rare (거의 없음)", "Sometimes (가끔)", "Frequent (자주)", "Nightmares (악몽)"])
    
    session.sweat_amt = random.choice(["None (무한 無汗)", "Normal (보통)", "Excessive (다한 多汗)"])
    session.sweat_area = random.choice(["General (전신)", "Head (두부)", "Night (야간/도한)"])
    session.sweat_feeling = random.choice(["Refreshed (상쾌)", "Tired/Cold (피곤/냉함)", "Hot (열감)"])
    
    session.cold_heat_pref = random.choice(["Cold Sens (오한/추위탐)", "Balanced (보통)", "Heat Sens (열감/더위탐)"])
    session.drink_temp = random.choice(["Icy (냉수)", "Warm (온수)", "Hot (열수)"])
    
    # ===========================================
    # 7. MENTAL, SENSORY & INSPECTION
    # ===========================================
    session.personality_speed = random.randint(1, 5)
    session.personality_io = random.randint(1, 5)
    session.personality_soft = random.randint(1, 5)
    session.personality_static = random.randint(1, 5)
    
    session.emot_anger = random.randint(1, 5)
    session.emot_depress = random.randint(1, 5)
    session.emot_anxiety = random.randint(1, 5)
    session.excitement = random.randint(1, 5)
    session.emot_fear = random.randint(1, 5)
    session.emot_thought = random.randint(1, 5)
    session.emot_grief = random.randint(1, 5)
    
    session.fatigue_level = random.choice(["None (없음)", "Low (약함)", "Moderate (중등도)", "Severe (심함)"])
    session.voice_vol = random.choice(["Soft (작음)", "Normal (보통)", "Loud (큼)"])
    session.voice_vol_slider = random.randint(1, 3)
    
    session.memory = random.choice(["Good (좋음)", "Forgetful (건망)", "Bad (나쁨)"])
    session.motivation = random.choice(["High (높음)", "Normal (보통)", "Low (낮음)", "Apathetic (무기력)"])
    session.stress_coping = random.choice(["Good (좋음)", "Average (보통)", "Poor (나쁨)"])
    
    session.edema = random.choice(["None (없음)", "Face (안면)", "Legs (하지)", "General (전신)"])
    session.bruising = random.choice(["Normal (정상)", "Easy (잘듦)", "Spontaneous (절로 생김)"])
    session.limb_weakness = random.choice([True, False])
    session.vision_blackout = random.choice([True, False])
    
    session.body_solidity = random.choice(["Soft (물렁)", "Normal (보통)", "Solid (단단)"])
    session.face_color = random.choice(["Normal (정상)", "Pale (창백)", "Red (홍조)", "Yellow (황달)", "Dark (암색)"])
    session.face_gloss = random.choice(["Dull (칙칙)", "Normal (보통)", "Shiny (윤기)"])
    session.eye_red = random.choice([True, False])
    session.lip_dry = random.choice([True, False])
    
    session.skin_dry = random.choice(["Normal (정상)", "Dry (건조)", "Scaly (각질)"])
    session.skin_itch = random.choice([True, False])
    
    session.tinnitus_freq = random.randint(0, 5)
    session.tinnitus_sev = random.randint(0, 5)
    session.hearing_sev = random.randint(0, 5)
    session.dizziness_sev = random.randint(0, 5)
    
    session.lip_color = random.choice(["Normal (정상)", "Pale (창백)", "Red (붉음)", "Dark (어두움)"])
    session.mouth_dry = random.randint(0, 5)
    session.throat_dry = random.choice([True, False])
    session.mouth_bitter = random.choice([True, False])
    session.bad_breath = random.choice([True, False])
    session.hiccup = random.choice([True, False])
    
    session.neck_nape_freq = random.randint(0, 5)
    session.neck_nape_sev = random.randint(0, 5)
    
    session.breath_sound = random.choice(["Normal (정상)", "Loud (큼)", "Weak (약함)"])
    session.palpitation = random.randint(0, 5)
    session.chest_tight_freq = random.randint(0, 5)
    session.chest_tight_sev = random.randint(0, 5)
    session.chest_pain_freq = random.randint(0, 5)
    session.chest_pain_sev = random.randint(0, 5)
    session.sighing_freq = random.randint(0, 5)
    session.nausea = random.randint(0, 5)
    session.bloating = random.randint(0, 5)
    session.flatulence = random.choice(["None (없음)", "Normal (보통)", "Frequent (잦음)"])
    
    session.lower_abd_discomfort = random.randint(0, 5)
    session.abd_pain_sev = random.randint(0, 5)
    session.abd_pain_type = random.choice(["None (없음)", "Dull (둔통)", "Sharp (예리통)", "Cramping (산통/경련통)"])
    session.abd_tenderness = random.choice([True, False])
    session.nausea_sev = random.randint(0, 5)
    session.belching = random.randint(0, 5)
    session.belching_smell = random.choice(["None (없음)", "Sour (신맛/산취)", "Foul (부패취)"])
    session.food_stag_sev = random.randint(0, 5)
    session.abd_muscle_tension = random.choice([True, False])
    session.abd_mass = random.choice([True, False])
    session.abd_pulsation = random.choice([True, False])
    session.bowel_sound = random.choice(["Normal (정상)", "Hyperactive (항진)", "Hypoactive (저하)"])
    
    session.cold_heat_body = random.choice(["Cold (한 寒)", "Balanced (보통)", "Hot (열 熱)"])
    session.cold_heat_distribution = random.choice(["Even (균등)", "Upper Hot (상열 上熱)", "Lower Cold (하한 下寒)", "Upper Hot Lower Cold (상열하한 上熱下寒)"])
    session.cold_sensitivity = random.randint(1, 5)
    session.heat_sensitivity = random.randint(1, 5)
    
    session.physical_strength = random.choice(["Weak (허약)", "Normal (보통)", "Strong (강건)"])
    session.condition_bad_area = random.sample(["Head (두부)", "Stomach (위장)", "Back (요배부)", "Limbs (사지)"], k=random.randint(0, 2))
    
    session.sweat_time = random.choice(["Daytime (주간)", "Night (야간/도한)", "Exercise (운동시)"])
    
    session.mental_clarity = random.choice(["Clear (맑음/청명)", "Foggy (흐릿/혼미)", "Confused (혼란)"])
    session.mood_swing = random.choice(["Stable (안정)", "Mild (약간)", "Severe (심함)"])
    session.emot_startle = random.randint(1, 5)
    
    session.flank_freq = random.randint(0, 5)
    session.flank_sev = random.randint(0, 5)
    session.back_freq = random.randint(0, 5)
    session.back_sev = random.randint(0, 5)
    session.pelvis_freq = random.randint(0, 5)
    session.pelvis_sev = random.randint(0, 5)
    session.shoulder_freq = random.randint(0, 5)
    session.shoulder_sev = random.randint(0, 5)
    session.elbow_freq = random.randint(0, 5)
    session.elbow_sev = random.randint(0, 5)
    session.hand_foot_freq = random.randint(0, 5)
    session.hand_foot_sev = random.randint(0, 5)
    session.leg_discomfort = random.randint(0, 5)
    session.knee_freq = random.randint(0, 5)
    session.knee_sev = random.randint(0, 5)
    
    # ===========================================
    # 8. PULSE & TONGUE (맥진 및 설진)
    # ===========================================
    session.pulse_depth = random.choice(["Floating (부맥)", "Middle (중맥)", "Sinking (침맥)"])
    session.pulse_width = random.choice(["Thin (세맥)", "Medium (대맥)", "Wide (홍맥)"])
    session.pulse_length = random.choice(["Short (단맥)", "Medium (장맥)", "Long (장맥)"])
    session.pulse_strength = random.choice(["Weak (무력)", "Moderate (유력)", "Strong (강력)"])
    session.pulse_smooth = random.choice(["Smooth (활맥)", "Normal (완맥)", "Rough (삽맥)"])
    session.pulse_tension = random.choice(["Soft (유맥)", "Normal (완맥)", "Tense (긴맥)"])
    
    session.tongue_color = random.choice(["Pale (담백)", "Pale Red (담홍)", "Red (홍설)", "Dark Red (강홍/자설)"])
    session.tongue_size = random.choice(["Small (소)", "Normal (정상)", "Enlarged (대/태)"])
    session.tongue_coat_color = random.choice(["White (백태)", "Yellow (황태)", "Grey (회태)"])
    session.tongue_coat_thick = random.choice(["Thin (박태)", "Thick (후태)", "Greasy (니태)"])
    session.tongue_coat_particle = random.choice(["Dry (조태)", "Fine (윤태)", "Wet (활태)"])
    session.tongue_marks = random.choice([True, False])
    
    # ===========================================
    # 9. PAIN GRID
    # ===========================================
    for part in ["pain_neck", "pain_shoulder", "pain_back", "pain_knee", "pain_hand", "pain_elbow", "pain_flank", "pain_pelvis", "pain_hip"]:
        freq = random.randint(0, 5)
        intensity = random.randint(0, 10) if freq > 0 else 0
        session[part] = [freq, intensity]
        session[f"{part}_f"] = freq
        session[f"{part}_i"] = intensity
    
    session.cold_hands_feet = random.choice([True, False])
    
    # ===========================================
    # 10. DISEASE & PATTERN SELECTION
    # ===========================================
    disease_opts = ["Common Cold (감기/급성상기도감염)", "Allergic Rhinitis (알레르기비염)", "Back Pain (요통)", "Functional Dyspepsia (기능성소화불량)"]
    session.disease = random.choice(disease_opts)
    
    if "Cold" in session.disease:
        num_patterns = len(DISEASE_PATTERNS["감기"]["patterns"])
        session.pattern_idx = random.randint(0, num_patterns - 1)
    elif "Rhinitis" in session.disease:
        num_patterns = len(DISEASE_PATTERNS["알레르기비염"]["patterns"])
        session.pattern_idx = random.randint(0, num_patterns - 1)
    elif "Back Pain" in session.disease:
        num_patterns = len(DISEASE_PATTERNS["요통"]["patterns"])
        session.pattern_idx = random.randint(0, num_patterns - 1)
    elif "Dyspepsia" in session.disease:
        num_patterns = len(DISEASE_PATTERNS["기능성소화불량"]["patterns"])
        session.pattern_idx = random.randint(0, num_patterns - 1)
    
    # ===========================================
    # 11. APPLY CONSTRAINT RULES
    # Constraints must be applied HERE during randomization,
    # NOT during patient generation (after widgets are rendered)
    # because Streamlit prevents modifying widget-bound session_state
    # ===========================================
    apply_constraint_rules(st)
    apply_symptom_correlation_rules(st.session_state)
