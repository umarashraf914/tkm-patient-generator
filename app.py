import streamlit as st
import google.generativeai as genai
import json
import random

# --- STEP 1: IMPORT DATA MAPPINGS ---
from data_mappings import get_desc, get_weights, CLINICAL_DATA

import streamlit as st
import google.generativeai as genai

# --- 🔐 SECURE API KEY HANDLING ---
try:
    # This looks for the key in Streamlit's secret storage
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except FileNotFoundError:
    st.error("⚠️ API Key not found. Please set it in Streamlit Secrets.")
    st.stop() # Stop the app if no key is found

# --- CONFIGURATION ---
st.set_page_config(page_title="TKM Clinical Scenario Generator", layout="wide")

# --- SESSION STATE & DEFAULTS ---
# Based on Pages 17-19: Complete TKM Clinical Information Items (한의 임상정보 항목)
defaults = {
    # ===========================================
    # 인구학적정보 (Demographics) - Page 17
    # ===========================================
    "age": 45, "sex": "Male (남)", "job": "Manual Labor (현장직)",
    "height": 175, "weight": 70,  # 키, 몸무게 -> BMI calculated
    
    # ===========================================
    # 활력징후 (Vital Signs) - Page 18
    # ===========================================
    "sbp": 120, "dbp": 80, "temp": 36.5, "pulse_rate": 72, "resp": 18,

    # ===========================================
    # O/S 경과 (Onset/History) - Page 17
    # ===========================================
    "onset": "1 week ago (1주 전)",  # 증상 발현시점
    "course": "Worsening (악화중)",  # 경과
    "past_illness": [],  # 과거 질병 경험
    "past_cold_problem_area": [],  # 과거 감기증상 시 문제가 되는 부위
    "aggravating_factors": [],  # 악화요인
    "relieving_factors": [],  # 완화요인

    # ===========================================
    # 현병력 (Current Medical History) - Page 18
    # ===========================================
    "history_conditions": [],  # 고혈압, 당뇨, 이상지질혈증, 기타
    
    # ===========================================
    # 약물력 (Medication History) - Page 18
    # ===========================================
    "meds_specific": [],  # 혈압약, 당뇨약, 이상지질혈증약, 수면제, 항우울제, 항불안제
    
    # ===========================================
    # 가족력 (Family History) - Page 18
    # ===========================================
    "family_hx": [],  # 고혈압, 당뇨, 심장병, 중풍, 기타

    # ===========================================
    # 사회력 (Social History) - Page 18
    # ===========================================
    # 술 (Alcohol)
    "social_alcohol_freq": "None (비음주)",  # 월간 음주 횟수
    "social_alcohol_amt": 0.0,  # 1회당 음주량
    # 담배 (Smoking)
    "social_smoke_daily": 0.0,  # 일간 개피
    "social_smoke_years": 0,  # 총 흡연기간 (years)
    # 운동 (Exercise)
    "social_exercise_freq": 0,  # 주간 횟수
    "social_exercise_time": 0,  # 1회당 평균 운동 시간
    "social_exercise_int": "Medium (중)",  # 운동 강도

    # ===========================================
    # 여성력 (Women's Health) - Page 18 (가임기 여성 14-50세만)
    # ===========================================
    "mens_cycle": 28,  # 생리주기
    "mens_regular": "Regular (규칙)",  # 생리규칙성
    "mens_duration": 5,  # 생리기간
    "mens_amt": "Normal (보통)",  # 생리 양
    "mens_pain_score": 0,  # 생리통강도 (0-10)
    "mens_clot": False,  # 생리혈 덩어리여부
    "mens_color": "Red (적색)",  # 생리혈 색

    # ===========================================
    # 식사 (Diet) - Page 18
    # ===========================================
    "diet_freq": 3,  # 1일 식사횟수
    "diet_regular": "Regular (규칙적)",  # 식사 규칙성
    "diet_amt": "Normal (보통)",  # 1일 평균 식사량
    "diet_speed": "Normal (20min)",  # 1회 평균식사시간
    "digestion": "Normal (보통)",  # 소화여부/소화정도
    "appetite": "Normal",  # 입맛

    # ===========================================
    # 대변 (Stool) - Page 18-19
    # ===========================================
    "stool_freq": "1/day",  # 대변 횟수
    "stool_color": "Brown (황갈색)",  # 대변 색
    "stool_form": "Normal (보통)",  # 대변 굵기(형태)
    "stool_discomfort": False,  # 배변 후 불편감
    "stool_residual": 0,  # 배변 후 잔변감(강도) 0-5

    # ===========================================
    # 소변 (Urine) - Page 19
    # ===========================================
    "urine_freq_day": 5,  # 1일 소변 횟수
    "urine_freq_night": 0,  # 야간뇨 횟수
    "urine_color": "Yellow (황색)",  # 소변 색
    "urine_stream": "Normal (정상)",  # 소변 굵기(소변줄기)
    "urine_discomfort": False,  # 소변 후 불편감
    "urine_residual": False,  # 배뇨 후 잔뇨감
    "urine_residual_sev": 0,  # 잔뇨감 강도 0-5
    "urine_incontinence": False,  # 유뇨/요실금

    # ===========================================
    # 수면상태 (Sleep) - Page 19
    # ===========================================
    "sleep_waking_state": "Refreshed (개운함)",  # 기상시 상쾌도
    "sleep_hours": 7,  # 수면 시간
    "sleep_depth": "Deep (깊음)",  # 수면 깊이
    "insomnia_freq": 0,  # 불면 빈도 (0-5)
    "dreams": "Rare (거의 없음)",  # 꿈의 빈도 및 내용
    "insomnia_onset": False,  # 입면장애
    "insomnia_maintain": False,  # 수면 중도 각성
    "insomnia_maintain_count": 0,  # 수면 중도 각성 횟수
    "insomnia_reentry": False,  # 수면 중도 각성 후 재입면 장애

    # ===========================================
    # 땀 (Sweat) - Page 19
    # ===========================================
    "sweat_amt": "Normal (보통)",  # 일상 생활에서 땀 량
    "sweat_time": "Daytime (주간)",  # 땀나는 시간대
    "sweat_area": "General (전신)",  # 땀나는 부위
    "sweat_feeling": "Normal (상쾌)",  # 땀 흘린 뒤 느낌

    # ===========================================
    # 한열경향 (Cold/Heat Tendency) - Page 19
    # ===========================================
    "cold_heat_body": "Balanced (보통)",  # 인체 한열(몸이 차고 더운 정도)
    "cold_heat_distribution": "Even (균등)",  # 한열의 편재(상열하한)
    "drink_temp": "Warm (따뜻한 물)",  # 음료 온도 선호도
    "cold_sensitivity": 3,  # 주위 민감도 (1-5)
    "heat_sensitivity": 3,  # 더위 민감도 (1-5)
    "cold_heat_pref": "Balanced (보통)",  # Legacy compatibility

    # ===========================================
    # 전신상태 (General Condition) - Page 19
    # ===========================================
    "body_solidity": "Solid (단단)",  # 물살/단단
    "physical_strength": "Normal (보통)",  # 체력강약
    "fatigue_level": "Low (약함)",  # 피로감
    "edema": "None (없음)",  # 부종여부
    "bruising": "Normal (정상)",  # 인체 부위의 출혈/멍듦
    "condition_bad_area": [],  # 평소 컨디션이 안좋을 때 불편한 부위
    "limb_weakness": False,  # 사지 무력감

    # ===========================================
    # 피부상태 (Skin Condition) - Page 19
    # ===========================================
    "skin_trouble": False,  # 피부트러블
    "skin_dry": "Normal (정상)",  # 피부 건조도
    "skin_itch": False,  # 피부 가려움

    # ===========================================
    # 얼굴 (Face) - Page 17
    # ===========================================
    "face_color": "Normal",  # 얼굴 색
    "face_gloss": "Normal",  # 얼굴 광택

    # ===========================================
    # 눈 (Eyes) - Page 17
    # ===========================================
    "eye_discomfort": False,  # 눈 불편감
    "eye_red": False,  # 눈 충혈
    "vision_blackout": False,  # 눈 앞이 캄캄함

    # ===========================================
    # 귀 (Ears) - Page 17
    # ===========================================
    "tinnitus_freq": 0,  # 이명(빈도) 0-5
    "tinnitus_sev": 0,  # 이명(강도) 0-5
    "hearing_sev": 0,  # 이롱(난청) 0-5

    # ===========================================
    # 구강/목 (Mouth/Throat) - Page 17-18
    # ===========================================
    "lip_color": "Normal (정상)",  # 입술 색
    "lip_dry": False,  # 입술 건조
    "water_intake": "Normal (1-1.5L)",  # 음수량
    "mouth_dry": 0,  # 입마름 정도(구건/구갈) 0-5
    "throat_dry": False,  # 인후 건조
    "mouth_bitter": False,  # 구고(입이 씀)
    "bad_breath": False,  # 구취
    "hiccup": False,  # 딸꾹질

    # ===========================================
    # 어지러움 (Dizziness) - Page 18
    # ===========================================
    "dizziness_sev": 0,  # 어지러움(두훈) 0-5

    # ===========================================
    # 뒷목/경항부 (Neck/Nape) - Page 18
    # ===========================================
    "neck_nape_freq": 0,  # 뒷목, 경항 불편감(빈도) 0-5
    "neck_nape_sev": 0,  # 뒷목, 경항 불편감(강도) 0-5

    # ===========================================
    # 흉부 (Chest) - Page 18
    # ===========================================
    "breath_sound": "Normal (정상)",  # 호흡소리 크기
    "palpitation": 0,  # 흉부 두근거림 0-5
    "chest_tight_freq": 0,  # 흉부 답답함(빈도) 0-5
    "chest_tight_sev": 0,  # 흉부 답답함(강도) 0-5
    "chest_pain_freq": 0,  # 흉부 통증(빈도) 0-5
    "chest_pain_sev": 0,  # 흉부 통증(강도) 0-5
    "sighing_freq": 0,  # 한숨 빈도 0-5
    "nausea": 0,  # 구역감/구토 0-5
    "bloating": 0,  # 복만/가스 참(강도) 0-5
    "flatulence": "Normal (보통)",  # 방귀

    # ===========================================
    # 기능성 소화불량 (Functional Dyspepsia) - Page 18
    # ===========================================
    "lower_abd_discomfort": 0,  # 아랫배 불편감(강도) 0-5
    "abd_pain_sev": 0,  # 전복부 통증(강도) 0-5
    "abd_pain_type": "None",  # 복통의 양상
    "abd_tenderness": False,  # 눌렀을 때 복부 압통
    "nausea_sev": 0,  # 메스꺼움(강도) 0-5
    "belching": 0,  # 트림 0-5
    "belching_smell": "None (없음)",  # 트림 시 냄새
    "food_stag_sev": 0,  # 체한(강도) 0-5
    "abd_muscle_tension": False,  # 복직근 긴장감
    "abd_mass": False,  # 복부 덩어리 만져짐
    "abd_pulsation": False,  # 동계
    "bowel_sound": "Normal (정상)",  # 장명(장에서 나는 소리)

    # ===========================================
    # 옆구리/등/골반 (Flank/Back/Pelvis) - Page 18
    # ===========================================
    "flank_freq": 0, "flank_sev": 0,  # 옆구리 불편감
    "back_freq": 0, "back_sev": 0,  # 등 불편감
    "pelvis_freq": 0, "pelvis_sev": 0,  # 골반부 불편감

    # ===========================================
    # 어깨/팔꿈치/손,발 (Shoulder/Elbow/Hands,Feet) - Page 18
    # ===========================================
    "shoulder_freq": 0, "shoulder_sev": 0,  # 어깨 불편감
    "elbow_freq": 0, "elbow_sev": 0,  # 팔꿈치 불편감
    "hand_foot_freq": 0, "hand_foot_sev": 0,  # 손 또는 발 불편감
    "cold_hands_feet": False,  # 수족냉증(손발냉감)

    # ===========================================
    # 고관절/무릎 (Hip/Knee) - Page 18
    # ===========================================
    "leg_discomfort": 0,  # 다리 불편감 0-5
    "knee_freq": 0, "knee_sev": 0,  # 슬부 불편감

    # ===========================================
    # 정신상태 (Mental State) - Page 19
    # ===========================================
    "mental_clarity": "Clear (맑음)",  # 정신상태
    "memory": "Good (좋음)",  # 기억력
    "motivation": "Normal (보통)",  # 의욕
    "stress_coping": "Average (보통)",  # 스트레스 대처력
    "mood_swing": "Stable (안정)",  # 감정 기복

    # ===========================================
    # 성격/성양 (Personality) - Page 19
    # ===========================================
    "personality_speed": 3,  # 성격 완급(느긋함/급함) 1-5
    "personality_soft": 3,  # 성격 강유(부드러움/강함) 1-5
    "personality_io": 3,  # 성격내외(내성적/외향적) 1-5
    "personality_static": 3,  # 성격 동정(정적/동적) 1-5

    # ===========================================
    # 감정상태 (Emotional State) - Page 19
    # ===========================================
    "voice_vol": "Normal (보통)",  # 목소리크기(성음크기)
    "excitement": 3,  # 흥분정도(차분함) 1-5
    "emot_anger": 1,  # 노(화냄/평온) 1-5
    "emot_depress": 1,  # 우울(우울함) 1-5
    "emot_anxiety": 1,  # 불안 1-5
    "emot_fear": 1,  # 공(두려움/용기) 1-5
    "emot_startle": 1,  # 놀람(잘놀람/평온함) 1-5
    "emot_thought": 1,  # 생각(생각많음/적음) 1-5
    "emot_grief": 1,  # 비탄(슬픔많음/적음) 1-5

    # ===========================================
    # 맥 (Pulse Diagnosis) - Page 19
    # ===========================================
    "pulse_depth": "Middle (중)",  # 맥 부침 정도(부침)
    "pulse_width": "Medium (대)",  # 맥 폭 정도(대세)
    "pulse_length": "Medium (장)",  # 맥 길이 정도(장단)
    "pulse_smooth": "Normal (완)",  # 맥 부드럽고 거친 정도(활삽)
    "pulse_strength": "Moderate (유력)",  # 세기
    "pulse_tension": "Soft (유)",  # 맥 긴장도(현긴완)

    # ===========================================
    # 설 (Tongue) - Page 19
    # ===========================================
    "tongue_color": "Pale Red (담홍)",  # 혀 색
    "tongue_size": "Normal (정상)",  # 혀 크기
    "tongue_marks": False,  # 혀 흔적/치흔

    # ===========================================
    # 태 (Tongue Coat) - Page 19
    # ===========================================
    "tongue_coat_color": "White (백태)",  # 설태 색
    "tongue_coat_thick": "Thin (박태)",  # 설태 두께
    "tongue_coat_particle": "Fine (윤)",  # 설태 입자크기

    # ===========================================
    # PAIN GRID (통증 부위별 빈도/강도)
    # ===========================================
    "pain_neck": [0,0], "pain_shoulder": [0,0], "pain_back": [0,0], "pain_knee": [0,0],
    "pain_hand": [0,0], "pain_elbow": [0,0], "pain_flank": [0,0], "pain_pelvis": [0,0], "pain_hip": [0,0],
    # Pain grid _f (frequency) and _i (intensity) individual keys for Streamlit widgets
    "pain_neck_f": 0, "pain_neck_i": 0,
    "pain_shoulder_f": 0, "pain_shoulder_i": 0,
    "pain_back_f": 0, "pain_back_i": 0,
    "pain_knee_f": 0, "pain_knee_i": 0,
    "pain_hand_f": 0, "pain_hand_i": 0,
    "pain_elbow_f": 0, "pain_elbow_i": 0,
    "pain_flank_f": 0, "pain_flank_i": 0,
    "pain_pelvis_f": 0, "pain_pelvis_i": 0,
    "pain_hip_f": 0, "pain_hip_i": 0,

    # ===========================================
    # 한의사 진찰 및 검사소견 (TKM Examinations) - Page 17
    # ===========================================
    "exam_lung_sound": None,  # 호흡음(폐음) 진찰
    "exam_throat": None,  # 인후부 진찰
    "exam_tonsil": None,  # 편도진찰
    "exams": [],  # X-ray, 이경, 비경, 혈액검사, CT, MRI, 내시경
    "exam_xray": None,  # X-ray
    "exam_otoscope": None,  # 이경
    "exam_rhinoscope": None,  # 비경
    "exam_blood_test": None,  # 혈액검사
    "exam_ct": None,  # CT
    "exam_mri": None,  # MRI
    "exam_endoscopy": None,  # 내시경

    # ===========================================
    # DIAGNOSIS & SPECIFICS (진단 및 특이사항)
    # ===========================================
    "disease": "Common Cold (Acute URI) - 감기",
    "pattern_idx": 0,
    
    # Cold Specifics (감기 특이사항) - Page 15
    "fever_sev": 1, "chills_sev": 1, "snot_sev": 1, "cough_sev": 1,
    "phlegm_amt": 0,  # 가래 양
    "phlegm_color": "None",  # 가래 색
    "sweating": False,  # 무한/유한
    "cold_symptoms_spec": [],
    
    # Rhinitis Specifics (비염 특이사항)
    "sneeze_sev": 1, "nose_block_sev": 1, "nose_itch_sev": 1, 
    "snot_type": "Clear/Watery (맑은 콧물)",
    
    # Back Pain Specifics (요통 특이사항) - Page 15-16
    "pain_sev": 1,
    "pain_nature": [],
    "back_pain_cause": "None",  # 발병 요인
    "back_pain_timing": "Constant",  # 통증 시간대
    "back_radiation": False,  # 다리로 방사
    
    # Dyspepsia Specifics (소화불량 특이사항) - Page 16
    "dyspepsia_spec": [],
    "acid_reflux": False,  # 신물
    "bitter_taste": False,  # 구고
    "foul_belch": False,  # 부패취
    "epigastric_pain": 0,  # 명치 통증 0-5
    "cold_limbs_dyspepsia": False  # 수족냉증
}

# ===========================================
# KCD CODE MAPPINGS (Pages 21-22)
# 대표질병과 KCD 코드 매핑
# ===========================================
KCD_CODES = {
    "감기": {
        "main_code": "J06",
        "sub_codes": {
            "J06.0": "급성 후두인두염 (Acute laryngopharyngitis)",
            "J06.8": "여러부위의 기타 급성 상기도감염 (Other acute upper respiratory infections of multiple sites)",
            "J06.9": "상세불명의 급성 상기도감염 (Acute upper respiratory infection unspecified)"
        },
        "exclusions": [
            "J22 - 급성호흡기감염 NOS (Acute respiratory infection NOS)",
            "J09, J10.1 - 인플루엔자바이러스 확인됨 (Influenza virus identified)",
            "J11.1 - 인플루엔자바이러스 미확인 (Influenza virus not identified)",
            "J98.7 - 호흡기감염 NOS (Respiratory infection NOS)"
        ]
    },
    "알레르기비염": {
        "main_code": "J30",
        "sub_codes": {
            "J30.0": "혈관운동성비염 (Vasomotor rhinitis)",
            "J30.1": "화분에 의한 알레르기비염 (Allergic rhinitis due to pollen, Hay fever, Pollinosis)",
            "J30.2": "기타 계절성 알레르기비염 (Other seasonal allergic rhinitis)",
            "J30.3": "기타 알레르기비염 (Other allergic rhinitis)",
            "J30.4": "다년성 알레르기비염/상세불명 (Perennial allergic rhinitis, unspecified)"
        },
        "exclusions": [
            "J45.0- 천식을 동반한 알레르기비염 (Allergic rhinitis with asthma)"
        ]
    },
    "요통": {
        "main_code": "M54",
        "sub_codes": {
            "M54.5": "등통증 (Dorsalgia)",
            "M54.50": "척추의 여러 부위 (Low back pain, multiple sites in spine)",
            "M54.55": "흉요추부 (Low back pain, thoracolumbar region)",
            "M54.56": "요추부 (Low back pain, lumbar region)",
            "M54.57": "요천부 (Low back pain, lumbosacral region)",
            "M54.58": "천추 및 천미추부 (Low back pain, sacral and sacrococcygeal region)",
            "M54.59": "상세불명의 부위 (Low back pain, site unspecified)"
        },
        "exclusions": [
            "M51.2 - 추간판 전위로 인한 요통 (Lumbago due to intervertebral disc displacement)",
            "M54.4 - 좌골신경통을 동반한 요통 (Lumbago with sciatica)"
        ]
    },
    "기능성소화불량": {
        "main_code": "K30",
        "sub_codes": {
            "K30": "기능성소화불량 (Functional dyspepsia)"
        },
        "exclusions": [
            "R10.19 - 상세불명 (NOS)",
            "F45.3 - 신경성/심인성 (Nervous, Neurotic, Psychogenic)",
            "R12 - 속쓰림 (Heartburn)"
        ]
    }
}

# ===========================================
# PATTERN CLASSIFICATION (Page 23)
# 질병별 변증유형 분류
# ===========================================
DISEASE_PATTERNS = {
    "감기": {
        "patterns": [
            {"id": "Cold_WC", "name": "풍한형 (Wind-Cold)", "prescriptions": ["행소산", "삼소음", "소청룡탕"]},
            {"id": "Cold_WH", "name": "풍열형 (Wind-Heat)", "prescriptions": ["은교산", "상국음", "연교패독산"]}
        ],
        "note": "상기도 감염의 경우 통상 급성임을 감안하여 풍한형과 풍열형 변증을 선정"
    },
    "알레르기비염": {
        "patterns": [
            {"id": "R_Fluid", "name": "수체형 (Fluid Retention)", "prescriptions": ["월비가반하탕", "사간마황탕", "소청룡탕", "영감강미신하인탕", "마황부자세신탕"]}
        ],
        "note": "다양한 변증형 중 수체형 알러지 비염을 단일로 선정"
    },
    "요통": {
        "patterns": [
            {"id": "BP_Cold", "name": "한증형 (Cold)", "prescriptions": ["오적산"]},
            {"id": "BP_Heat", "name": "열증형 (Heat)", "prescriptions": ["이묘창백산", "칠묘창백산"]},
            {"id": "BP_QiDef", "name": "기허형 (Qi Deficiency)", "prescriptions": ["두충환", "사군자탕"]},
            {"id": "BP_YangDef", "name": "양허형 (Yang Deficiency)", "prescriptions": ["팔미지황원"]},
            {"id": "BP_YinDef", "name": "음허형 (Yin Deficiency)", "prescriptions": ["육미지황원"]},
            {"id": "BP_FoodStag", "name": "식적형 (Food Stagnation)", "prescriptions": ["소적건비환"]},
            {"id": "BP_Phlegm", "name": "담음형 (Phlegm-Fluid)", "prescriptions": ["이진탕", "궁하탕"]},
            {"id": "BP_QiStag", "name": "기체형 (Qi Stagnation)", "prescriptions": ["칠기탕", "소간해울탕"]},
            {"id": "BP_BloodStasis", "name": "어혈형 (Blood Stasis)", "prescriptions": ["서근산", "독활탕"]}
        ],
        "note": "질병에 따라 증형이 달라지는 어려움을 배제하기 위해 팔강변증의 카테고리에서 한열허실을 구분"
    },
    "소화불량": {
        "patterns": [
            {"id": "DY_Cold", "name": "한증형 (Cold)", "prescriptions": ["오적산"]},
            {"id": "DY_Heat", "name": "열증형 (Heat)", "prescriptions": ["이묘창백산", "칠묘창백산"]},
            {"id": "DY_QiDef", "name": "기허형 (Qi Deficiency)", "prescriptions": ["두충환", "사군자탕"]},
            {"id": "DY_YangDef", "name": "양허형 (Yang Deficiency)", "prescriptions": ["팔미지황원"]},
            {"id": "DY_YinDef", "name": "음허형 (Yin Deficiency)", "prescriptions": ["육미지황원"]},
            {"id": "DY_FoodStag", "name": "식적형 (Food Stagnation)", "prescriptions": ["소적건비환"]},
            {"id": "DY_Phlegm", "name": "담음형 (Phlegm-Fluid)", "prescriptions": ["이진탕", "궁하탕"]},
            {"id": "DY_QiStag", "name": "기체형 (Qi Stagnation)", "prescriptions": ["칠기탕", "소간해울탕"]},
            {"id": "DY_BloodStasis", "name": "어혈형 (Blood Stasis)", "prescriptions": ["서근산", "독활탕"]}
        ],
        "note": "요통과 동일한 한열허실 구분 적용"
    }
}

# Helper function to get pattern info
def get_pattern_info(disease_key, pattern_idx):
    """Get pattern details including name and prescriptions."""
    if disease_key in DISEASE_PATTERNS:
        patterns = DISEASE_PATTERNS[disease_key]["patterns"]
        if 0 <= pattern_idx < len(patterns):
            return patterns[pattern_idx]
    return None

def get_kcd_info(disease_key):
    """Get KCD code information for a disease."""
    return KCD_CODES.get(disease_key, None)

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- STEP 2: WEIGHTED RANDOMIZATION FUNCTION ---
# This replaces random.randint with probability-based selection from the PDF
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


# --- STEP 3: CONSTRAINT LOGIC (RULES ENGINE) ---
# Fixes "impossible" combinations based on clinical logic (Pages 26-28)
# AND enforces KTAS safety rules (Emergency Exclusion)
def apply_constraint_rules():
    """
    Apply medical logic constraints to ensure realistic symptom combinations.
    Call this AFTER randomization to fix inconsistencies.
    
    CRITICAL: Enforces KTAS 1-2 exclusion rules for patient safety.
    
    가상환자 생성규칙 설정 (Virtual Patient Generation Rules):
    - 응급상황 배제 (KTAS 1-2 레벨 제외)
    - 임상적 모순 해결 (Clinical inconsistencies)
    - 변증별 증상 논리 (Pattern-specific symptom logic)
    """
    # ===========================================
    # KTAS EMERGENCY EXCLUSION RULES (CRITICAL!)
    # 응급상황 배제 기준 (KTAS Level 1-2 exclusion)
    # ===========================================
    
    # Rule: SBP must be 90-180 mmHg (exclude <90 hypotension/shock, >180 hypertensive crisis)
    # 수축기혈압: 90 미만 저혈압/쇼크, 180 초과 고혈압 위기 제외
    if st.session_state.sbp < 90:
        st.session_state.sbp = random.randint(95, 130)
    if st.session_state.sbp > 180:
        st.session_state.sbp = random.randint(120, 170)
    
    # Rule: DBP safe range 60-110 mmHg
    # 이완기혈압: 60-110 범위 유지
    if st.session_state.dbp < 60:
        st.session_state.dbp = random.randint(65, 85)
    if st.session_state.dbp > 110:
        st.session_state.dbp = random.randint(70, 100)
    
    # Rule: DBP must be less than SBP (by at least 20)
    # 맥압 유지: DBP는 SBP보다 최소 20 낮아야 함
    if st.session_state.dbp >= st.session_state.sbp:
        st.session_state.dbp = st.session_state.sbp - random.randint(20, 40)
    
    # Rule: HR must be 50-130 bpm (exclude <50 bradycardia, >130 tachycardia)
    # 심박수: 50 미만 서맥, 130 초과 빈맥 제외
    if st.session_state.pulse_rate < 50:
        st.session_state.pulse_rate = random.randint(55, 75)
    if st.session_state.pulse_rate > 130:
        st.session_state.pulse_rate = random.randint(70, 120)
    
    # Rule: RR must be 10-30/min (exclude <10 or >30 respiratory failure)
    # 호흡수: 10 미만 또는 30 초과 호흡부전 제외
    if st.session_state.resp < 10:
        st.session_state.resp = random.randint(12, 18)
    if st.session_state.resp > 30:
        st.session_state.resp = random.randint(16, 24)
    
    # Rule: Temperature must be 35.0-40.5°C (exclude hypothermia <35, hyperthermia >40.5)
    # 체온: 35°C 미만 저체온증, 40.5°C 초과 고체온증 제외
    if st.session_state.temp < 35.0:
        st.session_state.temp = round(random.uniform(36.0, 37.0), 1)
    if st.session_state.temp > 40.5:
        st.session_state.temp = round(random.uniform(37.5, 39.5), 1)
    
    # Rule: Pain NRS must be < 8 (exclude severe pain ≥8 which is KTAS Level 3+)
    # 통증 NRS: 8 이상 심한 통증 제외 (KTAS Level 3 이상)
    if st.session_state.pain_sev >= 8:
        st.session_state.pain_sev = random.randint(3, 7)
    
    # Rule: Exclude severe dizziness/neurological symptoms (KTAS emergency)
    # 심한 어지러움/신경학적 증상 제외 (의식장애 레벨)
    if st.session_state.dizziness_sev >= 5 and st.session_state.vision_blackout:
        st.session_state.dizziness_sev = random.randint(2, 4)
        st.session_state.vision_blackout = False
    
    # ===========================================
    # FEVER-TEMPERATURE CONSISTENCY
    # 발열-체온 일관성 규칙
    # ===========================================
    # Rule: High Fever (level 4-5) must have elevated temp (but under 40.5)
    # 고열 (레벨 4-5)은 38°C 이상 필수 (단, 40.5 이하 유지)
    if st.session_state.fever_sev >= 4 and st.session_state.temp < 38.0:
        st.session_state.temp = round(random.uniform(38.0, 39.5), 1)
    
    # Rule: Low/No Fever should have normal temperature
    # 미열/무열은 정상 체온 유지
    if st.session_state.fever_sev <= 2 and st.session_state.temp >= 38.5:
        st.session_state.temp = round(random.uniform(36.0, 37.3), 1)
    
    # Rule: Medium fever (level 3) = mild temp elevation
    # 중등도 발열 (레벨 3)은 미열 범위
    if st.session_state.fever_sev == 3 and (st.session_state.temp < 37.4 or st.session_state.temp >= 38.5):
        st.session_state.temp = round(random.uniform(37.4, 38.4), 1)
    
    # ===========================================
    # WOMEN'S HEALTH CONSTRAINTS
    # 여성건강 제약조건 (여성 14-50세만 적용)
    # ===========================================
    if st.session_state.sex == "Female (여)":
        # Women's health only applies to ages 14-50
        if st.session_state.age < 14 or st.session_state.age > 50:
            # Reset women's health to N/A or defaults for non-applicable ages
            st.session_state.mens_regular = "Menopause" if st.session_state.age > 50 else "N/A"
            st.session_state.mens_pain_score = 0
            st.session_state.mens_duration = 0
        else:
            # Valid menstrual age - ensure consistent values
            if st.session_state.mens_regular == "Menopause":
                st.session_state.mens_regular = random.choice(["Regular", "Irregular"])
    else:
        # Male patients - reset all women's health variables
        st.session_state.mens_pain_score = 0
        st.session_state.mens_duration = 0
    
    # ===========================================
    # SNOT/RHINITIS CONSTRAINTS
    # 콧물/비염 일관성 규칙
    # ===========================================
    # Rule: No Snot means Clear/None type
    # 콧물 없음 = 맑음/없음 타입
    if st.session_state.snot_sev <= 1:
        st.session_state.snot_type = "Clear/Watery (맑음/물)"
    
    # Rule: Severe snot (level 4-5) should not be "None"
    # 심한 콧물 (레벨 4-5)은 "없음"일 수 없음
    if st.session_state.snot_sev >= 4 and "Clear" in st.session_state.snot_type:
        # Keep clear for cold patterns, but ensure consistency
        pass  # Clear can be severe in cold patterns
    
    # ===========================================
    # MENTAL/APPETITE CONSTRAINTS
    # 정신/식욕 일관성 규칙
    # ===========================================
    # Rule: No appetite + High motivation is impossible
    # 식욕 없음 + 높은 의욕은 불가
    if st.session_state.appetite == "None" and st.session_state.motivation == "High (높음)":
        st.session_state.motivation = "Low (낮음)"
    
    # Rule: Severe fatigue should lower motivation
    # 심한 피로는 의욕 저하 유발
    if st.session_state.fatigue_level == "Severe (심함)" and st.session_state.motivation == "High (높음)":
        st.session_state.motivation = random.choice(["Normal (보통)", "Low (낮음)"])
    
    # Rule: Poor memory + High stress coping is inconsistent
    # 나쁜 기억력 + 좋은 스트레스 대처는 모순
    if st.session_state.memory == "Bad (나쁨)" and st.session_state.stress_coping == "Good (좋음)":
        st.session_state.stress_coping = random.choice(["Average (보통)", "Poor (나쁨)"])
    
    # ===========================================
    # BMI/BODY COMPOSITION CONSTRAINTS
    # BMI/체형 일관성 규칙
    # ===========================================
    # Calculate BMI and ensure reasonable body solidity
    height_m = st.session_state.height / 100
    bmi = st.session_state.weight / (height_m * height_m)
    
    if bmi < 18.5 and st.session_state.body_solidity == "Solid (단단)":
        st.session_state.body_solidity = "Soft (물렁)"
    if bmi > 30 and st.session_state.body_solidity == "Soft (물렁)":
        st.session_state.body_solidity = random.choice(["Normal (보통)", "Solid (단단)"])
    
    # ===========================================
    # COLD PATTERN CONSTRAINTS (감기 변증) - Page 15
    # Based on: 감기환자 변증지표 중요도 항목-임상진료지침
    # ===========================================
    if "Cold" in st.session_state.disease:
        current_pattern = st.session_state.pattern_idx
        
        if current_pattern == 0:  # Wind-Cold (풍한)
            # Page 15: 오한이 심하고 땀이 없다 (惡寒重, 無汗)
            # Severe chills, no sweating
            if st.session_state.fever_sev > st.session_state.chills_sev:
                st.session_state.chills_sev, st.session_state.fever_sev = st.session_state.fever_sev, st.session_state.chills_sev
            # Page 15: 맑고 옅은 흰색 가래 (稀薄白色白)
            # Thin, white phlegm
            st.session_state.tongue_coat_color = "White"
            st.session_state.phlegm_color = "White/Clear (희박/맑음)"
            # Page 15: 무한 (no sweating)
            st.session_state.sweating = False
            st.session_state.sweat_amt = "None (무한)"
            # Page 15: 관절 통증(骨節疼痛)
            if random.random() < 0.6:
                if "Joint Pain (관절통)" not in st.session_state.cold_symptoms_spec:
                    st.session_state.cold_symptoms_spec.append("Joint Pain (관절통)")
            # Cold preference (찬 것 싫어함)
            if st.session_state.drink_temp == "Icy":
                st.session_state.drink_temp = random.choice(["Warm", "Hot"])
                
        elif current_pattern == 1:  # Wind-Heat (풍열)
            # Page 15: 身熱 (body heat/fever dominant)
            if st.session_state.chills_sev > st.session_state.fever_sev:
                st.session_state.chills_sev, st.session_state.fever_sev = st.session_state.fever_sev, st.session_state.chills_sev
            # Page 15: 가래가 누렇고 끈적함 (痰稠, 黃稠)
            # Yellow, sticky phlegm
            st.session_state.tongue_coat_color = random.choice(["White", "Yellow"])
            st.session_state.phlegm_color = "Yellow/Sticky (황담/끈적)"
            # Page 15: 기타 증상 없음 noted, but sweating occurs
            st.session_state.sweating = True
            if st.session_state.sweat_amt == "None (무한)":
                st.session_state.sweat_amt = "Normal (보통)"
            # Heat preference (찬 것 선호)
            if st.session_state.drink_temp == "Hot":
                st.session_state.drink_temp = random.choice(["Warm", "Icy"])
                
        elif current_pattern == 2:  # Wind-Dryness (풍조/풍燥-온燥)
            # Page 15: 약한/발열 없음 (mild chills or no fever)
            st.session_state.fever_sev = random.randint(1, 2)
            st.session_state.chills_sev = random.randint(1, 2)
            # Page 15: 기침이 적거나 가래 배출이 인후가 건조하고 아프다
            # Dry cough, little phlegm, dry/painful throat
            st.session_state.phlegm_amt = random.randint(0, 1)
            st.session_state.throat_dry = True
            st.session_state.lip_dry = True
            # Page 15: 적다 (咳嗽少痰) 또는 객혈 다(咽乾, 咽痛)
            if st.session_state.skin_dry == "Normal (정상)":
                st.session_state.skin_dry = random.choice(["Dry (건조)", "Scaly (각질)"])
            # Dry mouth
            st.session_state.mouth_dry = random.randint(2, 4)
    
    # ===========================================
    # RHINITIS PATTERN CONSTRAINTS (비염 변증)
    # ===========================================
    if "Rhinitis" in st.session_state.disease:
        if st.session_state.pattern_idx == 0:  # Yuebi (월비가반하탕) - 열/점성
            # Yellow/thick snot, heat signs
            st.session_state.snot_type = "Yellow/Thick (누렇고 찐득)"
            if st.session_state.tongue_coat_color == "White":
                st.session_state.tongue_coat_color = "Yellow"
                
        elif st.session_state.pattern_idx == 1:  # Shegan (사간마황탕) - 한/천식
            # Clear snot with respiratory symptoms
            st.session_state.snot_type = random.choice(["Clear/Watery (맑음/물)", "White/Sticky (희고 끈적)"])
            
        elif st.session_state.pattern_idx == 2:  # Minor Blue Dragon (소청룡탕) - 한/수양
            # Clear watery discharge is key sign
            # 소청룡탕 핵심: 맑은 콧물이 줄줄
            st.session_state.snot_type = "Clear/Watery (맑음/물)"
            st.session_state.tongue_coat_color = "White"
            # Cold signs
            if st.session_state.cold_heat_pref == "Heat Sens":
                st.session_state.cold_heat_pref = random.choice(["Cold Sens", "Balanced"])
                
        elif st.session_state.pattern_idx == 3:  # Ling-Gan (영강감미신하인탕) - 한/허
            # Cold deficiency pattern
            st.session_state.snot_type = "Clear/Watery (맑음/물)"
            st.session_state.cold_heat_pref = "Cold Sens"
            st.session_state.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
            
        elif st.session_state.pattern_idx == 4:  # Mahuang-Fuzi (마황부자세신탕) - 신양허
            # Kidney Yang deficiency: cold hands/feet, fatigue
            # 신양허: 수족냉, 피로
            st.session_state.cold_hands_feet = True
            st.session_state.cold_heat_pref = "Cold Sens"
            st.session_state.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
    
    # ===========================================
    # SLEEP CONSTRAINTS (수면 일관성)
    # ===========================================
    # Rule: Very poor sleep affects waking state
    # 수면 부족은 기상 상태에 영향
    if st.session_state.sleep_hours <= 4:
        st.session_state.sleep_waking_state = random.choice(["Tired", "Heavy"])
    
    # Rule: Good sleep hours should feel refreshed
    # 충분한 수면은 개운함
    if st.session_state.sleep_hours >= 8 and st.session_state.sleep_depth == "Deep (깊음)":
        st.session_state.sleep_waking_state = "Refreshed"
    
    # Rule: Insomnia = shallow sleep
    # 불면증 = 얕은 잠
    if st.session_state.insomnia_onset or st.session_state.insomnia_maintain:
        st.session_state.sleep_depth = "Shallow/Light (얕음)"
    
    # Rule: Frequent night urination = poor sleep
    # 야간뇨 빈번 = 수면 질 저하
    if st.session_state.urine_freq_night >= 3:
        st.session_state.sleep_depth = "Shallow/Light (얕음)"
        if st.session_state.sleep_waking_state == "Refreshed":
            st.session_state.sleep_waking_state = "Tired"
    
    # Rule: Frequent dreams/nightmares = shallow sleep
    # 꿈 많음/악몽 = 얕은 잠
    if st.session_state.dreams in ["Frequent (자주)", "Nightmares (악몽)"]:
        st.session_state.sleep_depth = "Shallow/Light (얕음)"
    
    # ===========================================
    # EXCRETION CONSTRAINTS (배설 일관성)
    # ===========================================
    # Rule: Constipation + Loose stool is inconsistent
    if st.session_state.stool_freq == "Constipation" and st.session_state.stool_form == "Loose":
        st.session_state.stool_form = "Hard"
    
    # Rule: Frequent stool (2-3/day) shouldn't be hard
    if st.session_state.stool_freq == "2-3/day" and st.session_state.stool_form == "Hard":
        st.session_state.stool_form = random.choice(["Normal", "Loose"])
    
    # ===========================================
    # PULSE-TONGUE CONSISTENCY (맥-설 일관성)
    # ===========================================
    # Rule: Strong pulse + Pale tongue (deficiency sign) is rare
    if st.session_state.pulse_strength == "Strong" and st.session_state.tongue_color == "Pale":
        st.session_state.tongue_color = random.choice(["Pale Red", "Red"])
    
    # Rule: Weak pulse + Red tongue (heat sign) is inconsistent  
    if st.session_state.pulse_strength == "Weak" and st.session_state.tongue_color == "Red":
        st.session_state.tongue_color = random.choice(["Pale", "Pale Red"])
    
    # ===========================================
    # BACK PAIN CONSTRAINTS (요통 변증) - Pages 15-16
    # Based on: 요통환자 변증지표 중요도 항목-임상진료지침
    # ===========================================
    if "Back Pain" in st.session_state.disease:
        # Ensure pain severity is capped at 7 per KTAS rules
        if st.session_state.pain_sev >= 7:
            st.session_state.pain_sev = 7
        
        # Ensure back pain is present for back pain diagnosis
        if st.session_state.pain_back[0] < 3:
            st.session_state.pain_back = [random.randint(3, 5), st.session_state.pain_sev]
            st.session_state.pain_back_f = st.session_state.pain_back[0]
            st.session_state.pain_back_i = st.session_state.pain_back[1]
        
        current_pattern = st.session_state.pattern_idx
        pain_nature_list = st.session_state.get("pain_nature", [])
        
        if current_pattern == 0:  # 신허 (Kidney Deficiency)
            # Page 15: 성생활 또는 신(腎)이 상통증 양상이 쉽지 않고 지속
            # Continuous ache, hard to move, sexual overexertion cause
            st.session_state.back_pain_cause = "Kidney Deficiency (신허)"
            # Page 15: 舌大 (설대, 혀가 급) - Large tongue
            st.session_state.tongue_size = "Enlarged (대)"
            # Page 15: 맥가급 - Thin-rapid pulse
            st.session_state.pulse_width = "Thin"
            st.session_state.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
            
        elif current_pattern == 1:  # 담음 (Phlegm)
            # Page 15: 뼈골이 둥둥한다. 통증이 경락을 따라 상하로 돌아다님
            # Bone feels heavy, pain radiates up/down along meridians
            st.session_state.back_pain_cause = "No Specific Cause (발병 요인 없음)"
            if "Moving (유주통) - Phlegm" not in pain_nature_list:
                st.session_state.pain_nature.append("Moving (유주통) - Phlegm")
            # Page 15: 맥滑 또는 伏 (맥활 또는 복) - Slippery or hidden pulse
            st.session_state.pulse_smooth = "Smooth (활)"
            
        elif current_pattern == 2:  # 식적 (Food Stagnation)
            # Page 15: 음주나 과식 등으로 인해 발생
            # Caused by overeating/alcohol
            st.session_state.back_pain_cause = "Overeating/Alcohol (음주/과식)"
            # Page 15: 허리를 구부리고 펴기가 어렵다
            # Difficulty bending/straightening
            # Page 15: 맥滑 (맥활) - Slippery pulse
            st.session_state.pulse_smooth = "Smooth (활)"
            # Associated with digestive issues
            st.session_state.appetite = random.choice(["None", "Low"])
            st.session_state.bloating = random.randint(2, 4)
            
        elif current_pattern == 3:  # 기 (Qi)
            # Page 15: 자기 뜻대로 되지 않은 오래 서 있거나 오래 걸으면 통증이 심화
            # Frustration cause, worse with standing/walking
            st.session_state.back_pain_cause = "Frustration/Stress (울체)"
            if "Worse Standing (오래 서있으면 악화) - Qi" not in pain_nature_list:
                st.session_state.pain_nature.append("Worse Standing (오래 서있으면 악화) - Qi")
            # Page 15: 맥沈伏 또는 弦 (맥침복 또는 현) - Sinking-hidden or wiry pulse
            st.session_state.pulse_depth = "Sinking"
            st.session_state.pulse_tension = random.choice(["Tense (긴)", "Normal"])
            
        elif current_pattern == 4:  # 좌섬 (Sprain)
            # Page 15: 무거운 것을 들다가 힘에 겨워 허리를 상했거나 삐
            # Lifting heavy things, injury
            st.session_state.back_pain_cause = "Injury/Sprain (좌섬/외상)"
            # Page 15: 요통 양상 없음 - sudden onset
            st.session_state.onset = random.choice(["1 day ago", "2-3 days ago"])
            # Page 15: 맥沈伏이면서 實 (맥침복 實) - Sinking-hidden, replete pulse
            st.session_state.pulse_depth = "Sinking"
            st.session_state.pulse_strength = "Strong"
            
        elif current_pattern == 5:  # 어혈 (Blood Stasis)
            # Page 15: 넘어졌거나 맞았거나 떨어져서 생긴 요통
            # Fall, hit, or chronic injury
            st.session_state.back_pain_cause = "Trauma/Fall (외상/낙상)"
            # Page 15: 낮에는 덜 아프고 밤에 더 아프다. 찌르듯이 아프다
            # Less pain during day, worse at night; stabbing pain
            st.session_state.back_pain_timing = "Worse at Night (야간 악화)"
            if "Stabbing (자통) - Blood Stasis" not in pain_nature_list:
                st.session_state.pain_nature.append("Stabbing (자통) - Blood Stasis")
            if "Worse at Night (야간통) - Blood Stasis" not in pain_nature_list:
                st.session_state.pain_nature.append("Worse at Night (야간통) - Blood Stasis")
            # Page 15: 맥澀 (맥삽) - Choppy pulse
            st.session_state.pulse_smooth = "Rough (삽)"
            st.session_state.tongue_color = random.choice(["Dark Red", "Pale Red"])
            
        elif current_pattern == 6:  # 풍 (Wind)
            # Page 16: 허리가 일정한 곳이 아프지 않고 왼쪽 혹은 오른쪽이 아프며
            # Pain moves around, doesn't stay fixed; may radiate to legs
            st.session_state.back_pain_cause = "No Specific Cause (발병 요인 없음)"
            if "Moving (유주통) - Phlegm" not in pain_nature_list:
                st.session_state.pain_nature.append("Moving (유주통) - Phlegm")
            st.session_state.back_radiation = True  # 두 다리가 당긴다
            # Page 16: 맥浮 (맥부) - Floating pulse
            st.session_state.pulse_depth = "Floating"
            
        elif current_pattern == 7:  # 한 (Cold)
            # Page 16: 허리가 아프고 몸을 잘 돌리지 못하며 덜 아프게 해주는 것은 따뜻함
            # Hard to turn body, warmth helps
            st.session_state.back_pain_cause = "No Specific Cause (발병 요인 없음)"
            if "Fixed/Cold (한통) - Cold" not in pain_nature_list:
                st.session_state.pain_nature.append("Fixed/Cold (한통) - Cold")
            if "Better w/ Warmth (득온즉감) - Cold" not in pain_nature_list:
                st.session_state.pain_nature.append("Better w/ Warmth (득온즉감) - Cold")
            # Page 16: 맥沈緊 (맥침긴) - Sinking-tight pulse
            st.session_state.pulse_depth = "Sinking"
            st.session_state.pulse_tension = "Tense (긴)"
            st.session_state.cold_heat_pref = "Cold Sens"
            st.session_state.cold_hands_feet = True
            
        elif current_pattern == 8:  # 습 (Dampness)
            # Page 16: 습한 곳에 오래 머무르면 허리가 돌덩이처럼 무거움
            # Damp environment, heavy like a stone, cold feeling
            st.session_state.back_pain_cause = "Damp Environment (습한 환경)"
            if "Heavy/Stone-like (중통) - Dampness" not in pain_nature_list:
                st.session_state.pain_nature.append("Heavy/Stone-like (중통) - Dampness")
            # Page 16: 찬 것이 차는 느낌 - Cold feeling
            st.session_state.cold_heat_pref = "Cold Sens"
            # Page 16: 맥緩 (맥완) - Slow pulse
            st.session_state.pulse_tension = "Soft (유)"
            # Dampness signs
            st.session_state.tongue_coat_thick = random.choice(["Thick", "Greasy"])
            
        elif current_pattern == 9:  # 습열 (Damp-Heat)
            # Page 16: 평소에 기름진 음식을 많이 먹는 사람, 오래 앉아 있으면 심화
            # Greasy food, sitting long worsens it
            st.session_state.back_pain_cause = "Greasy Food/Sedentary (기름진 음식/오래 앉음)"
            # Page 16: 맥緩 또는 沈 (맥완 또는 침) - Slow or sinking pulse
            st.session_state.pulse_depth = random.choice(["Middle", "Sinking"])
            st.session_state.pulse_tension = "Soft (유)"
            # Heat signs
            st.session_state.tongue_coat_color = "Yellow"
            st.session_state.tongue_coat_thick = "Greasy"
    
    # ===========================================
    # DYSPEPSIA CONSTRAINTS (소화불량 변증) - Page 16
    # Based on: 소화불량 환자 변증지표 중요도 항목-임상진료지침
    # ===========================================
    if "Dyspepsia" in st.session_state.disease:
        current_pattern = st.session_state.pattern_idx
        dyspepsia_specs = st.session_state.get("dyspepsia_spec", [])
        
        if current_pattern == 0:  # 비위허약/위허기허 (Spleen-Stomach Weakness)
            # Page 16: 脾식욕이 없고 식사량이 적다 (不思飲食, 食少)
            # No appetite, eats little
            st.session_state.appetite = random.choice(["None", "Low"])
            st.session_state.diet_amt = "Little (적음)"
            # Page 16: 食後腹脹痛 或腹 - Bloating after eating
            st.session_state.bloating = random.randint(2, 4)
            # Page 16: 피곤하고 몸에 힘이빠 四肢倦怠 - Tired, weak limbs
            st.session_state.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
            st.session_state.limb_weakness = True
            # Page 16: 舌苔淡白 薄潤 - Pale tongue with thin white coat
            st.session_state.tongue_color = "Pale"
            st.session_state.tongue_coat_color = "White"
            st.session_state.tongue_coat_thick = "Thin"
            # Page 16: 脈細弱 또는 遲緩 - Thin-weak or slow pulse
            st.session_state.pulse_width = "Thin"
            st.session_state.pulse_strength = "Weak"
            
        elif current_pattern == 1:  # 비위기허 (Spleen-Stomach Qi Deficiency)
            # Page 16: 배가 쓰리거나 아한숨을 잘 쉬고 (胃脘隱痛), 피로해진
            # Stomach pain, sighing, easily tired
            st.session_state.epigastric_pain = random.randint(2, 4)
            st.session_state.sighing_freq = random.randint(2, 4)
            st.session_state.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
            # Page 16: 정신이 없고 편치 않다 (精神倦怠, 呻吟, 易怒)
            st.session_state.mental_clarity = "Foggy (흐릿)"
            st.session_state.emot_anger = random.randint(3, 5)
            # Page 16: 舌淡苔白 - Pale white tongue
            st.session_state.tongue_color = "Pale"
            st.session_state.tongue_coat_color = "White"
            # Page 16: 脈細弱 맥세약 - Thin-weak pulse
            st.session_state.pulse_width = "Thin"
            st.session_state.pulse_strength = "Weak"
            
        elif current_pattern == 2:  # 간위불화 (Liver-Stomach Disharmony)
            # Page 16: 신물이 나고 트림한 (吞酸, 噯氣頻發)
            # Acid reflux, frequent belching
            st.session_state.acid_reflux = True
            st.session_state.belching = random.randint(3, 5)
            if "Acid Reflux (신물) - Liver/Food" not in dyspepsia_specs:
                st.session_state.dyspepsia_spec.append("Acid Reflux (신물) - Liver/Food")
            # Page 16: 易怒, 입이 마르고 쓰다 (口苦, 口乾)
            # Easily angered, dry/bitter mouth
            st.session_state.emot_anger = random.randint(3, 5)
            st.session_state.bitter_taste = True
            st.session_state.mouth_dry = random.randint(2, 4)
            if "Bitter Taste (구고) - Heat" not in dyspepsia_specs:
                st.session_state.dyspepsia_spec.append("Bitter Taste (구고) - Heat")
            # Page 16: 舌淡紅 苔薄白 - Red tongue with thin white coat
            st.session_state.tongue_color = "Pale Red"
            st.session_state.tongue_coat_color = "White"
            st.session_state.tongue_coat_thick = "Thin"
            # Page 16: 脈弦 - Wiry pulse
            st.session_state.pulse_tension = "Tense (긴)"
            
        elif current_pattern == 3:  # 비위습열 (Spleen-Stomach Damp-Heat)
            # Page 16: 신물이 나고 메스껍고 토하려 한다 (吞酸, 惡心欲吐, 嘔逆)
            # Acid reflux, nausea, vomiting
            st.session_state.acid_reflux = True
            st.session_state.nausea = random.randint(3, 5)
            st.session_state.nausea_sev = random.randint(3, 5)
            if "Nausea/Vomiting (구역/구토) - Damp-Heat" not in dyspepsia_specs:
                st.session_state.dyspepsia_spec.append("Nausea/Vomiting (구역/구토) - Damp-Heat")
            # Page 16: 몸이 뜨겁고, 입이 쓰거나 마르다 (身熱, 口苦, 口乾)
            st.session_state.cold_heat_body = "Hot (열)"
            st.session_state.bitter_taste = True
            st.session_state.mouth_dry = random.randint(2, 4)
            # Page 16: 舌紅 苔黃膩 - Red tongue with yellow greasy coat
            st.session_state.tongue_color = "Red"
            st.session_state.tongue_coat_color = "Yellow"
            st.session_state.tongue_coat_thick = "Greasy"
            # Page 16: 脈滑數 - Slippery-rapid pulse
            st.session_state.pulse_smooth = "Smooth (활)"
            
        elif current_pattern == 4:  # 한열착잡 (Cold-Heat Complex)
            # Page 16: 신물이 나고 메스껍 명치 부위가 갑갑
            # Acid reflux, nausea, epigastric fullness
            st.session_state.acid_reflux = True
            st.session_state.epigastric_pain = random.randint(2, 4)
            # Page 16: 찬물을 마시면 차서 발다리가 차가 - Cold drinks cause cold limbs
            st.session_state.cold_limbs_dyspepsia = True
            st.session_state.cold_hands_feet = True
            if "Cold Limbs (수족냉증) - Deficiency" not in dyspepsia_specs:
                st.session_state.dyspepsia_spec.append("Cold Limbs (수족냉증) - Deficiency")
            # Page 16: 舌淡 苔黃 - Pale tongue with yellow coat
            st.session_state.tongue_color = "Pale"
            st.session_state.tongue_coat_color = "Yellow"
            # Page 16: 脈弦 - Wiry pulse
            st.session_state.pulse_tension = "Tense (긴)"
            
        elif current_pattern == 5:  # 음식정체/식적 (Food Stagnation)
            # Page 16-17: 신물이 나고 트림과 명치가 아프고 누소화가 안 된
            # Acid reflux with foul smell, no appetite, undigested food
            st.session_state.acid_reflux = True
            st.session_state.foul_belch = True
            st.session_state.belching = random.randint(3, 5)
            st.session_state.belching_smell = "Foul (부패취)"
            if "Foul Belching (부패취) - Food Stag" not in dyspepsia_specs:
                st.session_state.dyspepsia_spec.append("Foul Belching (부패취) - Food Stag")
            # Page 17: 음식을 토한다 (嘔吐 未 消化 食 물) - Vomiting undigested food
            st.session_state.nausea = random.randint(2, 4)
            st.session_state.appetite = "None"
            # Page 17: 苔厚膩 - Thick greasy coat
            st.session_state.tongue_coat_thick = "Greasy"
            # Page 17: 脈滑 - Slippery pulse
            st.session_state.pulse_smooth = "Smooth (활)"
    
    # ===========================================
    # AGE-SPECIFIC CONSTRAINTS (연령별 제약)
    # ===========================================
    # Elderly (>65): more likely to have certain conditions
    if st.session_state.age > 65:
        # Higher chance of night urination
        if st.session_state.urine_freq_night == 0:
            st.session_state.urine_freq_night = random.randint(1, 2)
        # Memory issues more common
        if st.session_state.memory == "Good (좋음)" and random.random() < 0.3:
            st.session_state.memory = "Forgetful (건망)"
    
    # Young (<30): less likely to have chronic conditions
    if st.session_state.age < 30:
        # Reset conditions that are rare in young people
        if "HTN" in st.session_state.history_conditions and random.random() < 0.7:
            st.session_state.history_conditions.remove("HTN")
        if "DM" in st.session_state.history_conditions and random.random() < 0.7:
            st.session_state.history_conditions.remove("DM")
        if "Lipid" in st.session_state.history_conditions and random.random() < 0.7:
            st.session_state.history_conditions.remove("Lipid")
        if "Insomnia" in st.session_state.history_conditions and random.random() < 0.7:
            st.session_state.history_conditions.remove("Insomnia")

# --- ROBUST RANDOMIZER (UPDATED WITH WEIGHTED LOGIC) ---
def randomize_inputs():
    # ===========================================
    # 1. DEMOGRAPHICS (인구학적정보)
    # ===========================================
    st.session_state.age = random.randint(20, 80)
    st.session_state.sex = random.choice(["Male (남)", "Female (여)"])
    st.session_state.job = random.choice(["Student (학생)", "Office (사무직)", "Labor (현장직)", "Housewife (가사)"])
    st.session_state.height = random.randint(150, 190)
    st.session_state.weight = random.randint(45, 100)
    
    # ===========================================
    # 2. VITALS (SAFETY RULES - Keep within safe clinical ranges)
    # ===========================================
    st.session_state.sbp = random.randint(95, 170)
    st.session_state.dbp = random.randint(60, 100)
    # Ensure DBP < SBP
    if st.session_state.dbp >= st.session_state.sbp:
        st.session_state.dbp = st.session_state.sbp - random.randint(20, 40)
    st.session_state.pulse_rate = random.randint(55, 120)
    st.session_state.temp = round(random.uniform(36.0, 40.0), 1)
    st.session_state.resp = random.randint(12, 24)
    
    # ===========================================
    # 3. HISTORY & ONSET (병력 및 경과)
    # ===========================================
    st.session_state.onset = random.choice(["1 day ago (1일 전)", "2-3 days ago (2-3일 전)", "1 week ago (1주 전)", "Chronic >3mo (만성 3개월 이상)"])
    st.session_state.course = random.choice(["Worsening (악화중)", "Improving (호전중)", "Fluctuating (비슷/오르내림)"])
    st.session_state.history_conditions = random.sample(["HTN (고혈압)", "DM (당뇨)", "Lipid (이상지질혈증)", "Insomnia (불면증)"], k=random.randint(0, 2))
    st.session_state.meds_specific = random.sample(["HTN Meds (혈압약)", "DM Meds (당뇨약)", "Sleep Meds (수면제)", "Mood Meds (항우울제/항불안제)"], k=random.randint(0, 2))
    st.session_state.family_hx = random.sample(["HTN (고혈압)", "DM (당뇨)", "Cancer (암)", "Heart Disease (심장병)"], k=random.randint(0, 2))
    
    # Social History (사회력)
    st.session_state.social_alcohol_freq = random.choice(["None (비음주)", "Week (주간)", "Daily (매일)"])
    st.session_state.social_alcohol_amt = round(random.uniform(0, 5), 1) if st.session_state.social_alcohol_freq != "None (비음주)" else 0.0
    st.session_state.social_smoke_daily = round(random.uniform(0, 20), 1)
    st.session_state.social_exercise_int = random.choice(["Low (저)", "Medium (중)", "High (고)"])
    st.session_state.social_exercise_time = random.randint(0, 120)
    
    # ===========================================
    # 4. WOMEN'S HEALTH (여성력 - Only relevant if Female)
    # ===========================================
    if st.session_state.sex == "Female (여)":
        st.session_state.mens_cycle = random.randint(21, 35)
        st.session_state.mens_regular = random.choice(["Regular (규칙)", "Irregular (불규칙)", "Menopause (폐경)"])
        st.session_state.mens_amt = random.choice(["Light (적음)", "Normal (보통)", "Heavy (많음)"])
        st.session_state.mens_clot = random.choice([True, False])
        st.session_state.mens_color = random.choice(["Pale (연함)", "Red (적색)", "Dark (흑자색)"])
        st.session_state.mens_duration = random.randint(3, 7)
        st.session_state.mens_pain_score = random.randint(0, 10)
    
    # ===========================================
    # 5. EXCRETION & DIET (배설 및 식사)
    # ===========================================
    st.session_state.diet_speed = random.choice(["Fast <10min (빠름)", "Normal 20min (보통)", "Slow >30min (느림)"])
    st.session_state.appetite = random.choice(["None (없음)", "Low (저하)", "Normal (보통)", "High (항진)"])
    st.session_state.diet_freq = random.choice([1, 2, 3, 4])
    st.session_state.diet_regular = random.choice(["Regular (규칙적)", "Irregular (불규칙)"])
    st.session_state.water_intake = random.choice(["<0.5L (0.5L 미만)", "0.5-1L", "1-2L", ">2L (2L 이상)"])
    
    # Stool (대변)
    st.session_state.stool_freq = random.choice(["1/day (1회/일)", "2-3/day (2-3회/일)", "Constipation (변비)"])
    st.session_state.stool_form = random.choice(["Normal (보통)", "Loose (묽음/연변)", "Hard (굳음/경변)"])
    st.session_state.stool_discomfort = random.choice([True, False])
    st.session_state.stool_color = random.choice(["Yellow (황색)", "Brown (황갈색)", "Black (흑색)", "Green (녹색)"])
    
    # Urine (소변)
    st.session_state.urine_freq_day = random.randint(3, 12)
    st.session_state.urine_freq_night = random.randint(0, 4)
    st.session_state.urine_stream = random.choice(["Normal (정상)", "Weak (약함)", "Intermittent (끊김)"])
    st.session_state.urine_residual = random.choice([True, False])
    st.session_state.urine_incontinence = random.choice([True, False])
    st.session_state.urine_color = random.choice(["Clear (맑음)", "Yellow (황색)", "Reddish (적색/혈뇨)"])
    
    # ===========================================
    # 6. SLEEP, SWEAT, COLD/HEAT (수면, 땀, 한열)
    # ===========================================
    st.session_state.sleep_hours = random.randint(4, 10)
    st.session_state.sleep_waking_state = random.choice(["Refreshed (개운함)", "Tired (피곤함)", "Heavy (무거움)"])
    st.session_state.sleep_depth = random.choice(["Deep (깊음)", "Shallow/Light (얕음)"])
    st.session_state.insomnia_onset = random.choice([True, False])
    st.session_state.insomnia_maintain = random.choice([True, False])
    st.session_state.insomnia_reentry = random.choice([True, False])
    st.session_state.dreams = random.choice(["Rare (거의 없음)", "Sometimes (가끔)", "Frequent (자주)", "Nightmares (악몽)"])
    
    st.session_state.sweat_amt = random.choice(["None (무한 無汗)", "Normal (보통)", "Excessive (다한 多汗)"])
    st.session_state.sweat_area = random.choice(["General (전신)", "Head (두부)", "Night (야간/도한)"])
    st.session_state.sweat_feeling = random.choice(["Refreshed (상쾌)", "Tired/Cold (피곤/냉함)", "Hot (열감)"])
    
    st.session_state.cold_heat_pref = random.choice(["Cold Sens (오한/추위탐)", "Balanced (보통)", "Heat Sens (열감/더위탐)"])
    st.session_state.drink_temp = random.choice(["Icy (냉수)", "Warm (온수)", "Hot (열수)"])
    
    # ===========================================
    # 7. MENTAL, SENSORY & INSPECTION (정신, 감각 및 신체검진)
    # ===========================================
    # Personality sliders (성격 1-5)
    st.session_state.personality_speed = random.randint(1, 5)
    st.session_state.personality_io = random.randint(1, 5)
    st.session_state.personality_soft = random.randint(1, 5)
    st.session_state.personality_static = random.randint(1, 5)
    
    # Emotions (감정 1-5)
    st.session_state.emot_anger = random.randint(1, 5)
    st.session_state.emot_depress = random.randint(1, 5)
    st.session_state.emot_anxiety = random.randint(1, 5)
    st.session_state.excitement = random.randint(1, 5)
    st.session_state.emot_fear = random.randint(1, 5)
    st.session_state.emot_thought = random.randint(1, 5)
    st.session_state.emot_grief = random.randint(1, 5)
    
    st.session_state.fatigue_level = random.choice(["None (없음)", "Low (약함)", "Moderate (중등도)", "Severe (심함)"])
    st.session_state.voice_vol = random.choice(["Soft (작음)", "Normal (보통)", "Loud (큼)"])
    st.session_state.voice_vol_slider = random.randint(1, 3)
    
    # Mental State (정신상태)
    st.session_state.memory = random.choice(["Good (좋음)", "Forgetful (건망)", "Bad (나쁨)"])
    st.session_state.motivation = random.choice(["High (높음)", "Normal (보통)", "Low (낮음)", "Apathetic (무기력)"])
    st.session_state.stress_coping = random.choice(["Good (좋음)", "Average (보통)", "Poor (나쁨)"])
    
    # Physical Inspection (신체검진)
    st.session_state.edema = random.choice(["None (없음)", "Face (안면)", "Legs (하지)", "General (전신)"])
    st.session_state.bruising = random.choice(["Normal (정상)", "Easy (잘듦)", "Spontaneous (절로 생김)"])
    st.session_state.limb_weakness = random.choice([True, False])
    st.session_state.vision_blackout = random.choice([True, False])
    
    st.session_state.body_solidity = random.choice(["Soft (물렁)", "Normal (보통)", "Solid (단단)"])
    st.session_state.face_color = random.choice(["Normal (정상)", "Pale (창백)", "Red (홍조)", "Yellow (황달)", "Dark (암색)"])
    st.session_state.face_gloss = random.choice(["Dull (칙칙)", "Normal (보통)", "Shiny (윤기)"])
    st.session_state.eye_red = random.choice([True, False])
    st.session_state.lip_dry = random.choice([True, False])
    
    st.session_state.skin_dry = random.choice(["Normal (정상)", "Dry (건조)", "Scaly (각질)"])
    st.session_state.skin_itch = random.choice([True, False])
    
    # Sensory symptoms (0-5 severity) - Page 17-18
    st.session_state.tinnitus_freq = random.randint(0, 5)
    st.session_state.tinnitus_sev = random.randint(0, 5)
    st.session_state.hearing_sev = random.randint(0, 5)
    st.session_state.dizziness_sev = random.randint(0, 5)
    st.session_state.vision_blackout = random.choice([True, False])
    
    # ===========================================
    # NEW: Mouth/Throat (구강/목) - Page 17-18
    # ===========================================
    st.session_state.lip_color = random.choice(["Normal (정상)", "Pale (창백)", "Red (붉음)", "Dark (어두움)"])
    st.session_state.mouth_dry = random.randint(0, 5)
    st.session_state.throat_dry = random.choice([True, False])
    st.session_state.mouth_bitter = random.choice([True, False])
    st.session_state.bad_breath = random.choice([True, False])
    st.session_state.hiccup = random.choice([True, False])
    
    # ===========================================
    # NEW: Neck/Nape (뒷목/경항부) - Page 18
    # ===========================================
    st.session_state.neck_nape_freq = random.randint(0, 5)
    st.session_state.neck_nape_sev = random.randint(0, 5)
    
    # ===========================================
    # NEW: Chest (흉부) - Page 18
    # ===========================================
    st.session_state.breath_sound = random.choice(["Normal (정상)", "Loud (큼)", "Weak (약함)"])
    st.session_state.palpitation = random.randint(0, 5)
    st.session_state.chest_tight_freq = random.randint(0, 5)
    st.session_state.chest_tight_sev = random.randint(0, 5)
    st.session_state.chest_pain_freq = random.randint(0, 5)
    st.session_state.chest_pain_sev = random.randint(0, 5)
    st.session_state.sighing_freq = random.randint(0, 5)
    st.session_state.nausea = random.randint(0, 5)
    st.session_state.bloating = random.randint(0, 5)
    st.session_state.flatulence = random.choice(["None (없음)", "Normal (보통)", "Frequent (잦음)"])
    
    # ===========================================
    # NEW: Functional Dyspepsia details (기능성 소화불량) - Page 18
    # ===========================================
    st.session_state.lower_abd_discomfort = random.randint(0, 5)
    st.session_state.abd_pain_sev = random.randint(0, 5)
    st.session_state.abd_pain_type = random.choice(["None (없음)", "Dull (둔통)", "Sharp (예리통)", "Cramping (산통/경련통)"])
    st.session_state.abd_tenderness = random.choice([True, False])
    st.session_state.nausea_sev = random.randint(0, 5)
    st.session_state.belching = random.randint(0, 5)
    st.session_state.belching_smell = random.choice(["None (없음)", "Sour (신맛/산취)", "Foul (부패취)"])
    st.session_state.food_stag_sev = random.randint(0, 5)
    st.session_state.abd_muscle_tension = random.choice([True, False])
    st.session_state.abd_mass = random.choice([True, False])
    st.session_state.abd_pulsation = random.choice([True, False])
    st.session_state.bowel_sound = random.choice(["Normal (정상)", "Hyperactive (항진)", "Hypoactive (저하)"])
    
    # ===========================================
    # NEW: Cold/Heat Tendency (한열경향) - Page 19
    # ===========================================
    st.session_state.cold_heat_body = random.choice(["Cold (한 寒)", "Balanced (보통)", "Hot (열 熱)"])
    st.session_state.cold_heat_distribution = random.choice(["Even (균등)", "Upper Hot (상열 上熱)", "Lower Cold (하한 下寒)", "Upper Hot Lower Cold (상열하한 上熱下寒)"])
    st.session_state.cold_sensitivity = random.randint(1, 5)
    st.session_state.heat_sensitivity = random.randint(1, 5)
    
    # ===========================================
    # NEW: General Condition (전신상태) - Page 19
    # ===========================================
    st.session_state.physical_strength = random.choice(["Weak (허약)", "Normal (보통)", "Strong (강건)"])
    st.session_state.condition_bad_area = random.sample(["Head (두부)", "Stomach (위장)", "Back (요배부)", "Limbs (사지)"], k=random.randint(0, 2))
    
    # ===========================================
    # NEW: Sweat details (땀) - Page 19
    # ===========================================
    st.session_state.sweat_time = random.choice(["Daytime (주간)", "Night (야간/도한)", "Exercise (운동시)"])
    
    # ===========================================
    # NEW: Mental State details (정신상태) - Page 19
    # ===========================================
    st.session_state.mental_clarity = random.choice(["Clear (맑음/청명)", "Foggy (흐릿/혼미)", "Confused (혼란)"])
    st.session_state.mood_swing = random.choice(["Stable (안정)", "Mild (약간)", "Severe (심함)"])
    st.session_state.emot_startle = random.randint(1, 5)
    
    # ===========================================
    # NEW: Body part discomfort - Page 18
    # ===========================================
    st.session_state.flank_freq = random.randint(0, 5)
    st.session_state.flank_sev = random.randint(0, 5)
    st.session_state.back_freq = random.randint(0, 5)
    st.session_state.back_sev = random.randint(0, 5)
    st.session_state.pelvis_freq = random.randint(0, 5)
    st.session_state.pelvis_sev = random.randint(0, 5)
    st.session_state.shoulder_freq = random.randint(0, 5)
    st.session_state.shoulder_sev = random.randint(0, 5)
    st.session_state.elbow_freq = random.randint(0, 5)
    st.session_state.elbow_sev = random.randint(0, 5)
    st.session_state.hand_foot_freq = random.randint(0, 5)
    st.session_state.hand_foot_sev = random.randint(0, 5)
    st.session_state.leg_discomfort = random.randint(0, 5)
    st.session_state.knee_freq = random.randint(0, 5)
    st.session_state.knee_sev = random.randint(0, 5)
    
    # ===========================================
    # 8. PULSE & TONGUE (맥진 및 설진)
    # ===========================================
    st.session_state.pulse_depth = random.choice(["Floating (부맥)", "Middle (중맥)", "Sinking (침맥)"])
    st.session_state.pulse_width = random.choice(["Thin (세맥)", "Medium (대맥)", "Wide (홍맥)"])
    st.session_state.pulse_length = random.choice(["Short (단맥)", "Medium (장맥)", "Long (장맥)"])
    st.session_state.pulse_strength = random.choice(["Weak (무력)", "Moderate (유력)", "Strong (강력)"])
    st.session_state.pulse_smooth = random.choice(["Smooth (활맥)", "Normal (완맥)", "Rough (삽맥)"])
    st.session_state.pulse_tension = random.choice(["Soft (유맥)", "Normal (완맥)", "Tense (긴맥)"])
    
    st.session_state.tongue_color = random.choice(["Pale (담백)", "Pale Red (담홍)", "Red (홍설)", "Dark Red (강홍/자설)"])
    st.session_state.tongue_size = random.choice(["Small (소)", "Normal (정상)", "Enlarged (대/태)"])
    st.session_state.tongue_coat_color = random.choice(["White (백태)", "Yellow (황태)", "Grey (회태)"])
    st.session_state.tongue_coat_thick = random.choice(["Thin (박태)", "Thick (후태)", "Greasy (니태)"])
    st.session_state.tongue_coat_particle = random.choice(["Dry (조태)", "Fine (윤태)", "Wet (활태)"])
    st.session_state.tongue_marks = random.choice([True, False])
    
    # ===========================================
    # 9. PAIN GRID
    # ===========================================
    for part in ["pain_neck", "pain_shoulder", "pain_back", "pain_knee", "pain_hand", "pain_elbow", "pain_flank", "pain_pelvis", "pain_hip"]:
        freq = random.randint(0, 5)
        intensity = random.randint(0, 10) if freq > 0 else 0
        st.session_state[part] = [freq, intensity]
        st.session_state[f"{part}_f"] = freq
        st.session_state[f"{part}_i"] = intensity
    
    st.session_state.cold_hands_feet = random.choice([True, False])
    
    # ===========================================
    # 10. DISEASE & PATTERN SELECTION (질환 및 변증 선택 - Page 23)
    # Updated to match official 한열허실 pattern classification
    # ===========================================
    disease_opts = ["Common Cold (감기/급성상기도감염)", "Allergic Rhinitis (알레르기비염)", "Back Pain (요통)", "Functional Dyspepsia (기능성소화불량)"]
    st.session_state.disease = random.choice(disease_opts)
    
    # Determine pattern key based on disease selection (Page 23 compliant)
    pattern_key = "Cold_WC"  # Default fallback
    
    if "Cold" in st.session_state.disease:
        # Page 23: Only 풍한형 (WC) and 풍열형 (WH) - removed 풍조
        num_patterns = len(DISEASE_PATTERNS["감기"]["patterns"])
        st.session_state.pattern_idx = random.randint(0, num_patterns - 1)
        pattern_key = DISEASE_PATTERNS["감기"]["patterns"][st.session_state.pattern_idx]["id"]
    elif "Rhinitis" in st.session_state.disease:
        # Page 23: Only 수체형 (Fluid) - single unified pattern
        num_patterns = len(DISEASE_PATTERNS["알레르기비염"]["patterns"])
        st.session_state.pattern_idx = random.randint(0, num_patterns - 1)
        pattern_key = DISEASE_PATTERNS["알레르기비염"]["patterns"][st.session_state.pattern_idx]["id"]
    elif "Back Pain" in st.session_state.disease:
        # Page 23: 한열허실 based 9 patterns
        num_patterns = len(DISEASE_PATTERNS["요통"]["patterns"])
        st.session_state.pattern_idx = random.randint(0, num_patterns - 1)
        pattern_key = DISEASE_PATTERNS["요통"]["patterns"][st.session_state.pattern_idx]["id"]
    elif "Dyspepsia" in st.session_state.disease:
        # Page 23: 한열허실 based 9 patterns
        num_patterns = len(DISEASE_PATTERNS["소화불량"]["patterns"])
        st.session_state.pattern_idx = random.randint(0, num_patterns - 1)
        pattern_key = DISEASE_PATTERNS["소화불량"]["patterns"][st.session_state.pattern_idx]["id"]
    
    # ===========================================
    # 11. DISEASE-SPECIFIC SYMPTOMS (질환별 증상 - WEIGHTED)
    # ===========================================
    # Randomize TKM Examination findings (한의사 진찰소견 - Page 17)
    st.session_state.exam_lung_sound = random.choice([None, "Normal (정상)", "Wheeze (천명)", "Crackle (수포음)"])
    st.session_state.exam_throat = random.choice([None, "Normal (정상)", "Red (발적)", "Swollen (부종)"])
    st.session_state.exam_tonsil = random.choice([None, "Normal (정상)", "Enlarged (비대)", "Exudate (삼출물)"])
    
    if "Cold" in st.session_state.disease:
        # Use weighted selection for cold symptoms based on pattern
        st.session_state.fever_sev = get_weighted_level("fever_sev", pattern_key)
        st.session_state.chills_sev = get_weighted_level("chills_sev", pattern_key)
        st.session_state.snot_sev = get_weighted_level("snot_sev", pattern_key)
        st.session_state.cough_sev = get_weighted_level("cough_sev", pattern_key)
        
        # Cold specific symptoms (감기 특이증상)
        cold_opts = ["No Sweat (무한 無汗)", "Yellow Phlegm (황담 黃痰)", "White Phlegm (희박담 稀薄白痰)", "Dry Throat (인후건조 咽乾)", "Joint Pain (관절통 骨節疼痛)"]
        st.session_state.cold_symptoms_spec = random.sample(cold_opts, k=random.randint(0, 3))
    
    elif "Rhinitis" in st.session_state.disease:
        # Use weighted selection for rhinitis symptoms
        st.session_state.sneeze_sev = get_weighted_level("rhinitis_sneeze", pattern_key)
        st.session_state.nose_block_sev = get_weighted_level("rhinitis_block", pattern_key)
        st.session_state.nose_itch_sev = get_weighted_level("rhinitis_itch", pattern_key)
        st.session_state.snot_sev = get_weighted_level("rhinitis_snot_sev", pattern_key)
        
        # Weighted snot type selection (콧물 성상)
        snot_type_level = get_weighted_level("rhinitis_snot_type", pattern_key, levels=[1, 2, 3])
        snot_type_map = {1: "Clear/Watery (청수양 淸水樣)", 2: "White/Sticky (백점액 白粘)", 3: "Yellow/Thick (황농성 黃膿)"}
        st.session_state.snot_type = snot_type_map.get(snot_type_level, "Clear/Watery (청수양 淸水樣)")
    
    elif "Back Pain" in st.session_state.disease:
        st.session_state.pain_sev = random.randint(3, 10)
        st.session_state.pain_back = [random.randint(3, 5), random.randint(5, 10)]
        st.session_state.pain_back_f = st.session_state.pain_back[0]
        st.session_state.pain_back_i = st.session_state.pain_back[1]
        
        # Randomize pain nature based on pattern (통증 양상)
        pain_opts = [
            "Moving (유주통 遊走痛) - Phlegm/Wind", 
            "Stabbing (자통 刺痛) - Blood Stasis", 
            "Fixed/Cold (한통 寒痛) - Cold", 
            "Better w/ Warmth (득온즉감 得溫則減) - Cold", 
            "Worse at Night (야간통 夜甚) - Blood Stasis", 
            "Heavy/Stone-like (중통 重痛) - Dampness",
            "Worse Standing (구립즉심 久立則甚) - Qi"
        ]
        st.session_state.pain_nature = random.sample(pain_opts, k=random.randint(1, 3))
    
    elif "Dyspepsia" in st.session_state.disease:
        st.session_state.pain_sev = random.randint(1, 5)
        dys_opts = [
            "Acid Reflux (신물/탄산 吞酸) - Liver/Food", 
            "Nausea/Vomiting (구역/구토 惡心嘔吐) - Damp-Heat", 
            "Bitter Taste (구고 口苦) - Heat", 
            "Foul Belching (부패취 噯氣腐臭) - Food Stag", 
            "Cold Limbs (수족냉증 四肢厥冷) - Deficiency"
        ]
        st.session_state.dyspepsia_spec = random.sample(dys_opts, k=random.randint(1, 3))
    
    # ===========================================
    # 12. APPLY CONSTRAINT RULES (제약규칙 적용 - Clinical Logic)
    # ===========================================
    apply_constraint_rules()

# --- UI LAYOUT ---
st.title("🏥 TKM Clinical Scenario Generator (한의 임상시나리오 생성기)")
st.caption("한의 임상정보 항목 기반 가상환자 생성 시스템 - Pages 15-19, 21-23 Compliant")

with st.sidebar:
    st.header("⚙️ Controls (조작)")
    if st.button("🎲 Randomize (랜덤 생성)", type="primary"):
        randomize_inputs()
        st.rerun()
    st.markdown("---")
    st.header("Diagnosis (진단명)")
    disease_opts = ["Common Cold (감기/급성상기도감염)", "Allergic Rhinitis (알레르기비염)", "Back Pain (요통)", "Functional Dyspepsia (기능성소화불량)"]
    
    # Get current disease index for the selectbox
    current_disease_idx = 0
    for i, opt in enumerate(disease_opts):
        if opt == st.session_state.disease:
            current_disease_idx = i
            break
    
    st.session_state.disease = st.selectbox("Disease (질환명)", disease_opts, index=current_disease_idx)

    # ===========================================
    # Pattern Selection based on Page 23 classification
    # 변증유형 선택 (Page 23 변증분류 기준)
    # ===========================================
    patterns = []
    pattern_display = []
    disease_key = None
    
    if "Cold" in st.session_state.disease:
        disease_key = "감기"
        # Page 23: 풍한형, 풍열형 only (removed 풍조 per official doc)
        patterns = DISEASE_PATTERNS["감기"]["patterns"]
        pattern_display = [f"{p['name']} → {', '.join(p['prescriptions'])}" for p in patterns]
    elif "Rhinitis" in st.session_state.disease:
        disease_key = "알레르기비염"
        # Page 23: 수체형 only (unified pattern)
        patterns = DISEASE_PATTERNS["알레르기비염"]["patterns"]
        pattern_display = [f"{p['name']} → {', '.join(p['prescriptions'])}" for p in patterns]
    elif "Back Pain" in st.session_state.disease:
        disease_key = "요통"
        # Page 23: 한열허실 based 9 patterns
        patterns = DISEASE_PATTERNS["요통"]["patterns"]
        pattern_display = [f"{p['name']} → {', '.join(p['prescriptions'])}" for p in patterns]
    elif "Dyspepsia" in st.session_state.disease:
        disease_key = "소화불량"
        # Page 23: 한열허실 based 9 patterns
        patterns = DISEASE_PATTERNS["소화불량"]["patterns"]
        pattern_display = [f"{p['name']} → {', '.join(p['prescriptions'])}" for p in patterns]
    else:
        pattern_display = ["General"]
    
    if st.session_state.pattern_idx >= len(pattern_display): 
        st.session_state.pattern_idx = 0
    
    selected_pattern = st.selectbox("Pattern/Prescription (변증/처방)", pattern_display, index=st.session_state.pattern_idx)
    
    # Display KCD code info (한국표준질병사인분류)
    if disease_key:
        kcd_info = get_kcd_info(disease_key)
        if kcd_info:
            st.caption(f"📋 KCD (한국표준질병사인분류): {kcd_info['main_code']}")
            with st.expander("KCD Details (KCD 상세정보 - Page 21-22)", expanded=False):
                st.markdown(f"**Main Code (주코드):** {kcd_info['main_code']}")
                st.markdown("**Included (포함):**")
                for code, desc in kcd_info['sub_codes'].items():
                    st.markdown(f"- {code}: {desc}")
                st.markdown("**Excluded (배제):**")
                for excl in kcd_info['exclusions']:
                    st.markdown(f"- ❌ {excl}")

# --- MAIN FORM (주요 입력양식) ---

with st.expander("1. Demographics & Vitals (인구학적정보 및 활력징후) - KTAS Safety Enforced", expanded=True):
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

with st.expander("2. Medical History & Lifestyle (병력 및 생활습관)", expanded=False):
    h1, h2 = st.columns(2)
    with h1:
        st.multiselect("Conditions (현병력)", ["HTN (고혈압)", "DM (당뇨)", "Lipid (이상지질혈증)", "Insomnia (불면증)"], key="history_conditions")
        st.multiselect("Meds (약물력)", ["HTN Meds (혈압약)", "DM Meds (당뇨약)", "Sleep Meds (수면제)", "Mood Meds (항우울제/항불안제)"], key="meds_specific")
    with h2:
        st.selectbox("Alcohol (음주)", ["None (비음주)", "Week (주간)", "Daily (매일)"], key="social_alcohol_freq")
        st.number_input("Smoke (흡연 개피/일)", 0.0, 50.0, key="social_smoke_daily")
        st.selectbox("Exercise Intensity (운동 강도)", ["Low (저)", "Medium (중)", "High (고)"], key="social_exercise_int")

    if st.session_state.sex == "Female (여)":
        st.markdown("**Women's Health (여성력)**")
        # Ensure valid values before rendering widgets
        if st.session_state.mens_duration < 1:
            st.session_state.mens_duration = 5
        if st.session_state.mens_cycle < 1:
            st.session_state.mens_cycle = 28
        w1, w2, w3, w4 = st.columns(4)
        with w1: st.selectbox("Cycle (생리규칙성)", ["Regular (규칙)", "Irregular (불규칙)", "Menopause (폐경)"], key="mens_regular")
        with w2: st.number_input("Duration (생리기간 일)", 1, 10, key="mens_duration")
        with w3: st.slider("Pain Score (생리통 0-10)", 0, 10, key="mens_pain_score")
        with w4: st.selectbox("Color (생리혈 색)", ["Pale (연함)", "Red (적색)", "Dark (흑자색)"], key="mens_color")

with st.expander("3. Excretion & Diet (배설 및 식사)", expanded=False):
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

with st.expander("4. Sleep, Sweat, Cold/Heat (수면, 땀, 한열경향)", expanded=False):
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

with st.expander("5. Mental State & Physical Inspection (정신상태 및 신체검진)", expanded=True):
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Mental State (정신상태)**")
        st.selectbox("Memory (기억력)", ["Good (좋음)", "Forgetful (건망)", "Bad (나쁨)"], key="memory")
        st.selectbox("Motivation (의욕)", ["High (높음)", "Normal (보통)", "Low (낮음)", "Apathetic (무기력)"], key="motivation")
        st.selectbox("Stress Coping (스트레스 대처력)", ["Good (좋음)", "Average (보통)", "Poor (나쁨)"], key="stress_coping")
        st.slider("Voice Vol (성음크기)", 1, 3, key="voice_vol_slider", help="1=작음, 2=보통, 3=큼")
        st.slider("Speed (성격완급 느긋-급함)", 1, 5, key="personality_speed", help="1=느긋, 5=급함")
        st.slider("Anger (노 화냄정도)", 1, 5, key="emot_anger", help="1=평온, 5=화 잘냄")
        st.slider("Grief (비 슬픔정도)", 1, 5, key="emot_grief", help="1=평온, 5=슬픔 많음")
    with m2:
        st.markdown("**Physical Inspection (신체검진)**")
        st.selectbox("Edema (부종여부)", ["None (없음)", "Face (안면)", "Legs (하지)", "General (전신)"], key="edema")
        st.selectbox("Bruising (출혈/멍듦)", ["Normal (정상)", "Easy (잘듦)", "Spontaneous (절로 생김)"], key="bruising")
        c_a, c_b = st.columns(2)
        with c_a: st.checkbox("Limb Weakness (사지무력감)", key="limb_weakness")
        with c_b: st.checkbox("Vision Blackout (눈앞캄캄함)", key="vision_blackout")
        st.markdown("---")
        st.selectbox("Skin Dryness (피부 건조도)", ["Normal (정상)", "Dry (건조)", "Scaly (각질)"], key="skin_dry")
        st.checkbox("Skin Itch (피부 가려움)", key="skin_itch")
        
        # UPDATED: Changed to severity sliders (0-5) per Pages 18, 103
        st.slider("Tinnitus Severity (이명 강도)", 0, 5, key="tinnitus_sev", 
                  help="0=없음, 1-2=경미, 3-4=중등도, 5=심함")
        st.slider("Hearing Issue Severity (난청/이롱 강도)", 0, 5, key="hearing_sev",
                  help="0=없음, 1-2=경미, 3-4=중등도, 5=심함")
        st.slider("Dizziness Severity (어지러움/두훈 강도)", 0, 5, key="dizziness_sev",
                  help="0=없음, 1-2=경미, 3-4=중등도, 5=심함")
        
        st.selectbox("Face Color (면색/얼굴 색)", ["Normal (정상)", "Pale (창백)", "Red (홍조)", "Yellow (황달)", "Dark (암색)"], key="face_color")

with st.expander("6. Pulse & Tongue Diagnosis (맥진 및 설진)", expanded=True):
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

with st.expander("7. ROS Pain Grid (통증 부위별 Review of Systems)", expanded=False):
    st.caption("Freq (빈도 0-5) / Int (강도 0-10)")
    cols = st.columns(3)
    parts = [("Neck (경항부)", "pain_neck"), ("Back (요배부)", "pain_back"), ("Knee (슬부)", "pain_knee"), ("Shldr (견부)", "pain_shoulder"), ("Elbow (주관절)", "pain_elbow"), ("Hand (수부)", "pain_hand")]
    for l, k in parts:
        with cols[0]: st.text(l)
        with cols[1]: st.number_input(f"{l} F (빈도)", 0, 5, key=f"{k}_f", label_visibility="collapsed")
        with cols[2]: st.number_input(f"{l} I (강도)", 0, 10, key=f"{k}_i", label_visibility="collapsed")
        st.session_state[k] = [st.session_state[f"{k}_f"], st.session_state[f"{k}_i"]]
    st.checkbox("Cold Hands/Feet (수족냉증)", key="cold_hands_feet")

# --- SECTION 8: DISEASE SPECIFIC SCALES (주소증별 증상 척도) ---
st.markdown("---")
st.subheader("8. Chief Complaint Specifics (주소증 상세 - 변증지표)")

if "Cold" in st.session_state.disease:
    st.caption("감기환자 변증지표 (Page 15 - 임상진료지침 기준)")
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Fever Level (발열 강도: 1-5)", 1, 5, key="fever_sev", help="1=미열/무열, 5=고열 壯熱")
        st.slider("Chills Level (오한 강도: 1-5)", 1, 5, key="chills_sev", help="1=경미, 5=惡寒重")
    with c2:
        st.slider("Runny Nose (콧물 양: 1-5)", 1, 5, key="snot_sev", help="1=경미, 5=콧물 줄줄")
        st.slider("Cough (기침 강도: 1-5)", 1, 5, key="cough_sev", help="1=경미, 5=기침 심함")
    cold_opts = ["No Sweat (무한 無汗)", "Yellow Phlegm (황담 黃痰)", "White Phlegm (희박담 稀薄白痰)", "Dry Throat (인후건조 咽乾)", "Joint Pain (관절통 骨節疼痛)"]
    st.multiselect("Cold Symptoms (감기 증상 - Page 15)", cold_opts, key="cold_symptoms_spec")

elif "Rhinitis" in st.session_state.disease:
    st.caption("알레르기비염 변증지표 (Page 23 - 수체형)")
    r1, r2 = st.columns(2)
    with r1:
        st.slider("Sneezing (재채기 嚏噴)", 1, 5, key="sneeze_sev", help="1=경미, 5=연발성")
        st.slider("Nasal Blockage (코막힘 鼻塞)", 1, 5, key="nose_block_sev", help="1=경미, 5=완전폐쇄")
    with r2:
        st.slider("Nasal Itch (코가려움 鼻癢)", 1, 5, key="nose_itch_sev", help="1=경미, 5=심한 가려움")
        st.slider("Runny Nose (콧물 양 鼻涕)", 1, 5, key="snot_sev", help="1=경미, 5=콧물 줄줄")
    st.selectbox("Snot Type (콧물 성상)", 
                 ["Clear/Watery (청수양 淸水樣)", "White/Sticky (백점액 白粘)", "Yellow/Thick (황농성 黃膿)"], 
                 key="snot_type")
    st.info(f"Target Prescription (처방): {selected_pattern}")

elif "Dyspepsia" in st.session_state.disease:
    st.caption("기능성소화불량 변증지표 (Pages 16-17 - 한열허실 팔강변증)")
    st.slider("Bloating/Pain (복만/복통 강도)", 1, 5, key="pain_sev", help="1=경미, 5=심함")
    dys_opts = [
        "Acid Reflux (신물/탄산 吞酸) - Liver/Food", 
        "Nausea/Vomiting (구역/구토 惡心嘔吐) - Damp-Heat", 
        "Bitter Taste (구고 口苦) - Heat", 
        "Foul Belching (부패취 噯氣腐臭) - Food Stag", 
        "Cold Limbs (수족냉증 四肢厥冷) - Deficiency"
    ]
    st.multiselect("Dyspepsia Specifics (소화불량 증상 - Page 16/17)", dys_opts, key="dyspepsia_spec")

elif "Back Pain" in st.session_state.disease:
    st.caption("요통 변증지표 (Pages 15-16 - 한열허실 팔강변증)")
    st.slider("Pain Intensity (통증 강도 NRS)", 1, 10, key="pain_sev", help="1=경미, 10=극심 (KTAS: 7 이하 권장)")
    pain_opts = [
        "Moving (유주통 遊走痛) - Phlegm/Wind", 
        "Stabbing (자통 刺痛) - Blood Stasis", 
        "Fixed/Cold (한통 寒痛) - Cold", 
        "Better w/ Warmth (득온즉감 得溫則減) - Cold", 
        "Worse at Night (야간통 夜甚) - Blood Stasis", 
        "Heavy/Stone-like (중통 重痛) - Dampness",
        "Worse Standing (구립즉심 久立則甚) - Qi"
    ]
    st.multiselect("Pain Nature (통증 양상 - Page 15/16)", pain_opts, key="pain_nature")

# --- GENERATION (가상환자 생성) ---
def generate_patient():
    try:
        model = genai.GenerativeModel('gemini-flash-latest') 
    except:
        st.error("API 키 오류. Streamlit Secrets에서 확인하세요.")
        return

    # --- STEP 4: GET RICH KOREAN DESCRIPTIONS FOR LLM ---
    # Fetch Korean text instead of sending raw numbers
    fever_desc = get_desc("fever_sev", st.session_state.fever_sev) or f"레벨 {st.session_state.fever_sev}"
    chills_desc = get_desc("chills_sev", st.session_state.chills_sev) or f"레벨 {st.session_state.chills_sev}"
    snot_desc = get_desc("snot_sev", st.session_state.snot_sev) or f"레벨 {st.session_state.snot_sev}"
    cough_desc = get_desc("cough_sev", st.session_state.cough_sev) or f"레벨 {st.session_state.cough_sev}"
    
    # Rhinitis descriptions
    sneeze_desc = get_desc("rhinitis_sneeze", st.session_state.sneeze_sev) or f"레벨 {st.session_state.sneeze_sev}"
    nose_block_desc = get_desc("rhinitis_block", st.session_state.nose_block_sev) or f"레벨 {st.session_state.nose_block_sev}"
    nose_itch_desc = get_desc("rhinitis_itch", st.session_state.nose_itch_sev) or f"레벨 {st.session_state.nose_itch_sev}"
    rhinitis_snot_desc = get_desc("rhinitis_snot_sev", st.session_state.snot_sev) or f"레벨 {st.session_state.snot_sev}"
    
    # Other descriptors from data_mappings
    fatigue_desc = get_desc("fatigue", st.session_state.get("fatigue_sev", 2)) or "보통"
    sweat_desc = get_desc("sweat_amt", 3) or "적당히 흘림"
    sleep_desc = get_desc("sleep_quality", 3) or "보통"

    # ===========================================
    # KOREAN-FIRST PROMPT (의사 관점 진료기록)
    # Primary output: Korean clinical documentation
    # Secondary: English SOAP (supplementary)
    # ===========================================
    system_prompt = f"""
    당신은 한의 임상 가상환자 시나리오 생성 전문가입니다.
    
    ## 역할
    한의사의 관점에서 진료기록부 형식으로 가상환자 시나리오를 생성하세요.
    ❌ 환자 시점 (예: "저는 열이 나고...")이 아닌
    ✅ 의사 시점 (예: "상기 환자는 발열을 호소하며...")으로 작성하세요.
    
    ## 환자 정보 (Patient Data)
    
    ### 1. 인구학적정보 및 활력징후
    - 나이/성별: {st.session_state.age}세 {st.session_state.sex}
    - 직업: {st.session_state.job}
    - 발현시점: {st.session_state.onset}
    - 경과: {st.session_state.course}
    - 활력징후: BP {st.session_state.sbp}/{st.session_state.dbp} mmHg, 맥박 {st.session_state.pulse_rate}회/분, 체온 {st.session_state.temp}°C
    
    ### 2. 병력 및 생활습관
    - 현병력: {st.session_state.history_conditions}
    - 약물력: {st.session_state.meds_specific}
    - 가족력: {st.session_state.family_hx}
    - 음주: {st.session_state.social_alcohol_freq}
    - 흡연: {st.session_state.social_smoke_daily}개피/일
    - 운동강도: {st.session_state.social_exercise_int}
    
    ### 3. 배설 및 식사
    - 식사횟수: {st.session_state.diet_freq}회/일, {st.session_state.diet_regular}
    - 음수량: {st.session_state.water_intake}
    - 대변: {st.session_state.stool_freq}, {st.session_state.stool_color}, {st.session_state.stool_form}
    - 소변: {st.session_state.urine_color}, 주간 {st.session_state.urine_freq_day}회, 야간 {st.session_state.urine_freq_night}회
    
    ### 4. 수면, 땀, 한열
    - 수면: {st.session_state.sleep_hours}시간, {st.session_state.sleep_depth}, 기상시 {st.session_state.sleep_waking_state}
    - 입면장애: {st.session_state.insomnia_onset}, 중도각성: {st.session_state.insomnia_maintain}
    - 땀: {st.session_state.sweat_amt}, {st.session_state.sweat_area}
    - 한열경향: {st.session_state.cold_heat_pref}
    - 음료온도선호: {st.session_state.drink_temp}
    
    ### 5. 정신상태 및 신체검진
    - 기억력: {st.session_state.memory}, 의욕: {st.session_state.motivation}
    - 스트레스대처력: {st.session_state.stress_coping}
    - 부종: {st.session_state.edema}, 멍듦: {st.session_state.bruising}
    - 사지무력감: {st.session_state.limb_weakness}
    - 피부건조도: {st.session_state.skin_dry}, 가려움: {st.session_state.skin_itch}
    - 이명강도: {st.session_state.tinnitus_sev}/5, 난청: {st.session_state.hearing_sev}/5
    - 어지러움: {st.session_state.dizziness_sev}/5
    - 면색: {st.session_state.face_color}
    
    ### 6. 맥진 및 설진
    - 맥진: {st.session_state.pulse_depth}, {st.session_state.pulse_width}, {st.session_state.pulse_strength}, {st.session_state.pulse_smooth}
    - 설질: {st.session_state.tongue_color}, {st.session_state.tongue_size}
    - 설태: {st.session_state.tongue_coat_color}, {st.session_state.tongue_coat_thick}
    
    ### 7. 주소증 및 변증
    - 질환명: {st.session_state.disease}
    - 변증/처방: {selected_pattern}
    
    **감기 증상 (해당시):**
    - 발열: {fever_desc} ({st.session_state.fever_sev}/5)
    - 오한: {chills_desc} ({st.session_state.chills_sev}/5)
    - 콧물: {snot_desc} ({st.session_state.snot_sev}/5)
    - 기침: {cough_desc} ({st.session_state.cough_sev}/5)
    - 기타: {st.session_state.cold_symptoms_spec}
    
    **비염 증상 (해당시):**
    - 재채기: {sneeze_desc} ({st.session_state.sneeze_sev}/5)
    - 코막힘: {nose_block_desc} ({st.session_state.nose_block_sev}/5)
    - 코가려움: {nose_itch_desc} ({st.session_state.nose_itch_sev}/5)
    - 콧물양: {rhinitis_snot_desc} ({st.session_state.snot_sev}/5)
    - 콧물성상: {st.session_state.get('snot_type', 'N/A')}
    
    **요통 증상 (해당시):**
    - 통증강도: {st.session_state.pain_sev}/10
    - 통증양상: {st.session_state.get('pain_nature', [])}
    
    **소화불량 증상 (해당시):**
    - 복만/복통: {st.session_state.pain_sev}/5
    - 증상: {st.session_state.get('dyspepsia_spec', [])}
    
    ## 출력 형식 (JSON)
    반드시 아래 형식으로 JSON을 생성하세요:
    
    {{
      "요약": "환자 요약 (예: 45세 남성, 풍한형 감기, 오한중 발열경 호소)",
      
      "초진기록": "한의사 관점의 상세 초진기록. 반드시 다음 형식으로 작성:
        
        【환자정보】
        상기 환자는 XX세 XX 환자로 [직업] 종사자이다.
        
        【주소증】
        [발현시점]부터 [주요증상]을 주소로 내원하였다.
        
        【현병력】
        [증상의 발생, 경과, 양상을 상세히 기술]
        
        【과거력/가족력】
        [해당사항 기술]
        
        【계통적 문진】
        - 식욕/소화: ...
        - 대변: ...
        - 소변: ...
        - 수면: ...
        - 한열: ...
        - 땀: ...
        - 기타: ...
        
        【망진소견】
        - 면색: ...
        - 설진: ...
        
        【맥진소견】
        ...
        
        【변증】
        상기 소견을 종합하면 [변증명]으로 판단된다.
        
        【치법】
        [치료법 설명]
        
        【처방】
        [처방명] 투여를 고려한다.",
      
      "변증근거": "변증 선정의 근거를 단계별로 설명.
        예시:
        1. 오한이 발열보다 심하다 (惡寒重, 發熱輕) → 풍한(風寒) 시사
        2. 맑고 묽은 콧물 (淸涕) → 한증(寒證) 시사  
        3. 무한(無汗) → 표실증(表實證) 시사
        4. 맥부긴(脈浮緊), 설태박백(舌苔薄白) → 풍한표증 확인
        ∴ 풍한형(風寒型) 감기로 변증하고 [처방명] 투여",
      
      "soap_english": "Brief English SOAP note for international reference (supplementary only):
        S: Chief complaint and history
        O: Vital signs, physical exam, tongue/pulse
        A: TKM pattern diagnosis
        P: Treatment plan and prescription"
    }}
    
    ## 중요 지침
    1. 모든 주요 출력은 한국어로 작성 (English SOAP은 보조용)
    2. 의사 관점으로 작성 (환자 시점 ❌)
    3. 한의학 전문용어 적극 사용 (예: 惡寒, 發熱, 無汗, 脈浮緊 등)
    4. 변증과 처방의 논리적 연결 명확히 기술
    5. 임상진료지침 (Pages 15-19, 21-23) 기준 준수
    """

    with st.spinner('가상환자 시나리오 생성 중...'):
        try:
            response = model.generate_content(system_prompt, generation_config={"response_mime_type": "application/json"})
            data = json.loads(response.text)
            st.success("✅ 생성 완료")
            st.subheader(data.get('요약', data.get('summary', '요약 없음')))
            
            # Korean-first tabs
            t1, t2, t3 = st.tabs(["📋 초진기록 (Primary)", "🧠 변증근거", "🇺🇸 SOAP (Supplementary)"])
            with t1: 
                st.markdown("### 한의사 진료기록")
                st.markdown(data.get('초진기록', data.get('narrative_korean', '기록 없음')))
            with t2: 
                st.markdown("### 변증 논리 및 근거")
                st.info(data.get('변증근거', data.get('reasoning', '근거 없음')))
            with t3: 
                st.markdown("### English SOAP Note (Reference)")
                st.caption("영문 SOAP 노트는 국제 참조용입니다.")
                st.markdown(data.get('soap_english', 'No English SOAP available'))

        except Exception as e:
            st.error(f"오류 발생: {e}")

# --- GENERATE BUTTON (Outside the function) ---
st.markdown("---")
if st.button("🩺 가상환자 시나리오 생성", type="primary"):
    generate_patient()

