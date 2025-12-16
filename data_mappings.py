# data_mappings.py

# ==========================================
# 1. RESPIRATORY & RHINITIS (From Prompt 1)
# ==========================================
PART_1 = {
    # ---------------------------------------------------------
    # COMMON COLD VARIABLES (Source: Appendix 1, Pages 57-60)
    # Weights: [Cold_WC (Wind-Cold), Cold_WH (Wind-Heat), Cold_WD (Wind-Dryness)]
    # Page 15: 감기 변증 - 풍한, 풍열, 풍조
    # ---------------------------------------------------------
    "fever_sev": {
        1: {"desc": "저체온 (35℃ 이하)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.00, "Cold_WD": 0.30}},
        2: {"desc": "정상 (36.0~37.3℃)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.00, "Cold_WD": 0.50}},
        3: {"desc": "미열 (37.4~37.9℃)", "weights": {"Cold_WC": 0.08, "Cold_WH": 0.25, "Cold_WD": 0.15}},
        4: {"desc": "중등도 발열 (38~39.9℃)", "weights": {"Cold_WC": 0.08, "Cold_WH": 0.50, "Cold_WD": 0.05}},
        5: {"desc": "고열 (40℃ 이상)", "weights": {"Cold_WC": 0.08, "Cold_WH": 0.30, "Cold_WD": 0.00}}
    },
    "chills_sev": {
        1: {"desc": "오한 없음", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.40, "Cold_WD": 0.40}},
        2: {"desc": "경미 (약간 으슬으슬함)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40, "Cold_WD": 0.40}},
        3: {"desc": "중등도 (뚜렷한 추위/옷을 껴입음)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.15, "Cold_WD": 0.15}},
        4: {"desc": "심함 (몸이 떨릴 정도)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.00, "Cold_WD": 0.05}},
        5: {"desc": "매우 심함 (이가 부딪힘/극심한 추위)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.00, "Cold_WD": 0.00}}
    },
    "snot_sev": {
        1: {"desc": "콧물이 없음", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00, "Cold_WD": 0.00}},
        2: {"desc": "콧물 조금 흐름 (경미)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.15, "Cold_WD": 0.10}},
        3: {"desc": "콧물이 줄줄 (중등도)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20, "Cold_WD": 0.15}},
        4: {"desc": "콧물이 쉼 없이 흐름 (심함)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.05, "Cold_WD": 0.05}},
        5: {"desc": "수도꼭지처럼 쏟아짐 (매우 심함)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.03, "Cold_WD": 0.00}}
    },
    "snot_color": {
        1: {"desc": "맑고 투명한 콧물", "weights": {"Cold_WC": 0.50, "Cold_WH": 0.15, "Cold_WD": 0.10}},
        2: {"desc": "약간 끈적하고 흰 콧물", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.20, "Cold_WD": 0.10}},
        3: {"desc": "누렇고 진한 콧물", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.65, "Cold_WD": 0.15}}
    },
    "cough_sev": {
        1: {"desc": "기침 안함", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.10, "Cold_WD": 0.00}},
        2: {"desc": "가끔 기침 (간헐적)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10, "Cold_WD": 0.05}},
        3: {"desc": "자주 기침함 (빈번함)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10, "Cold_WD": 0.05}},
        4: {"desc": "하루종일 기침 (지속적)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10, "Cold_WD": 0.05}},
        5: {"desc": "발작적인 기침 (만성적/발작적)", "weights": {"Cold_WC": 0.25, "Cold_WH": 0.60, "Cold_WD": 0.10}}
    },
    "phlegm_amt": {
        1: {"desc": "가래 없음", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.05, "Cold_WD": 0.00}},
        2: {"desc": "마른 가래 (잘 안나옴)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20, "Cold_WD": 0.05}},
        3: {"desc": "소량 (뱉으면 조금 나옴)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.25, "Cold_WD": 0.10}},
        4: {"desc": "다량 (자주 뱉어냄)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10, "Cold_WD": 0.05}},
        5: {"desc": "매우 많음 (계속 생김)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.10, "Cold_WD": 0.00}}
    },
    "phlegm_color": {
        1: {"desc": "맑은 가래", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.00, "Cold_WD": 0.00}},
        2: {"desc": "끈적한 흰 가래", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.10, "Cold_WD": 0.05}},
        3: {"desc": "누런 가래", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15, "Cold_WD": 0.05}},
        4: {"desc": "찐득한 누런/녹색 가래", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.75, "Cold_WD": 0.10}} # Adjusted based on pattern dominance
    },

    # ---------------------------------------------------------
    # RHINITIS VARIABLES (Source: Appendix 2, Pages 93-95)
    # Weights: [R_Yuebi (월비), R_Shegan (사간), R_Minor (소청룡), R_Ling (영강), R_Mahuang (마황부자)]
    # ---------------------------------------------------------
    "rhinitis_sneeze": {
        1: {"desc": "재채기 안함", "weights": {"R_Yuebi": 0.00, "R_Shegan": 0.00, "R_Minor": 0.00, "R_Ling": 0.00, "R_Mahuang": 0.00}},
        2: {"desc": "어쩌다 한두 번 (간헐적)", "weights": {"R_Yuebi": 0.40, "R_Shegan": 0.20, "R_Minor": 0.20, "R_Ling": 0.20, "R_Mahuang": 0.20}},
        3: {"desc": "재채기를 자주 함 (빈번함)", "weights": {"R_Yuebi": 0.30, "R_Shegan": 0.40, "R_Minor": 0.30, "R_Ling": 0.40, "R_Mahuang": 0.40}},
        4: {"desc": "재채기를 매일 함 (지속적)", "weights": {"R_Yuebi": 0.20, "R_Shegan": 0.30, "R_Minor": 0.40, "R_Ling": 0.30, "R_Mahuang": 0.30}},
        5: {"desc": "재채기 발작 수준 (만성적)", "weights": {"R_Yuebi": 0.10, "R_Shegan": 0.10, "R_Minor": 0.10, "R_Ling": 0.10, "R_Mahuang": 0.10}}
    },
    "rhinitis_block": {
        1: {"desc": "코막힘 없음", "weights": {"R_Yuebi": 0.00, "R_Shegan": 0.00, "R_Minor": 0.00, "R_Ling": 0.00, "R_Mahuang": 0.00}},
        2: {"desc": "약간 코가 막힘", "weights": {"R_Yuebi": 0.30, "R_Shegan": 0.06, "R_Minor": 0.06, "R_Ling": 0.06, "R_Mahuang": 0.06}},
        3: {"desc": "코가 막혀서 답답함", "weights": {"R_Yuebi": 0.40, "R_Shegan": 0.08, "R_Minor": 0.08, "R_Ling": 0.08, "R_Mahuang": 0.08}},
        4: {"desc": "코가 많이 막힘", "weights": {"R_Yuebi": 0.20, "R_Shegan": 0.04, "R_Minor": 0.04, "R_Ling": 0.04, "R_Mahuang": 0.04}},
        5: {"desc": "완전히 막힘 (입으로 숨쉼)", "weights": {"R_Yuebi": 0.10, "R_Shegan": 0.02, "R_Minor": 0.02, "R_Ling": 0.02, "R_Mahuang": 0.02}}
    },
    "rhinitis_itch": {
        1: {"desc": "코 가려움 없음", "weights": {"R_Yuebi": 0.00, "R_Shegan": 0.00, "R_Minor": 0.00, "R_Ling": 0.00, "R_Mahuang": 0.00}},
        2: {"desc": "약간 가려움 (무시 가능)", "weights": {"R_Yuebi": 0.20, "R_Shegan": 0.04, "R_Minor": 0.04, "R_Ling": 0.04, "R_Mahuang": 0.04}},
        3: {"desc": "자주 비빔 (신경 쓰임)", "weights": {"R_Yuebi": 0.50, "R_Shegan": 0.10, "R_Minor": 0.10, "R_Ling": 0.10, "R_Mahuang": 0.10}},
        4: {"desc": "심하게 가려움 (일상 방해)", "weights": {"R_Yuebi": 0.20, "R_Shegan": 0.04, "R_Minor": 0.04, "R_Ling": 0.04, "R_Mahuang": 0.04}},
        5: {"desc": "매우 심함 (상처/염증)", "weights": {"R_Yuebi": 0.10, "R_Shegan": 0.02, "R_Minor": 0.02, "R_Ling": 0.02, "R_Mahuang": 0.02}}
    },
    "rhinitis_snot_sev": {
        1: {"desc": "콧물이 없음", "weights": {"R_Yuebi": 0.00, "R_Shegan": 0.00, "R_Minor": 0.00, "R_Ling": 0.00, "R_Mahuang": 0.00}},
        2: {"desc": "콧물 조금 흐름 (경미)", "weights": {"R_Yuebi": 0.20, "R_Shegan": 0.04, "R_Minor": 0.04, "R_Ling": 0.04, "R_Mahuang": 0.04}},
        3: {"desc": "콧물이 줄줄 (중등도)", "weights": {"R_Yuebi": 0.40, "R_Shegan": 0.08, "R_Minor": 0.08, "R_Ling": 0.08, "R_Mahuang": 0.08}},
        4: {"desc": "쉼 없이 흐름 (심함)", "weights": {"R_Yuebi": 0.30, "R_Shegan": 0.06, "R_Minor": 0.06, "R_Ling": 0.06, "R_Mahuang": 0.06}},
        5: {"desc": "감당 불가 (매우 심함)", "weights": {"R_Yuebi": 0.10, "R_Shegan": 0.02, "R_Minor": 0.02, "R_Ling": 0.02, "R_Mahuang": 0.02}}
    },
    "rhinitis_snot_type": {
        1: {"desc": "맑고 투명한 콧물", "weights": {"R_Yuebi": 0.94, "R_Shegan": 0.14, "R_Minor": 0.20, "R_Ling": 0.20, "R_Mahuang": 0.20}},
        2: {"desc": "약간 끈적하고 흰 콧물", "weights": {"R_Yuebi": 0.06, "R_Shegan": 0.06, "R_Minor": 0.00, "R_Ling": 0.00, "R_Mahuang": 0.00}},
        3: {"desc": "누렇고 진한 콧물", "weights": {"R_Yuebi": 0.00, "R_Shegan": 0.00, "R_Minor": 0.00, "R_Ling": 0.00, "R_Mahuang": 0.00}}
    }
}

# ==========================================
# 2. INTERNAL & EXCRETION (From Prompt 2)
# ==========================================
PART_2 = {
    "diet_freq": {
        1: {"desc": "1회 (1일)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}},
        2: {"desc": "2회 (1일)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}},
        3: {"desc": "3회 (1일)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}}, # Source: 50% 30% 30%
        4: {"desc": "4회 (1일)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}},
        5: {"desc": "5회 이상 (소식/자주)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}} 
    },
    "diet_regular": {
        1: {"desc": "매우 규칙적", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40}},
        2: {"desc": "규칙적", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}},
        3: {"desc": "왔다갔다 함", "weights": {"Cold_WC": 0.45, "Cold_WH": 0.45}},
        4: {"desc": "불규칙", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}},
        5: {"desc": "매우 불규칙", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}}
    },
    "diet_amt": {
        1: {"desc": "매우 적음 (<1공기)", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.15}},
        2: {"desc": "적은 편 (1-2공기)", "weights": {"Cold_WC": 0.25, "Cold_WH": 0.25}},
        3: {"desc": "보통 (3공기)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        4: {"desc": "많음 (4-5공기/과식)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}},
        5: {"desc": "매우 많음 (>5공기/폭식)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}}
    },
    "digestion": {
        1: {"desc": "매우 좋음 (속이 편안함)", "weights": {"Cold_WC": 0.26, "Cold_WH": 0.26}},
        2: {"desc": "좋은 편", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40}}, # Normalized from 20% raw
        3: {"desc": "속이 자주 더부룩함", "weights": {"Cold_WC": 0.26, "Cold_WH": 0.26}},
        4: {"desc": "거의 매일 속이 불편함", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}},
        5: {"desc": "만성적인 소화불량", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}}
    },
    "appetite": {
        1: {"desc": "식욕 없음", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}},
        2: {"desc": "입맛 저하", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        3: {"desc": "보통 (자연스럽게 배고픔)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40}},
        4: {"desc": "입맛이 늘 좋음", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        5: {"desc": "식욕 왕성함 (항진)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}
    },

    # ---------------------------------------------------------
    # STOOL (Source: Page 67)
    # ---------------------------------------------------------
    "stool_freq": {
        1: {"desc": "매우 적음 (주 2회 이하)", "weights": {"Cold_WC": 0.04, "Cold_WH": 0.16}},
        2: {"desc": "다소 적음 (주 3-4회)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.30}},
        3: {"desc": "정상 (1일 1-2회)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40}},
        4: {"desc": "잦은 편 (1일 2-3회)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.10}},
        5: {"desc": "매우 잦음 (1일 3-4회 이상)", "weights": {"Cold_WC": 0.16, "Cold_WH": 0.04}}
    },
    "stool_color": {
        1: {"desc": "황금색/밝은 노란색", "weights": {"Cold_WC": 0.06, "Cold_WH": 0.06}},
        2: {"desc": "황토색/진한 노란색", "weights": {"Cold_WC": 0.06, "Cold_WH": 0.06}},
        3: {"desc": "황갈색/된장색", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40}},
        4: {"desc": "진한 갈색/고동색", "weights": {"Cold_WC": 0.46, "Cold_WH": 0.46}},
        5: {"desc": "녹갈색/짙은 풀색", "weights": {"Cold_WC": 0.04, "Cold_WH": 0.04}} # Level 6 (Black) is 2%
    },
    "stool_form": {
        1: {"desc": "단단한 염소 똥 모양", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.10}},
        2: {"desc": "딱딱/울퉁불퉁한 소시지", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.20}},
        3: {"desc": "표면이 갈라진 소시지", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}},
        4: {"desc": "부드러운 떡가래 모양", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}},
        5: {"desc": "물렁물렁한 수제비 모양", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.00}} # Levels 6 (Mushy) & 7 (Watery) follow WC pattern
    },

    # ---------------------------------------------------------
    # URINE (Source: Pages 68-69)
    # ---------------------------------------------------------
    "urine_freq_day": {
        1: {"desc": "매우 적음 (0-2회)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}},
        2: {"desc": "다소 적음 (3-4회)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        3: {"desc": "정상 (5-7회)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.40}},
        4: {"desc": "잦은 편 (8-10회)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        5: {"desc": "매우 잦음 (11회 이상)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}
    },
    "urine_freq_night": {
        1: {"desc": "0회 (안 깸)", "weights": {"Cold_WC": 0.70, "Cold_WH": 0.50}},
        2: {"desc": "1회", "weights": {"Cold_WC": 0.26, "Cold_WH": 0.26}},
        3: {"desc": "2회", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.06}},
        4: {"desc": "3-4회", "weights": {"Cold_WC": 0.06, "Cold_WH": 0.00}},
        5: {"desc": "5회 이상", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}}
    },
    "urine_color": {
        1: {"desc": "무색/물처럼 맑음", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.00}},
        2: {"desc": "매우 옅은 노란색", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.00}},
        3: {"desc": "옅은 노란색/볏짚색", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}},
        4: {"desc": "맑은 노란색", "weights": {"Cold_WC": 0.36, "Cold_WH": 0.36}},
        5: {"desc": "다소 진한 노란색", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}} # L6, L7, L8 are increasingly Heat/Dark
    },
    "urine_comfort": {
        1: {"desc": "소변 보고 속이 아주 시원함", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        2: {"desc": "소변 보고 시원하고 개운함", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.50}},
        3: {"desc": "소변 보고 불편함 없이 무난함", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        4: {"desc": "소변 보고 뭔가 불편함", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}},
        5: {"desc": "소변 보고 전혀 개운치 않음", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}}
    }
}

# ==========================================
# 3. BODY, SLEEP & TEMP (From Prompt 3)
# ==========================================
PART_3 = {
    # ---------------------------------------------------------
    # SLEEP (Source: Pages 72-73)
    # Weights: [Cold_WC (Wind-Cold), Cold_WH (Wind-Heat)]
    # ---------------------------------------------------------
    "sleep_quality": {
        1: {"desc": "매우 힘들다 (개운치 않음)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.20}},
        2: {"desc": "힘들다 (찌뿌둥함)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.30}},
        3: {"desc": "보통 (별로 개운하지도 않음)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15}},
        4: {"desc": "상쾌하다 (기분 좋게 일어남)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.03}},
        5: {"desc": "매우 상쾌하다 (눈이 번쩍)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}}
    },
    "sleep_hours": {
        1: {"desc": "매우 부족 (4시간 이하)", "weights": {"Cold_WC": 0.03, "Cold_WH": 0.03}},
        2: {"desc": "부족 (5-6시간)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.20}},
        3: {"desc": "적정 (7-9시간)", "weights": {"Cold_WC": 0.50, "Cold_WH": 0.25}},
        4: {"desc": "다소 많음 (10시간)", "weights": {"Cold_WC": 0.03, "Cold_WH": 0.02}},
        5: {"desc": "매우 많음 (11시간 이상)", "weights": {"Cold_WC": 0.02, "Cold_WH": 0.01}}
    },
    "sleep_depth": {
        1: {"desc": "매우 얕음 (선잠)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.03}},
        2: {"desc": "얕은 편 (설침)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.15}},
        3: {"desc": "보통", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.20}},
        4: {"desc": "깊은 편 (숙면)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}},
        5: {"desc": "매우 깊음 (아주 푹 잠)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.03}}
    },

    # ---------------------------------------------------------
    # TEMPERATURE & SWEAT (Source: Pages 74-75)
    # ---------------------------------------------------------
    "sweat_amt": {
        1: {"desc": "땀이 안 남 (무한)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.02}}, # Text ambiguous, prioritized WC for no-sweat
        2: {"desc": "땀이 적음", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15}},
        3: {"desc": "적당히 흘림", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.20}},
        4: {"desc": "땀이 많은 편", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.05}},
        5: {"desc": "비오듯 쏟아짐 (다한/도한)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.02}}
    },
    "cold_heat_pref": {
        1: {"desc": "몸이 많이 뜨거운 편 (열)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.00}},
        2: {"desc": "약간 뜨거운 편", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.00}},
        3: {"desc": "보통 (차지도 뜨겁지도 않음)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.20}},
        4: {"desc": "약간 찬 편 (냉)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        5: {"desc": "많이 찬 편 (심한 냉증)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}
    },
    "drink_temp": {
        1: {"desc": "따뜻한 것만 (찬 것 못 마심)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.05}},
        2: {"desc": "따뜻한 것 선호", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}},
        3: {"desc": "상관없음", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.25}},
        4: {"desc": "찬 것 선호 (아이스)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15}},
        5: {"desc": "찬 것만 (얼죽아)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.30}}
    },

    # ---------------------------------------------------------
    # BODY & PHYSICAL CONDITION (Source: Pages 76-79)
    # ---------------------------------------------------------
    "fatigue": {
        1: {"desc": "전혀 안 피곤함", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}},
        2: {"desc": "가벼운 피로 (경미)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.20}},
        3: {"desc": "늘 피곤함 (중등도)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}},
        4: {"desc": "너무 지침 (심함)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.05}},
        5: {"desc": "번아웃 (매우 심함)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.05}}
    },
    "edema": {
        1: {"desc": "전혀 안 부음", "weights": {"Cold_WC": 0.50, "Cold_WH": 0.30}},
        2: {"desc": "일시적으로 부음", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.15}},
        3: {"desc": "자주 부음", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.05}},
        4: {"desc": "붓기가 안 빠짐", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.00}},
        5: {"desc": "항상 부어있음", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}}
    },
    "bruising": {
        1: {"desc": "멍이 잘 안 듦", "weights": {"Cold_WC": 0.50, "Cold_WH": 0.30}},
        2: {"desc": "세게 부딪혀야 듦", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.10}},
        3: {"desc": "아주 쉽게 멍이 듦", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.05}},
        4: {"desc": "조금만 스쳐도 멍", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.00}},
        5: {"desc": "이유 없이 멍이 듦", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}}
    },

    # ---------------------------------------------------------
    # FACE, SKIN & SENSORY (Source: Pages 80-83)
    # ---------------------------------------------------------
    "face_color": {
        1: {"desc": "희다 (창백)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15}},
        2: {"desc": "황색 (누렇다)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.25}},
        3: {"desc": "붉은색 (홍조)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.05}},
        4: {"desc": "적갈색 (칙칙함)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.02}},
        5: {"desc": "흑색 (어둡다)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.02}}
    },
    "skin_dry": {
        1: {"desc": "촉촉함 (정상)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15}},
        2: {"desc": "속당김 (경미)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.25}},
        3: {"desc": "거칠거칠함 (중등도)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.10}},
        4: {"desc": "각질이 심함", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.00}},
        5: {"desc": "악건성 (아픔)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.00}}
    },
    "eye_discomfort": {
        1: {"desc": "편안함", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.15}},
        2: {"desc": "가끔 뻑뻑함", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.30}},
        3: {"desc": "자주 건조함", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.30}},
        4: {"desc": "매일 건조함", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.10}},
        5: {"desc": "안구건조증 심함", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.10}}
    },
    "tinnitus": {
        1: {"desc": "없음", "weights": {"Cold_WC": 0.80, "Cold_WH": 0.40}},
        2: {"desc": "가끔 삐 소리 (일시적)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}},
        3: {"desc": "자주 삐 소리 (간헐적)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.00}},
        4: {"desc": "계속 윙윙거림 (지속적)", "weights": {"Cold_WC": 0.03, "Cold_WH": 0.00}},
        5: {"desc": "소리 때문에 잠 못 잠", "weights": {"Cold_WC": 0.02, "Cold_WH": 0.00}}
    }
}

# ==========================================
# 4. MENTAL & DIAGNOSTICS (From Prompt 4)
# ==========================================
PART_4 = {
    # ---------------------------------------------------------
    # MENTAL STATE & EMOTION (Source: Pages 86-89)
    # Weights: [Cold_WC (Wind-Cold), Cold_WH (Wind-Heat)]
    # Note: Most mental variables show identical or default distributions (e.g., 5%/5%)
    # in the source text, suggesting they are not primary differentiators for Cold types.
    # ---------------------------------------------------------
    "mental_state": {
        1: {"desc": "매우 맑음 (Very Clear)", "weights": {"Cold_WC": 0.03, "Cold_WH": 0.03}}, 
        2: {"desc": "대체로 맑음 (Clear)", "weights": {"Cold_WC": 0.35, "Cold_WH": 0.35}}, 
        3: {"desc": "가끔 흐릿함 (Foggy)", "weights": {"Cold_WC": 0.35, "Cold_WH": 0.35}}, 
        4: {"desc": "자주 흐릿함 (Confused)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "혼미 (Coma/Delirium)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}} 
    },
    "memory": {
        1: {"desc": "매우 좋음", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.15}}, 
        2: {"desc": "좋음", "weights": {"Cold_WC": 0.35, "Cold_WH": 0.35}}, 
        3: {"desc": "깜빡임 (건망증)", "weights": {"Cold_WC": 0.25, "Cold_WH": 0.25}}, 
        4: {"desc": "나쁨 (지장 있음)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "매우 나쁨", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}} 
    },
    "motivation": {
        1: {"desc": "의욕 충만", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}}, 
        2: {"desc": "활력 있음", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.15}}, 
        3: {"desc": "보통", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}}, 
        4: {"desc": "의욕 없음 (무기력)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}}, 
        5: {"desc": "완전 무기력", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}} 
    },
    "personality_speed": {
        1: {"desc": "매우 느긋함", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}}, 
        2: {"desc": "느긋한 편", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        3: {"desc": "보통", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}}, 
        4: {"desc": "급한 편", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "매우 성급함", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}} 
    },
    "emot_anger": {
        1: {"desc": "화를 안 냄 (평온)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}}, 
        2: {"desc": "잘 참음", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        3: {"desc": "보통", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}}, 
        4: {"desc": "쉽게 화냄 (짜증)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "분노 조절 불가", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}} 
    },
    "emot_anxiety": {
        1: {"desc": "평온함", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}}, 
        2: {"desc": "가끔 긴장", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        3: {"desc": "약간 불안", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}}, 
        4: {"desc": "자꾸 불안함 (안절부절)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "극심한 불안 (공황)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}} 
    },
    "emot_depress": {
        1: {"desc": "매우 낙관적", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}},
        2: {"desc": "낙관적", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        3: {"desc": "보통", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}}, 
        4: {"desc": "우울한 편", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "심한 우울 (비애)", "weights": {"Cold_WC": 0.05, "Cold_WH": 0.05}} 
    },

    # ---------------------------------------------------------
    # PULSE DIAGNOSIS (Source: Page 62 & 90-91)
    # ---------------------------------------------------------
    "pulse_rate": {
        # Sourced from Page 62 (Source 27-28) as Page 90+ lacks rate data.
        1: {"desc": "매우 느림 (지맥)", "weights": {"Cold_WC": 0.01, "Cold_WH": 0.00}}, 
        2: {"desc": "느림 (완맥)", "weights": {"Cold_WC": 0.03, "Cold_WH": 0.02}}, 
        3: {"desc": "중간 (평맥)", "weights": {"Cold_WC": 0.25, "Cold_WH": 0.25}}, 
        4: {"desc": "약간 빠름 (삭맥)", "weights": {"Cold_WC": 0.35, "Cold_WH": 0.25}}, 
        5: {"desc": "매우 빠름 (질맥)", "weights": {"Cold_WC": 0.02, "Cold_WH": 0.08}} 
    },
    "pulse_depth": {
        1: {"desc": "부맥 (Floating)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}}, 
        2: {"desc": "중간-부 (Slightly Floating)", "weights": {"Cold_WC": 0.40, "Cold_WH": 0.30}}, 
        3: {"desc": "중간 (Middle)", "weights": {"Cold_WC": 0.20, "Cold_WH": 0.20}},
        4: {"desc": "침맥 (Sinking)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "복맥 (Hidden)", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}} 
    },
    "pulse_strength": {
        1: {"desc": "매우 약함 (미맥)", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}}, 
        2: {"desc": "약함 (약맥)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        3: {"desc": "보통 (완맥)", "weights": {"Cold_WC": 0.30, "Cold_WH": 0.30}}, 
        4: {"desc": "강함 (실맥)", "weights": {"Cold_WC": 0.10, "Cold_WH": 0.10}}, 
        5: {"desc": "매우 강함 (대맥)", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}} 
    },

    # ---------------------------------------------------------
    # TONGUE DIAGNOSIS (Source: Pages 91-92)
    # ---------------------------------------------------------
    "tongue_color": {
        1: {"desc": "담백설 (Pale)", "weights": {"Cold_WC": 0.15, "Cold_WH": 0.05}}, 
        2: {"desc": "담홍설 (Pink/Normal)", "weights": {"Cold_WC": 0.25, "Cold_WH": 0.05}}, 
        3: {"desc": "홍설 (Red)", "weights": {"Cold_WC": 0.25, "Cold_WH": 0.15}}, 
        4: {"desc": "강설 (Dark Red)", "weights": {"Cold_WC": 0.02, "Cold_WH": 0.03}}, 
        5: {"desc": "청자설 (Purple/Blue)", "weights": {"Cold_WC": 0.03, "Cold_WH": 0.02}} 
    },
    "tongue_coat": {
        1: {"desc": "황태 (Yellow Coat)", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.50}}, 
        2: {"desc": "백태 (White Coat)", "weights": {"Cold_WC": 0.70, "Cold_WH": 0.30}}, 
        3: {"desc": "무태 (No Coat)", "weights": {"Cold_WC": 0.00, "Cold_WH": 0.00}} 
    }
}

# ==========================================
# MERGE ALL DATA
# ==========================================
CLINICAL_DATA = {}
CLINICAL_DATA.update(PART_1)
CLINICAL_DATA.update(PART_2)
CLINICAL_DATA.update(PART_3)
CLINICAL_DATA.update(PART_4)

# NOTE: PART_5 is added after being defined below

# Helper function to get text
def get_desc(variable, level):
    try:
        return CLINICAL_DATA[variable][level]['desc']
    except:
        return ""

# Helper function to get weights
def get_weights(variable, level):
    try:
        return CLINICAL_DATA[variable][level]['weights']
    except:
        return {}

# ==========================================
# 5. BACK PAIN & DYSPEPSIA PATTERNS (Page 23)
# 한열허실 based pattern classification
# ==========================================
PART_5 = {
    # ---------------------------------------------------------
    # BACK PAIN (요통) SYMPTOM WEIGHTS - Page 23
    # Pattern Keys: BP_Cold, BP_Heat, BP_QiDef, BP_YangDef, BP_YinDef, 
    #               BP_FoodStag, BP_Phlegm, BP_QiStag, BP_BloodStasis
    # ---------------------------------------------------------
    "back_pain_sev": {
        1: {"desc": "통증 없음", "weights": {
            "BP_Cold": 0.00, "BP_Heat": 0.00, "BP_QiDef": 0.00, "BP_YangDef": 0.00, "BP_YinDef": 0.00,
            "BP_FoodStag": 0.00, "BP_Phlegm": 0.00, "BP_QiStag": 0.00, "BP_BloodStasis": 0.00}},
        2: {"desc": "약간 (경미)", "weights": {
            "BP_Cold": 0.15, "BP_Heat": 0.15, "BP_QiDef": 0.30, "BP_YangDef": 0.25, "BP_YinDef": 0.25,
            "BP_FoodStag": 0.20, "BP_Phlegm": 0.20, "BP_QiStag": 0.20, "BP_BloodStasis": 0.10}},
        3: {"desc": "중등도", "weights": {
            "BP_Cold": 0.35, "BP_Heat": 0.35, "BP_QiDef": 0.40, "BP_YangDef": 0.40, "BP_YinDef": 0.40,
            "BP_FoodStag": 0.40, "BP_Phlegm": 0.40, "BP_QiStag": 0.40, "BP_BloodStasis": 0.30}},
        4: {"desc": "심함", "weights": {
            "BP_Cold": 0.35, "BP_Heat": 0.35, "BP_QiDef": 0.25, "BP_YangDef": 0.25, "BP_YinDef": 0.25,
            "BP_FoodStag": 0.30, "BP_Phlegm": 0.30, "BP_QiStag": 0.30, "BP_BloodStasis": 0.40}},
        5: {"desc": "매우 심함", "weights": {
            "BP_Cold": 0.15, "BP_Heat": 0.15, "BP_QiDef": 0.05, "BP_YangDef": 0.10, "BP_YinDef": 0.10,
            "BP_FoodStag": 0.10, "BP_Phlegm": 0.10, "BP_QiStag": 0.10, "BP_BloodStasis": 0.20}}
    },
    "back_pain_cold_agg": {  # 한통 - worse with cold
        1: {"desc": "냉기에 무관", "weights": {
            "BP_Cold": 0.00, "BP_Heat": 0.60, "BP_QiDef": 0.30, "BP_YangDef": 0.10, "BP_YinDef": 0.40,
            "BP_FoodStag": 0.40, "BP_Phlegm": 0.30, "BP_QiStag": 0.40, "BP_BloodStasis": 0.30}},
        2: {"desc": "약간 민감", "weights": {
            "BP_Cold": 0.20, "BP_Heat": 0.30, "BP_QiDef": 0.40, "BP_YangDef": 0.30, "BP_YinDef": 0.35,
            "BP_FoodStag": 0.35, "BP_Phlegm": 0.40, "BP_QiStag": 0.35, "BP_BloodStasis": 0.35}},
        3: {"desc": "찬 것에 악화", "weights": {
            "BP_Cold": 0.50, "BP_Heat": 0.10, "BP_QiDef": 0.20, "BP_YangDef": 0.40, "BP_YinDef": 0.20,
            "BP_FoodStag": 0.20, "BP_Phlegm": 0.25, "BP_QiStag": 0.20, "BP_BloodStasis": 0.25}},
        4: {"desc": "냉기시 심함", "weights": {
            "BP_Cold": 0.25, "BP_Heat": 0.00, "BP_QiDef": 0.08, "BP_YangDef": 0.15, "BP_YinDef": 0.05,
            "BP_FoodStag": 0.05, "BP_Phlegm": 0.05, "BP_QiStag": 0.05, "BP_BloodStasis": 0.08}},
        5: {"desc": "극심한 한통", "weights": {
            "BP_Cold": 0.05, "BP_Heat": 0.00, "BP_QiDef": 0.02, "BP_YangDef": 0.05, "BP_YinDef": 0.00,
            "BP_FoodStag": 0.00, "BP_Phlegm": 0.00, "BP_QiStag": 0.00, "BP_BloodStasis": 0.02}}
    },
    "back_pain_warmth_relief": {  # 득온즉감 - better with warmth
        1: {"desc": "온기에 무관", "weights": {
            "BP_Cold": 0.00, "BP_Heat": 0.50, "BP_QiDef": 0.30, "BP_YangDef": 0.10, "BP_YinDef": 0.50,
            "BP_FoodStag": 0.40, "BP_Phlegm": 0.30, "BP_QiStag": 0.40, "BP_BloodStasis": 0.30}},
        2: {"desc": "약간 호전", "weights": {
            "BP_Cold": 0.20, "BP_Heat": 0.30, "BP_QiDef": 0.35, "BP_YangDef": 0.30, "BP_YinDef": 0.30,
            "BP_FoodStag": 0.35, "BP_Phlegm": 0.35, "BP_QiStag": 0.35, "BP_BloodStasis": 0.35}},
        3: {"desc": "따뜻하면 호전", "weights": {
            "BP_Cold": 0.50, "BP_Heat": 0.15, "BP_QiDef": 0.25, "BP_YangDef": 0.40, "BP_YinDef": 0.15,
            "BP_FoodStag": 0.20, "BP_Phlegm": 0.25, "BP_QiStag": 0.20, "BP_BloodStasis": 0.25}},
        4: {"desc": "온찜질 필수", "weights": {
            "BP_Cold": 0.25, "BP_Heat": 0.05, "BP_QiDef": 0.08, "BP_YangDef": 0.15, "BP_YinDef": 0.05,
            "BP_FoodStag": 0.05, "BP_Phlegm": 0.08, "BP_QiStag": 0.05, "BP_BloodStasis": 0.08}},
        5: {"desc": "극도 온열선호", "weights": {
            "BP_Cold": 0.05, "BP_Heat": 0.00, "BP_QiDef": 0.02, "BP_YangDef": 0.05, "BP_YinDef": 0.00,
            "BP_FoodStag": 0.00, "BP_Phlegm": 0.02, "BP_QiStag": 0.00, "BP_BloodStasis": 0.02}}
    },
    "back_pain_stabbing": {  # 자통 - stabbing pain (Blood Stasis marker)
        1: {"desc": "찌르는 통증 없음", "weights": {
            "BP_Cold": 0.40, "BP_Heat": 0.40, "BP_QiDef": 0.50, "BP_YangDef": 0.45, "BP_YinDef": 0.45,
            "BP_FoodStag": 0.45, "BP_Phlegm": 0.40, "BP_QiStag": 0.30, "BP_BloodStasis": 0.05}},
        2: {"desc": "가끔 찌름", "weights": {
            "BP_Cold": 0.35, "BP_Heat": 0.35, "BP_QiDef": 0.30, "BP_YangDef": 0.30, "BP_YinDef": 0.30,
            "BP_FoodStag": 0.30, "BP_Phlegm": 0.35, "BP_QiStag": 0.35, "BP_BloodStasis": 0.20}},
        3: {"desc": "자주 찌르는 통증", "weights": {
            "BP_Cold": 0.20, "BP_Heat": 0.20, "BP_QiDef": 0.15, "BP_YangDef": 0.20, "BP_YinDef": 0.20,
            "BP_FoodStag": 0.20, "BP_Phlegm": 0.20, "BP_QiStag": 0.25, "BP_BloodStasis": 0.40}},
        4: {"desc": "심한 자통", "weights": {
            "BP_Cold": 0.05, "BP_Heat": 0.05, "BP_QiDef": 0.05, "BP_YangDef": 0.05, "BP_YinDef": 0.05,
            "BP_FoodStag": 0.05, "BP_Phlegm": 0.05, "BP_QiStag": 0.08, "BP_BloodStasis": 0.25}},
        5: {"desc": "칼로 찌르는 듯", "weights": {
            "BP_Cold": 0.00, "BP_Heat": 0.00, "BP_QiDef": 0.00, "BP_YangDef": 0.00, "BP_YinDef": 0.00,
            "BP_FoodStag": 0.00, "BP_Phlegm": 0.00, "BP_QiStag": 0.02, "BP_BloodStasis": 0.10}}
    },
    "back_pain_moving": {  # 유주통 - moving pain (Phlegm marker)
        1: {"desc": "고정 통증", "weights": {
            "BP_Cold": 0.35, "BP_Heat": 0.35, "BP_QiDef": 0.40, "BP_YangDef": 0.40, "BP_YinDef": 0.40,
            "BP_FoodStag": 0.40, "BP_Phlegm": 0.05, "BP_QiStag": 0.20, "BP_BloodStasis": 0.45}},
        2: {"desc": "가끔 이동", "weights": {
            "BP_Cold": 0.35, "BP_Heat": 0.35, "BP_QiDef": 0.35, "BP_YangDef": 0.35, "BP_YinDef": 0.35,
            "BP_FoodStag": 0.35, "BP_Phlegm": 0.25, "BP_QiStag": 0.30, "BP_BloodStasis": 0.30}},
        3: {"desc": "통증 부위 변화", "weights": {
            "BP_Cold": 0.20, "BP_Heat": 0.20, "BP_QiDef": 0.20, "BP_YangDef": 0.20, "BP_YinDef": 0.20,
            "BP_FoodStag": 0.20, "BP_Phlegm": 0.40, "BP_QiStag": 0.35, "BP_BloodStasis": 0.20}},
        4: {"desc": "자주 이동", "weights": {
            "BP_Cold": 0.08, "BP_Heat": 0.08, "BP_QiDef": 0.05, "BP_YangDef": 0.05, "BP_YinDef": 0.05,
            "BP_FoodStag": 0.05, "BP_Phlegm": 0.25, "BP_QiStag": 0.12, "BP_BloodStasis": 0.05}},
        5: {"desc": "항상 이동 (유주통)", "weights": {
            "BP_Cold": 0.02, "BP_Heat": 0.02, "BP_QiDef": 0.00, "BP_YangDef": 0.00, "BP_YinDef": 0.00,
            "BP_FoodStag": 0.00, "BP_Phlegm": 0.05, "BP_QiStag": 0.03, "BP_BloodStasis": 0.00}}
    },

    # ---------------------------------------------------------
    # DYSPEPSIA (소화불량) SYMPTOM WEIGHTS - Page 23
    # Pattern Keys: DY_Cold, DY_Heat, DY_QiDef, DY_YangDef, DY_YinDef,
    #               DY_FoodStag, DY_Phlegm, DY_QiStag, DY_BloodStasis
    # ---------------------------------------------------------
    "dyspepsia_bloating": {
        1: {"desc": "복부팽만 없음", "weights": {
            "DY_Cold": 0.20, "DY_Heat": 0.20, "DY_QiDef": 0.15, "DY_YangDef": 0.15, "DY_YinDef": 0.25,
            "DY_FoodStag": 0.05, "DY_Phlegm": 0.10, "DY_QiStag": 0.10, "DY_BloodStasis": 0.25}},
        2: {"desc": "약간 더부룩함", "weights": {
            "DY_Cold": 0.25, "DY_Heat": 0.25, "DY_QiDef": 0.30, "DY_YangDef": 0.25, "DY_YinDef": 0.30,
            "DY_FoodStag": 0.20, "DY_Phlegm": 0.25, "DY_QiStag": 0.25, "DY_BloodStasis": 0.30}},
        3: {"desc": "식후 불편", "weights": {
            "DY_Cold": 0.30, "DY_Heat": 0.30, "DY_QiDef": 0.35, "DY_YangDef": 0.35, "DY_YinDef": 0.30,
            "DY_FoodStag": 0.35, "DY_Phlegm": 0.35, "DY_QiStag": 0.35, "DY_BloodStasis": 0.30}},
        4: {"desc": "심한 복만", "weights": {
            "DY_Cold": 0.20, "DY_Heat": 0.20, "DY_QiDef": 0.15, "DY_YangDef": 0.20, "DY_YinDef": 0.12,
            "DY_FoodStag": 0.30, "DY_Phlegm": 0.25, "DY_QiStag": 0.25, "DY_BloodStasis": 0.12}},
        5: {"desc": "극심한 팽만", "weights": {
            "DY_Cold": 0.05, "DY_Heat": 0.05, "DY_QiDef": 0.05, "DY_YangDef": 0.05, "DY_YinDef": 0.03,
            "DY_FoodStag": 0.10, "DY_Phlegm": 0.05, "DY_QiStag": 0.05, "DY_BloodStasis": 0.03}}
    },
    "dyspepsia_cold_food_agg": {  # 찬 음식에 악화
        1: {"desc": "찬 음식 무관", "weights": {
            "DY_Cold": 0.05, "DY_Heat": 0.50, "DY_QiDef": 0.30, "DY_YangDef": 0.10, "DY_YinDef": 0.40,
            "DY_FoodStag": 0.35, "DY_Phlegm": 0.30, "DY_QiStag": 0.35, "DY_BloodStasis": 0.35}},
        2: {"desc": "약간 민감", "weights": {
            "DY_Cold": 0.20, "DY_Heat": 0.30, "DY_QiDef": 0.35, "DY_YangDef": 0.25, "DY_YinDef": 0.35,
            "DY_FoodStag": 0.35, "DY_Phlegm": 0.35, "DY_QiStag": 0.35, "DY_BloodStasis": 0.35}},
        3: {"desc": "찬것 먹으면 악화", "weights": {
            "DY_Cold": 0.45, "DY_Heat": 0.15, "DY_QiDef": 0.25, "DY_YangDef": 0.40, "DY_YinDef": 0.20,
            "DY_FoodStag": 0.25, "DY_Phlegm": 0.30, "DY_QiStag": 0.25, "DY_BloodStasis": 0.25}},
        4: {"desc": "찬음식 기피", "weights": {
            "DY_Cold": 0.25, "DY_Heat": 0.05, "DY_QiDef": 0.08, "DY_YangDef": 0.20, "DY_YinDef": 0.05,
            "DY_FoodStag": 0.05, "DY_Phlegm": 0.05, "DY_QiStag": 0.05, "DY_BloodStasis": 0.05}},
        5: {"desc": "절대 찬것 안됨", "weights": {
            "DY_Cold": 0.05, "DY_Heat": 0.00, "DY_QiDef": 0.02, "DY_YangDef": 0.05, "DY_YinDef": 0.00,
            "DY_FoodStag": 0.00, "DY_Phlegm": 0.00, "DY_QiStag": 0.00, "DY_BloodStasis": 0.00}}
    },
    "dyspepsia_acid_reflux": {  # 신물 - acid reflux
       
        1: {"desc": "신물 없음", "weights": {
            "DY_Cold": 0.50, "DY_Heat": 0.30, "DY_QiDef": 0.45, "DY_YangDef": 0.50, "DY_YinDef": 0.35,
            "DY_FoodStag": 0.20, "DY_Phlegm": 0.40, "DY_QiStag": 0.30, "DY_BloodStasis": 0.45}},
        2: {"desc": "가끔 신물", "weights": {
            "DY_Cold": 0.30, "DY_Heat": 0.35, "DY_QiDef": 0.35, "DY_YangDef": 0.30, "DY_YinDef": 0.35,
            "DY_FoodStag": 0.35, "DY_Phlegm": 0.35, "DY_QiStag": 0.35, "DY_BloodStasis": 0.35}},
        3: {"desc": "식후 신물", "weights": {
            "DY_Cold": 0.15, "DY_Heat": 0.25, "DY_QiDef": 0.15, "DY_YangDef": 0.15, "DY_YinDef": 0.20,
            "DY_FoodStag": 0.30, "DY_Phlegm": 0.20, "DY_QiStag": 0.25, "DY_BloodStasis": 0.15}},
        4: {"desc": "자주 신물", "weights": {
            "DY_Cold": 0.05, "DY_Heat": 0.08, "DY_QiDef": 0.05, "DY_YangDef": 0.05, "DY_YinDef": 0.08,
            "DY_FoodStag": 0.12, "DY_Phlegm": 0.05, "DY_QiStag": 0.08, "DY_BloodStasis": 0.05}},
        5: {"desc": "항상 신물", "weights": {
            "DY_Cold": 0.00, "DY_Heat": 0.02, "DY_QiDef": 0.00, "DY_YangDef": 0.00, "DY_YinDef": 0.02,
            "DY_FoodStag": 0.03, "DY_Phlegm": 0.00, "DY_QiStag": 0.02, "DY_BloodStasis": 0.00}}
    },
    "dyspepsia_foul_belch": {  # 부패취 - foul belching (Food Stagnation marker)
        1: {"desc": "트림 냄새 없음", "weights": {
            "DY_Cold": 0.50, "DY_Heat": 0.40, "DY_QiDef": 0.50, "DY_YangDef": 0.50, "DY_YinDef": 0.45,
            "DY_FoodStag": 0.05, "DY_Phlegm": 0.40, "DY_QiStag": 0.40, "DY_BloodStasis": 0.50}},
        2: {"desc": "가끔 냄새", "weights": {
            "DY_Cold": 0.30, "DY_Heat": 0.35, "DY_QiDef": 0.30, "DY_YangDef": 0.30, "DY_YinDef": 0.35,
            "DY_FoodStag": 0.25, "DY_Phlegm": 0.35, "DY_QiStag": 0.35, "DY_BloodStasis": 0.30}},
        3: {"desc": "트림시 냄새", "weights": {
            "DY_Cold": 0.15, "DY_Heat": 0.20, "DY_QiDef": 0.15, "DY_YangDef": 0.15, "DY_YinDef": 0.15,
            "DY_FoodStag": 0.40, "DY_Phlegm": 0.20, "DY_QiStag": 0.20, "DY_BloodStasis": 0.15}},
        4: {"desc": "부패취 심함", "weights": {
            "DY_Cold": 0.05, "DY_Heat": 0.05, "DY_QiDef": 0.05, "DY_YangDef": 0.05, "DY_YinDef": 0.05,
            "DY_FoodStag": 0.25, "DY_Phlegm": 0.05, "DY_QiStag": 0.05, "DY_BloodStasis": 0.05}},
        5: {"desc": "극심한 부패취", "weights": {
            "DY_Cold": 0.00, "DY_Heat": 0.00, "DY_QiDef": 0.00, "DY_YangDef": 0.00, "DY_YinDef": 0.00,
            "DY_FoodStag": 0.05, "DY_Phlegm": 0.00, "DY_QiStag": 0.00, "DY_BloodStasis": 0.00}}
    },
    "dyspepsia_cold_limbs": {  # 수족냉증 - cold limbs (Yang Deficiency marker)
        1: {"desc": "손발 따뜻함", "weights": {
            "DY_Cold": 0.10, "DY_Heat": 0.50, "DY_QiDef": 0.30, "DY_YangDef": 0.05, "DY_YinDef": 0.35,
            "DY_FoodStag": 0.40, "DY_Phlegm": 0.30, "DY_QiStag": 0.35, "DY_BloodStasis": 0.30}},
        2: {"desc": "약간 시림", "weights": {
            "DY_Cold": 0.25, "DY_Heat": 0.30, "DY_QiDef": 0.35, "DY_YangDef": 0.20, "DY_YinDef": 0.35,
            "DY_FoodStag": 0.35, "DY_Phlegm": 0.35, "DY_QiStag": 0.35, "DY_BloodStasis": 0.35}},
        3: {"desc": "손발 차가움", "weights": {
            "DY_Cold": 0.40, "DY_Heat": 0.15, "DY_QiDef": 0.25, "DY_YangDef": 0.40, "DY_YinDef": 0.25,
            "DY_FoodStag": 0.20, "DY_Phlegm": 0.30, "DY_QiStag": 0.25, "DY_BloodStasis": 0.30}},
        4: {"desc": "수족냉증 심함", "weights": {
            "DY_Cold": 0.20, "DY_Heat": 0.05, "DY_QiDef": 0.08, "DY_YangDef": 0.30, "DY_YinDef": 0.05,
            "DY_FoodStag": 0.05, "DY_Phlegm": 0.05, "DY_QiStag": 0.05, "DY_BloodStasis": 0.05}},
        5: {"desc": "극심 수족냉", "weights": {
            "DY_Cold": 0.05, "DY_Heat": 0.00, "DY_QiDef": 0.02, "DY_YangDef": 0.05, "DY_YinDef": 0.00,
            "DY_FoodStag": 0.00, "DY_Phlegm": 0.00, "DY_QiStag": 0.00, "DY_BloodStasis": 0.00}}
    },

    # ---------------------------------------------------------
    # ALLERGIC RHINITIS - FLUID RETENTION (수체형) - Page 23
    # Single unified pattern for rhinitis as per official doc
    # ---------------------------------------------------------
    "rhinitis_fluid_severity": {
        1: {"desc": "증상 없음", "weights": {"R_Fluid": 0.00}},
        2: {"desc": "경미 (Mild)", "weights": {"R_Fluid": 0.25}},
        3: {"desc": "중등도 (Moderate)", "weights": {"R_Fluid": 0.40}},
        4: {"desc": "심함 (Severe)", "weights": {"R_Fluid": 0.25}},
        5: {"desc": "매우 심함 (Very Severe)", "weights": {"R_Fluid": 0.10}}
    }
}

# ==========================================
# FINAL MERGE - ALL DATA (Including PART_5)
# ==========================================
CLINICAL_DATA.update(PART_5)  # Add PART_5 to CLINICAL_DATA

# Helper function to get all descriptions for a variable
def get_all_descs(variable):
    descs = []
    try:
        for level in CLINICAL_DATA[variable]:
            descs.append(CLINICAL_DATA[variable][level]['desc'])
    except:
        return []
    return descs

# Helper function to get all weights for a variable
def get_all_weights(variable):
    weights = []
    try:
        for level in CLINICAL_DATA[variable]:
            weights.append(CLINICAL_DATA[variable][level]['weights'])
    except:
        return []
    return weights