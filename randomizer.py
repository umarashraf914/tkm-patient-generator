"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - Randomization Functions
═══════════════════════════════════════════════════════════════════════════════
"""

import random
import logging
from data_mappings import get_weights
from constants import (
    DISEASE_PATTERNS, PAST_COLD_PROBLEM_AREAS, AGGRAVATING_FACTORS,
    RELIEVING_FACTORS, FREQUENT_COMORBIDITIES,
    get_random_additional_symptoms, get_random_comorbidities
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
# LOGGING CONFIGURATION
# ============================================================================

# Create a logger for randomization tracking
randomizer_logger = logging.getLogger("randomizer")
randomizer_logger.setLevel(logging.DEBUG)

# Create console handler if not already present
if not randomizer_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s [%(name)s] %(message)s')
    console_handler.setFormatter(formatter)
    randomizer_logger.addHandler(console_handler)

# Enable/disable detailed logging (set to True to see all value changes)
# Set to False to disable console output
ENABLE_RANDOMIZER_LOGGING = False  # Change to True to enable detailed logging

def log_value_set(field_name: str, value, source: str):
    """Log when a session state value is set."""
    if ENABLE_RANDOMIZER_LOGGING:
        randomizer_logger.debug(f"SET {field_name} = {value} [Source: {source}]")

def log_layer_start(layer_name: str):
    """Log when a layer starts."""
    if ENABLE_RANDOMIZER_LOGGING:
        randomizer_logger.info(f"{'='*50}")
        randomizer_logger.info(f"STARTING: {layer_name}")
        randomizer_logger.info(f"{'='*50}")


def print_randomization_summary(session):
    """Print a human-readable summary of key randomized values."""
    print("\n" + "="*60)
    print("🎲 RANDOMIZATION SUMMARY")
    print("="*60)
    print(f"Disease: {getattr(session, 'disease', 'N/A')}")
    print(f"Pattern Index: {getattr(session, 'pattern_idx', 'N/A')}")
    print("-"*60)
    print("COMORBIDITIES (현병력) - FROM CSV:")
    hx = getattr(session, 'history_conditions', [])
    if hx:
        for c in hx:
            print(f"  ✓ {c}")
    else:
        print("  (None)")
    print("-"*60)
    print("Expected CSV Probabilities:")
    print("  당뇨: 15%  |  고혈압: 30%  |  이상지질혈증: 45%")
    print("="*60 + "\n")


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
        
        # =============================================================================
        # Map CSV symptom keys to session state variables
        # CSV keys follow pattern: "Category_Subcategory_ItemName"
        # =============================================================================
        
        # Helper function to find key by partial match
        def find_key(partial_name):
            """Find a key in patient_data containing the partial name."""
            for key in patient_data:
                if partial_name in key:
                    return key
            return None
        
        # Demographics - use actual CSV keys
        sex_key = find_key("성별")
        if sex_key and sex_key in patient_data:
            opt = patient_data[sex_key]["option_number"]
            session.sex = "남" if opt == 1 else "여"
        
        age_key = find_key("나이")
        if age_key and age_key in patient_data:
            opt = patient_data[age_key]["option_number"]
            # Map age category to actual age range
            age_ranges = {1: (10, 19), 2: (20, 39), 3: (40, 54), 4: (55, 69), 5: (70, 85)}
            age_range = age_ranges.get(opt, (20, 80))
            session.age = random.randint(age_range[0], age_range[1])
        
        job_key = find_key("직업")
        if job_key and job_key in patient_data:
            opt = patient_data[job_key]["option_number"]
            job_map = {
                1: "사무직", 2: "사무직", 
                3: "사무직", 4: "사무직",
                5: "사무직", 6: "현장직",
                7: "현장직", 8: "현장직",
                9: "현장직", 10: "사무직",
                11: "사무직"
            }
            session.job = job_map.get(opt, "사무직")
        
        # Height/Weight from category
        height_key = find_key("키")
        if height_key and height_key in patient_data:
            opt = patient_data[height_key]["option_number"]
            # Map to approximate height ranges
            height_ranges = {1: (150, 155), 2: (156, 162), 3: (163, 178), 4: (179, 186), 5: (187, 195)}
            h_range = height_ranges.get(opt, (160, 180))
            session.height = random.randint(h_range[0], h_range[1])
        
        weight_key = find_key("몸무게")
        if weight_key and weight_key in patient_data:
            opt = patient_data[weight_key]["option_number"]
            weight_ranges = {1: (45, 55), 2: (56, 63), 3: (64, 76), 4: (77, 85), 5: (86, 100)}
            w_range = weight_ranges.get(opt, (55, 85))
            session.weight = random.randint(w_range[0], w_range[1])
        
        # Vitals - use actual CSV keys
        temp_key = find_key("체온")
        if temp_key and temp_key in patient_data:
            opt = patient_data[temp_key]["option_number"]
            temp_ranges = {1: (34.5, 35.5), 2: (36.0, 37.3), 3: (37.4, 37.9), 4: (38.0, 39.9), 5: (40.0, 41.0)}
            t_range = temp_ranges.get(opt, (36.0, 37.5))
            session.temp = round(random.uniform(t_range[0], t_range[1]), 1)
        
        pulse_key = find_key("맥박")
        if pulse_key and pulse_key in patient_data:
            opt = patient_data[pulse_key]["option_number"]
            pulse_ranges = {1: (45, 50), 2: (50, 60), 3: (60, 80), 4: (80, 100), 5: (100, 120)}
            p_range = pulse_ranges.get(opt, (60, 90))
            session.pulse_rate = random.randint(p_range[0], p_range[1])
        
        resp_key = find_key("호흡")
        if resp_key and resp_key in patient_data:
            opt = patient_data[resp_key]["option_number"]
            resp_ranges = {1: (8, 12), 2: (12, 20), 3: (21, 28)}
            r_range = resp_ranges.get(opt, (12, 20))
            session.resp = random.randint(r_range[0], r_range[1])
        
        bp_key = find_key("혈압")
        if bp_key and bp_key in patient_data:
            opt = patient_data[bp_key]["option_number"]
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
        session.fever_sev = int(opt) if opt else 1
    
    # Chills severity
    if "감기환자_감기주소증 유형_오한" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_오한"]["option_number"]
        session.chills_sev = int(opt) if opt else 1
    
    # Nasal discharge amount
    if "감기환자_감기주소증 유형_콧물 감기" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_콧물 감기"]["option_number"]
        session.snot_sev = int(opt) if opt else 1
    
    # Nasal discharge color - map option number to UI string
    if "감기환자_감기주소증 유형_콧물 색" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_콧물 색"]["option_number"]
        snot_color_map = {
            1: "없음",
            2: "맑음/투명",
            3: "백색",
            4: "황색",
            5: "녹색"
        }
        session.snot_color = snot_color_map.get(opt, "없음")
    
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
        session.cough_sev = int(opt) if opt else 1
    
    # Phlegm amount
    if "감기환자_감기주소증 유형_담(가래) 양" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_담(가래) 양"]["option_number"]
        session.phlegm_amt = int(opt) if opt else 0
    
    # Phlegm color - map option number to UI string
    if "감기환자_감기주소증 유형_담(가래) 색" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_담(가래) 색"]["option_number"]
        phlegm_color_map = {
            1: "맑음",
            2: "백색",
            3: "황색",
            4: "녹색"
        }
        session.phlegm_color = phlegm_color_map.get(opt, "맑음")
    
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
    
    # Throat exam - map to UI string values
    if "감기환자_한의사 진찰 및 검사소견_인후부 진찰" in patient_data:
        opt = patient_data["감기환자_한의사 진찰 및 검사소견_인후부 진찰"]["option_number"]
        session.throat_redness = opt
        # Map to exam_throat_visual UI option
        throat_visual_map = {
            1: "정상",
            2: "발적",
            3: "부종",
            4: "삼출물"
        }
        session.exam_throat_visual = throat_visual_map.get(opt, "정상")
    else:
        session.exam_throat_visual = random.choice(["정상", "발적", "부종"])
    
    # Tonsil exam - map to UI string values
    if "감기환자_한의사 진찰 및 검사소견_편도진찰" in patient_data:
        opt = patient_data["감기환자_한의사 진찰 및 검사소견_편도진찰"]["option_number"]
        session.tonsil_swelling = opt
        # Map to exam_tongue_depressor UI option
        tongue_dep_map = {
            1: "정상",
            2: "편도비대",
            3: "삼출물",
            4: "염증"
        }
        session.exam_tongue_depressor = tongue_dep_map.get(opt, "정상")
    else:
        session.exam_tongue_depressor = random.choice(["정상", "편도비대"])
    
    # Stethoscope exam (lung sounds)
    if "감기환자_한의사 진찰 및 검사소견_호흡음(폐음) 진찰" in patient_data:
        opt = patient_data["감기환자_한의사 진찰 및 검사소견_호흡음(폐음) 진찰"]["option_number"]
        stethoscope_map = {
            1: "정상",
            2: "수포음",
            3: "천명음",
            4: "감소"
        }
        session.exam_stethoscope = stethoscope_map.get(opt, "정상")
    else:
        session.exam_stethoscope = random.choice(["정상", "수포음"])
    
    # Rhinoscope exam
    if "감기환자_한의사 진찰 및 검사소견_비경 검사" in patient_data:
        opt = patient_data["감기환자_한의사 진찰 및 검사소견_비경 검사"]["option_number"]
        rhinoscope_map = {
            1: "정상",
            2: "충혈"
        }
        session.exam_rhinoscope_finding = rhinoscope_map.get(opt, "정상")
    else:
        session.exam_rhinoscope_finding = random.choice(["정상", "충혈", "분비물"])
    
    # Smell reduction
    if "감기환자_감기주소증 유형_후각 감퇴" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_후각 감퇴"]["option_number"]
        session.smell_reduction = int(opt) if opt else 0
    else:
        session.smell_reduction = random.randint(0, 3)
    
    # Alternating chills-fever
    if "감기환자_감기주소증 유형_한열왕래" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_한열왕래"]["option_number"]
        session.alternating_chills_fever = int(opt) if opt else 0
    else:
        session.alternating_chills_fever = random.randint(0, 3)
    
    # Dyspnea
    if "감기환자_감기주소증 유형_숨이 가쁨" in patient_data:
        opt = patient_data["감기환자_감기주소증 유형_숨이 가쁨"]["option_number"]
        session.cold_dyspnea = bool(opt >= 2)
    else:
        session.cold_dyspnea = random.choice([True, False, False])  # Usually False
    
    # Cold onset specific (days)
    if "감기환자_O/S_감기증상 발현시점" in patient_data:
        opt = patient_data["감기환자_O/S_감기증상 발현시점"]["option_number"]
        onset_specific_map = {
            1: "1일 전",
            2: "2일 전",
            3: "3일 전",
            4: "4일 전",
            5: "5일 전",
            6: "1주일 전"
        }
        session.cold_onset_specific = onset_specific_map.get(opt, "3일 전")
    else:
        session.cold_onset_specific = random.choice(["1일 전", "2일 전", "3일 전", "4일 전", "5일 전"])
    
    # =========================================================================
    # Set cold_symptoms_spec based on pattern and CSV data
    # This maps various CSV symptoms to the UI multiselect options
    # =========================================================================
    cold_symptoms = []
    
    # Check for sweating (무한 = no sweat = 풍한)
    sweat_opt = patient_data.get("감기환자_감기주소증 유형_감기 시 땀 유무", {}).get("option_number", 3)
    if sweat_opt == 1:  # No sweating
        cold_symptoms.append("무한 (無汗) - 풍한")
    
    # Check phlegm color for yellow (황담 = 풍열)
    phlegm_color_opt = patient_data.get("감기환자_감기주소증 유형_담(가래) 색", {}).get("option_number", 1)
    if phlegm_color_opt == 3:  # Yellow
        cold_symptoms.append("황담 (黃痰) - 풍열")
    elif phlegm_color_opt in [1, 2]:  # Clear or White
        cold_symptoms.append("희박담 (稀薄白痰) - 풍한")
    
    # Check for sore throat/dry throat (인후건조 = 풍조)
    throat_opt = patient_data.get("감기환자_감기주소증 유형_인후통", {}).get("option_number", 1)
    if throat_opt >= 3:  # Significant throat symptoms
        cold_symptoms.append("인후건조 (咽乾) - 풍조")
    
    # Check for body ache (골절동통 = 풍한)
    body_ache_opt = patient_data.get("감기환자_감기주소증 유형_몸살, 신체통, 근육통", {}).get("option_number", 1)
    if body_ache_opt >= 3:  # Significant body ache
        cold_symptoms.append("골절동통 (骨節疼痛) - 풍한")
    
    # Check cough with little phlegm (객담소 = 풍조)
    cough_opt = patient_data.get("감기환자_감기주소증 유형_기침", {}).get("option_number", 1)
    phlegm_amt_opt = patient_data.get("감기환자_감기주소증 유형_담(가래) 양", {}).get("option_number", 1)
    if cough_opt >= 3 and phlegm_amt_opt <= 2:  # Cough but little phlegm
        cold_symptoms.append("객담소 (咳嗽少痰) - 풍조")
    
    # Set cold_symptoms_spec (ensure at least 1-2 symptoms for realism)
    if not cold_symptoms:
        # Default based on randomization
        cold_symptoms = random.sample([
            "무한 (無汗) - 풍한",
            "희박담 (稀薄白痰) - 풍한",
            "골절동통 (骨節疼痛) - 풍한"
        ], k=random.randint(1, 2))
    
    session.cold_symptoms_spec = cold_symptoms
    
    # =========================================================================
    # Set cold chief complaint checkboxes based on CSV data
    # =========================================================================
    # Sore throat checkbox
    session.sore_throat = bool(throat_opt >= 2)
    
    # Body ache checkbox
    session.body_ache_cold = bool(body_ache_opt >= 2)
    
    # Body heaviness checkbox
    body_heavy_opt = patient_data.get("감기환자_감기주소증 유형_신중(身重)", {}).get("option_number", 1)
    session.body_heaviness_cold = bool(body_heavy_opt >= 2)
    
    # Headache checkbox
    headache_opt = patient_data.get("감기환자_감기주소증 유형_두부, 뒷목 불편감(강도)", {}).get("option_number", 1)
    session.headache_cold = bool(headache_opt >= 2)
    
    # Neck pain checkbox (based on headache area)
    session.neck_pain_cold = bool(headache_opt >= 3)
    
    # Sweating checkbox
    session.cold_sweating_check = bool(sweat_opt >= 3)
    
    # Cold chief type (at least 1 required)
    cold_chief_types = []
    if session.fever_sev >= 2:
        cold_chief_types.append("발열 (Fever)")
    if session.chills_sev >= 2:
        cold_chief_types.append("오한 (Chills)")
    if session.snot_sev >= 2:
        cold_chief_types.append("콧물 (Runny nose)")
    if session.cough_sev >= 2:
        cold_chief_types.append("기침 (Cough)")
    if throat_opt >= 2:
        cold_chief_types.append("인후통 (Sore throat)")
    
    # Ensure at least 1 chief type
    if not cold_chief_types:
        cold_chief_types = ["기침 (Cough)"]
    
    session.cold_chief_type = cold_chief_types


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
        session.snot_sev = int(opt) if opt else 1
    
    # Nasal discharge color - map to snot_type for rhinitis (different UI options)
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_콧물 색" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_콧물 색"]["option_number"]
        snot_type_map = {
            1: "청수양 (淸水樣) - 맑은 콧물",
            2: "백점액 (白粘) - 희고 끈적",
            3: "황농성 (黃膿) - 누렇고 찐득"
        }
        session.snot_type = snot_type_map.get(opt, "청수양 (淸水樣) - 맑은 콧물")
    
    # Nasal congestion
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_코막힘" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_코막힘"]["option_number"]
        session.nose_block_sev = int(opt) if opt else 1
    
    # Sneezing intensity
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(정도)" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(정도)"]["option_number"]
        session.sneeze_intensity = int(opt) if opt else 1
    
    # Sneezing frequency
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(빈도)" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_재채기(빈도)"]["option_number"]
        session.sneeze_sev = int(opt) if opt else 1
    
    # Nose itching
    if "알러지비염가상환자_알러지비염 주증 및 동반증상_코 가려움" in patient_data:
        opt = patient_data["알러지비염가상환자_알러지비염 주증 및 동반증상_코 가려움"]["option_number"]
        session.nose_itch_sev = int(opt) if opt else 1


def _apply_common_symptoms(session, patient_data):
    """Apply common symptoms that are shared across diseases."""
    log_layer_start("LAYER 2: CSV-based Common Symptoms")
    
    # History conditions - use correct CSV key pattern
    hx_conditions = []
    for key in patient_data:
        if "현병력" in key and "고혈압" in key:
            if patient_data[key]["option_number"] == 2:
                hx_conditions.append("고혈압")
        elif "현병력" in key and "당뇨" in key:
            if patient_data[key]["option_number"] == 2:
                hx_conditions.append("당뇨")
        elif "현병력" in key and "이상지질혈증" in key:
            if patient_data[key]["option_number"] == 2:
                hx_conditions.append("이상지질혈증")
    session.history_conditions = hx_conditions
    log_value_set("history_conditions", hx_conditions, "CSV (현병력)")
    
    # Medications - match with history conditions
    meds = []
    if "고혈압" in hx_conditions:
        meds.append("혈압약")
    if "당뇨" in hx_conditions:
        meds.append("당뇨약")
    if "이상지질혈증" in hx_conditions:
        meds.append("이상지질혈증약")
    session.meds_specific = meds
    
    # Family history - use correct CSV key pattern
    fam_hx = []
    for key in patient_data:
        if "가족력" in key:
            if "고혈압" in key and patient_data[key]["option_number"] == 2:
                fam_hx.append("고혈압")
            elif "당뇨" in key and patient_data[key]["option_number"] == 2:
                fam_hx.append("당뇨")
            elif "심장병" in key and patient_data[key]["option_number"] == 2:
                fam_hx.append("심장병")
            elif "중풍" in key and patient_data[key]["option_number"] == 2:
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
    
    log_layer_start("LAYER 1: Hardcoded Random Values")
    
    # ===========================================
    # 1. DEMOGRAPHICS (인구학적정보)
    # NOTE: Minimum age = 10 to match CSV rule categories (options 1-5 start at age 10-19)
    # UI BOUNDS: height min=130, weight min=30
    # ===========================================
    session.age = random.randint(10, 85)  # Min 10 to match CSV rules
    session.sex = random.choice(["남", "여"])
    session.job = random.choice(["학생", "사무직", "현장직", "가사"])
    session.height = random.randint(140, 190)  # Adjusted for age 10+, UI min is 130
    session.weight = random.randint(45, 100)   # Adjusted for age 10+, UI min is 30
    log_value_set("age/sex/job/height/weight", f"{session.age}/{session.sex}/.../...", "HARDCODED")
    
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
    session.onset = random.choice(["1일 전", "2-3일 전", "1주 전", "만성 3개월 이상"])
    session.course = random.choice(["악화중", "호전중", "비슷/오르내림"])
    session.history_conditions = random.sample(["고혈압", "당뇨", "이상지질혈증", "기타"], k=random.randint(0, 2))
    log_value_set("history_conditions", session.history_conditions, "HARDCODED (will be overwritten by CSV)")
    session.meds_specific = random.sample(["혈압약", "당뇨약", "이상지질혈증약", "수면제", "항우울제", "항불안제"], k=random.randint(0, 3))
    session.family_hx = random.sample(["고혈압", "당뇨", "이상지질혈증", "심장병", "중풍", "기타"], k=random.randint(0, 2))
    session.past_cold_problem_area = random.sample(PAST_COLD_PROBLEM_AREAS, k=random.randint(0, 2))
    session.aggravating_factors = random.sample(AGGRAVATING_FACTORS, k=random.randint(0, 3))
    session.relieving_factors = random.sample(RELIEVING_FACTORS, k=random.randint(0, 2))
    
    # Additional Symptoms & Comorbidities (추가 증상 및 동반질환 - Pages 24-25)
    session.additional_symptoms = get_random_additional_symptoms(count=random.randint(1, 2))
    session.additional_comorbidities = get_random_comorbidities(count=random.randint(0, 2))
    
    # Social History (사회력)
    session.social_alcohol_freq = random.choice(["비음주", "주간", "매일"])
    session.social_alcohol_amt = round(random.uniform(0, 5), 1) if session.social_alcohol_freq != "비음주" else 0.0
    session.social_smoke_daily = round(random.uniform(0, 20), 1)
    session.social_exercise_int = random.choice(["저", "중", "고"])
    session.social_exercise_time = random.randint(0, 120)
    
    # ===========================================
    # 4. WOMEN'S HEALTH (여성력)
    # ===========================================
    if session.sex == "여":
        session.mens_cycle = random.randint(21, 35)
        session.mens_regular = random.choice(["규칙", "불규칙", "폐경"])
        session.mens_amt = random.choice(["적음", "보통", "많음"])
        session.mens_clot = random.choice([True, False])
        session.mens_color = random.choice(["연함", "적색", "흑자색"])
        session.mens_duration = random.randint(3, 7)
        session.mens_pain_score = random.randint(0, 10)
    
    # ===========================================
    # 5. EXCRETION & DIET (배설 및 식사)
    # ===========================================
    session.diet_speed = random.choice(["빠름 (<10분)", "보통 (20분)", "느림 (>30분)"])
    session.appetite = random.choice(["없음", "저하", "보통", "항진"])
    session.diet_freq = random.choice([1, 2, 3, 4])
    session.diet_regular = random.choice(["규칙적", "불규칙"])
    session.water_intake = random.choice(["0.5L 미만", "0.5-1L", "1-2L", "2L 이상"])
    
    session.stool_freq = random.choice(["1회/일", "2-3회/일", "변비"])
    session.stool_form = random.choice(["보통", "묽음/연변", "굳음/경변"])
    session.stool_discomfort = random.choice([True, False])
    session.stool_color = random.choice(["황색", "황갈색", "흑색", "녹색"])
    
    session.urine_freq_day = random.randint(3, 12)
    session.urine_freq_night = random.randint(0, 4)
    session.urine_stream = random.choice(["정상", "약함", "끊김"])
    session.urine_residual = random.choice([True, False])
    session.urine_incontinence = random.choice([True, False])
    session.urine_color = random.choice(["맑음", "황색", "적색/혈뇨"])
    
    # ===========================================
    # 6. SLEEP, SWEAT, COLD/HEAT (수면, 땀, 한열)
    # ===========================================
    session.sleep_hours = random.randint(4, 10)
    session.sleep_waking_state = random.choice(["개운함", "피곤함", "무거움"])
    session.sleep_depth = random.choice(["깊음", "얕음"])
    session.insomnia_onset = random.choice([True, False])
    session.insomnia_maintain = random.choice([True, False])
    session.insomnia_reentry = random.choice([True, False])
    session.dreams = random.choice(["거의 없음", "가끔", "자주", "악몽"])
    
    session.sweat_amt = random.choice(["무한 (無汗)", "보통", "다한 (多汗)"])
    session.sweat_area = random.choice(["전신", "두부", "야간/도한"])
    session.sweat_feeling = random.choice(["상쾌", "피곤/냉함", "열감"])
    
    session.cold_heat_pref = random.choice(["오한/추위탐", "보통", "열감/더위탐"])
    session.drink_temp = random.choice(["냉수", "온수", "열수"])
    
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
    
    session.fatigue_level = random.choice(["없음", "약함", "중등도", "심함"])
    session.voice_vol = random.choice(["작음", "보통", "큼"])
    session.voice_vol_slider = random.randint(1, 3)
    
    session.memory = random.choice(["좋음", "건망", "나쁨"])
    session.motivation = random.choice(["높음", "보통", "낮음", "무기력"])
    session.stress_coping = random.choice(["좋음", "보통", "나쁨"])
    
    session.edema = random.choice(["없음", "안면", "하지", "전신"])
    session.bruising = random.choice(["정상", "잘듦", "절로 생김"])
    session.limb_weakness = random.choice([True, False])
    session.vision_blackout = random.choice([True, False])
    
    session.body_solidity = random.choice(["물렁", "보통", "단단"])
    session.face_color = random.choice(["정상", "창백", "홍조", "황달", "암색"])
    session.face_gloss = random.choice(["칙칙", "보통", "윤기"])
    session.eye_red = random.choice([True, False])
    session.lip_dry = random.choice([True, False])
    
    session.skin_dry = random.choice(["정상", "건조", "각질"])
    session.skin_itch = random.choice([True, False])
    
    session.tinnitus_freq = random.randint(0, 5)
    session.tinnitus_sev = random.randint(0, 5)
    session.hearing_sev = random.randint(0, 5)
    session.dizziness_sev = random.randint(0, 5)
    
    session.lip_color = random.choice(["정상", "창백", "붉음", "어두움"])
    session.mouth_dry = random.randint(0, 5)
    session.throat_dry = random.choice([True, False])
    session.mouth_bitter = random.choice([True, False])
    session.bad_breath = random.choice([True, False])
    session.hiccup = random.choice([True, False])
    
    session.neck_nape_freq = random.randint(0, 5)
    session.neck_nape_sev = random.randint(0, 5)
    
    session.breath_sound = random.choice(["정상", "큼", "약함"])
    session.palpitation = random.randint(0, 5)
    session.chest_tight_freq = random.randint(0, 5)
    session.chest_tight_sev = random.randint(0, 5)
    session.chest_pain_freq = random.randint(0, 5)
    session.chest_pain_sev = random.randint(0, 5)
    session.sighing_freq = random.randint(0, 5)
    session.nausea = random.randint(0, 5)
    session.bloating = random.randint(0, 5)
    session.flatulence = random.choice(["없음", "보통", "잦음"])
    
    session.lower_abd_discomfort = random.randint(0, 5)
    session.abd_pain_sev = random.randint(0, 5)
    session.abd_pain_type = random.choice(["없음", "둔통", "예리통", "산통/경련통"])
    session.abd_tenderness = random.choice([True, False])
    session.nausea_sev = random.randint(0, 5)
    session.belching = random.randint(0, 5)
    session.belching_smell = random.choice(["없음", "신맛/산취", "부패취"])
    session.food_stag_sev = random.randint(0, 5)
    session.abd_muscle_tension = random.choice([True, False])
    session.abd_mass = random.choice([True, False])
    session.abd_pulsation = random.choice([True, False])
    session.bowel_sound = random.choice(["정상", "항진", "저하"])
    
    session.cold_heat_body = random.choice(["한 (寒)", "보통", "열 (熱)"])
    session.cold_heat_distribution = random.choice(["균등", "상열 (上熱)", "하한 (下寒)", "상열하한 (上熱下寒)"])
    session.cold_sensitivity = random.randint(1, 5)
    session.heat_sensitivity = random.randint(1, 5)
    
    session.physical_strength = random.choice(["허약", "보통", "강건"])
    session.condition_bad_area = random.sample(["두부", "위장", "요배부", "사지"], k=random.randint(0, 2))
    
    session.sweat_time = random.choice(["주간", "야간/도한", "운동시"])
    
    session.mental_clarity = random.choice(["맑음/청명", "흐릿/혼미", "혼란"])
    session.mood_swing = random.choice(["안정", "약간", "심함"])
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
    # NOTE: Only 감기 and 알레르기비염 have CSV rules ready
    # So we only randomize to these two diseases for now
    # ===========================================
    # Only select from supported diseases (Cold and Rhinitis)
    supported_disease_opts = [
        "Common Cold (감기/급성상기도감염)", 
        "Allergic Rhinitis (알레르기비염)"
    ]
    session.disease = random.choice(supported_disease_opts)
    
    if "Cold" in session.disease:
        num_patterns = len(DISEASE_PATTERNS["감기"]["patterns"])
        session.pattern_idx = random.randint(0, num_patterns - 1)
        # Try to use CSV-based randomization for Cold
        _apply_csv_cold_randomization(st)
    elif "Rhinitis" in session.disease:
        num_patterns = len(DISEASE_PATTERNS["알레르기비염"]["patterns"])
        session.pattern_idx = random.randint(0, num_patterns - 1)
        # Try to use CSV-based randomization for Rhinitis
        _apply_csv_rhinitis_randomization(st)
    
    # ===========================================
    # 11. APPLY CONSTRAINT RULES
    # Constraints must be applied HERE during randomization,
    # NOT during patient generation (after widgets are rendered)
    # because Streamlit prevents modifying widget-bound session_state
    # ===========================================
    log_layer_start("LAYER 3: Constraint Rules")
    apply_constraint_rules(st)
    log_layer_start("LAYER 4: Symptom Correlation Rules")
    apply_symptom_correlation_rules(st.session_state)
    
    # ===========================================
    # FINAL SAFETY CLAMP: Ensure all values are within UI bounds
    # This prevents Streamlit errors when widget values < min_value
    # ===========================================
    log_layer_start("LAYER 5: UI Bounds Safety Clamp")
    session = st.session_state
    # Age: UI min=10, max=100
    session.age = max(10, min(100, session.age))
    # Height: UI min=130, max=220
    session.height = max(130, min(220, session.height))
    # Weight: UI min=30, max=150
    session.weight = max(30, min(150, session.weight))
    # SBP: UI min=90, max=180
    session.sbp = max(90, min(180, session.sbp))
    # DBP: UI min=50, max=120
    session.dbp = max(50, min(120, session.dbp))
    # Pulse: UI min=50, max=130
    session.pulse_rate = max(50, min(130, session.pulse_rate))
    # Temp: UI min=35.0, max=40.5
    session.temp = max(35.0, min(40.5, session.temp))
    # Resp: UI min=8, max=30
    session.resp = max(8, min(30, session.resp))
    
    log_layer_start("RANDOMIZATION COMPLETE")
    log_value_set("FINAL history_conditions", st.session_state.history_conditions, "After all layers")


def _apply_csv_cold_randomization(st):
    """Apply CSV-based randomization for Common Cold (감기)."""
    if not CSV_RULES_AVAILABLE:
        return
    
    session = st.session_state
    
    # Get the pattern name for CSV lookup
    patterns = DISEASE_PATTERNS["감기"]["patterns"]
    idx = session.get("pattern_idx", 0)
    if 0 <= idx < len(patterns):
        pattern_name = patterns[idx]["name"]  # e.g., "풍한형" or "풍열형"
    else:
        pattern_name = None
    
    # Use CSV-based randomization
    success = randomize_from_csv_rules(st, "감기", pattern_name)
    if not success:
        print("Warning: CSV randomization failed for 감기, using fallback")


def _apply_csv_rhinitis_randomization(st):
    """Apply CSV-based randomization for Allergic Rhinitis (알레르기비염)."""
    if not CSV_RULES_AVAILABLE:
        return
    
    session = st.session_state
    
    # Get the pattern/prescription name for CSV lookup
    patterns = DISEASE_PATTERNS["알레르기비염"]["patterns"]
    idx = session.get("pattern_idx", 0)
    if 0 <= idx < len(patterns):
        # For rhinitis, we use prescription name as pattern (e.g., "소청룡탕")
        prescriptions = patterns[idx].get("prescriptions", [])
        pattern_name = prescriptions[0] if prescriptions else None
    else:
        pattern_name = None
    
    # Use CSV-based randomization
    success = randomize_from_csv_rules(st, "알레르기비염", pattern_name)
    if not success:
        print("Warning: CSV randomization failed for 알레르기비염, using fallback")
