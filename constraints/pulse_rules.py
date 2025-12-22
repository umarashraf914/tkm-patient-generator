"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - 맥진 규칙 (Pulse Diagnosis Rules)
교수님 피드백 기반 맥 조합 규칙
═══════════════════════════════════════════════════════════════════════════════

맥 분류 및 조합 규칙:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

정상맥:
  - 완맥 (緩脈, Moderate Pulse)

부맥류 (浮脈類, Floating Pulses):
  - 부대 (浮大脈) - 부맥 + 대맥
  - 부색 (浮澀脈) - 부맥 + 삽맥
  - 부삭 (浮數脈) - 부맥 + 삭맥 (빠른맥, 맥박수로 대체)
  - 부긴실 (浮緊實脈) - 부맥 + 긴맥 + 실맥
  - 부허 (浮虛脈) - 부맥 + 허맥
  - 홍대 (洪大脈) - 홍맥 + 대맥
  - 홍삭 (洪數脈) - 홍맥 + 삭맥 (빠른맥)

침맥류 (沈脈類, Deep Pulses):
  - 침실 (沈實脈) - 침맥 + 실맥
  - 침긴 (沈緊脈) - 침맥 + 긴맥
  - 침세 (沈細脈) - 침맥 + 세맥

허맥류 (虛脈類, Deficient Pulses):
  - 허대 (虛大脈) - 허맥 + 대맥
  - 미약 (微弱脈) - 미맥 + 약맥
  - 세약 (細弱脈) - 세맥 + 약맥
  - 대활 (大滑脈) - 대맥 + 활맥

실맥류 (實脈類, Excess Pulses):
  - 현긴 (弦緊脈) - 현맥 + 긴맥

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
금기 규칙 (Contraindication Rules):
  1. 부맥류 + 침맥류 = 동시 불가 (浮沈不能同見)
  2. 허맥류 + 실맥류 = 동시 불가 (虛實不能同見)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
질환별 허용 맥 (Disease-Specific Allowed Pulses):
  - 감기: 부대, 부색, 부삭, 부긴실, 부허, 홍대, 홍삭
  - 알레르기비염: 부대, 부색, 부삭, 부긴실, 부허, 홍대, 홍삭
  - 요통: 모든 맥 가능
  - 소화불량: 부허, 침실, 침긴, 허대, 미약, 세활, 현긴, 완맥
═══════════════════════════════════════════════════════════════════════════════
"""

import random


# ═══════════════════════════════════════════════════════════════════════════════
# 맥 정의 (Pulse Definitions)
# ═══════════════════════════════════════════════════════════════════════════════

# 정상맥
NORMAL_PULSE = "완맥"

# 부맥류 (Floating category)
FLOATING_PULSES = ["부대", "부색", "부삭", "부긴실", "부허", "홍대", "홍삭"]

# 침맥류 (Deep category)
DEEP_PULSES = ["침실", "침긴", "침세"]

# 허맥류 (Deficient category)
DEFICIENT_PULSES = ["허대", "미약", "세약", "대활"]

# 실맥류 (Excess category)
EXCESS_PULSES = ["현긴"]

# 모든 복합맥
ALL_COMPOUND_PULSES = [NORMAL_PULSE] + FLOATING_PULSES + DEEP_PULSES + DEFICIENT_PULSES + EXCESS_PULSES


# ═══════════════════════════════════════════════════════════════════════════════
# 질환별 허용 맥 (Disease-Specific Allowed Pulses)
# ═══════════════════════════════════════════════════════════════════════════════

DISEASE_PULSE_MAP = {
    "감기": FLOATING_PULSES,  # 풍한/풍열 - 부맥류만
    "알레르기비염": FLOATING_PULSES,  # 풍한/풍열 - 부맥류만
    "요통": ALL_COMPOUND_PULSES,  # 모든 맥 가능
    "기능성 소화불량": ["부허", "침실", "침긴", "허대", "미약", "세약", "현긴", "완맥"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# 복합맥 → 기본맥 매핑 (Compound to Base Pulse Mapping)
# ═══════════════════════════════════════════════════════════════════════════════

COMPOUND_TO_BASE = {
    # 정상
    "완맥": {"depth": "중맥", "width": "세맥", "strength": "유력", "smooth": "완맥"},
    
    # 부맥류
    "부대": {"depth": "부맥", "width": "대맥", "strength": "유력", "smooth": "완맥"},
    "부색": {"depth": "부맥", "width": "세맥", "strength": "유력", "smooth": "삽맥"},
    "부삭": {"depth": "부맥", "width": "세맥", "strength": "유력", "smooth": "활맥"},  # 빠른맥
    "부긴실": {"depth": "부맥", "width": "대맥", "strength": "강력", "smooth": "삽맥"},
    "부허": {"depth": "부맥", "width": "세맥", "strength": "무력", "smooth": "완맥"},
    "홍대": {"depth": "부맥", "width": "홍맥", "strength": "강력", "smooth": "활맥"},
    "홍삭": {"depth": "부맥", "width": "홍맥", "strength": "강력", "smooth": "활맥"},  # 빠른맥
    
    # 침맥류
    "침실": {"depth": "침맥", "width": "대맥", "strength": "강력", "smooth": "완맥"},
    "침긴": {"depth": "침맥", "width": "세맥", "strength": "강력", "smooth": "삽맥"},
    "침세": {"depth": "침맥", "width": "세맥", "strength": "무력", "smooth": "완맥"},
    
    # 허맥류
    "허대": {"depth": "중맥", "width": "대맥", "strength": "무력", "smooth": "완맥"},
    "미약": {"depth": "침맥", "width": "세맥", "strength": "무력", "smooth": "완맥"},
    "세약": {"depth": "중맥", "width": "세맥", "strength": "무력", "smooth": "완맥"},
    "대활": {"depth": "중맥", "width": "대맥", "strength": "유력", "smooth": "활맥"},
    
    # 실맥류
    "현긴": {"depth": "중맥", "width": "세맥", "strength": "강력", "smooth": "삽맥"},
}


def get_allowed_pulses(disease: str) -> list:
    """
    질환에 따라 허용되는 맥 목록을 반환합니다.
    
    Args:
        disease: 질환명 (감기, 알레르기비염, 요통, 기능성 소화불량)
    
    Returns:
        허용되는 복합맥 목록
    """
    return DISEASE_PULSE_MAP.get(disease, ALL_COMPOUND_PULSES)


def select_random_pulse(disease: str) -> str:
    """
    질환에 맞는 랜덤 맥을 선택합니다.
    
    Args:
        disease: 질환명
    
    Returns:
        선택된 복합맥명
    """
    allowed = get_allowed_pulses(disease)
    return random.choice(allowed)


def get_base_pulse_values(compound_pulse: str) -> dict:
    """
    복합맥에서 기본 맥 속성값을 추출합니다.
    
    Args:
        compound_pulse: 복합맥명 (예: "부대", "침실")
    
    Returns:
        기본 맥 속성 딕셔너리 (depth, width, strength, smooth)
    """
    return COMPOUND_TO_BASE.get(compound_pulse, COMPOUND_TO_BASE["완맥"])


def apply_pulse_rules(session):
    """
    맥진 규칙을 적용합니다.
    - 질환에 맞는 맥을 선택
    - 복합맥에서 기본 맥 속성을 설정
    - 부맥류/침맥류 충돌 방지
    - 허맥류/실맥류 충돌 방지
    
    Args:
        session: Streamlit session_state 객체
    """
    disease = session.get('disease', '감기')
    
    # 질환에 맞는 맥 선택
    compound_pulse = select_random_pulse(disease)
    
    # 복합맥 저장 (출력용)
    session.compound_pulse = compound_pulse
    
    # 기본 맥 속성 설정
    base_values = get_base_pulse_values(compound_pulse)
    session.pulse_depth = base_values["depth"]
    session.pulse_width = base_values["width"]
    session.pulse_strength = base_values["strength"]
    session.pulse_smooth = base_values["smooth"]
    
    # 삭맥/홍삭 → 빠른 맥박수 (90-110)
    if compound_pulse in ["부삭", "홍삭"]:
        session.pulse_rate = random.randint(90, 110)
    
    # 지맥 계열 (느린 맥) - 현재 미사용이지만 확장 가능
    # if compound_pulse in ["지맥계열"]:
    #     session.pulse_rate = random.randint(50, 60)


def validate_pulse_compatibility(pulse1: str, pulse2: str) -> bool:
    """
    두 맥이 함께 나타날 수 있는지 검증합니다.
    
    Rules:
    1. 부맥류 + 침맥류 = 불가
    2. 허맥류 + 실맥류 = 불가
    
    Args:
        pulse1: 첫 번째 맥
        pulse2: 두 번째 맥
    
    Returns:
        True if compatible, False if incompatible
    """
    # 부맥류 + 침맥류 충돌
    if (pulse1 in FLOATING_PULSES and pulse2 in DEEP_PULSES) or \
       (pulse1 in DEEP_PULSES and pulse2 in FLOATING_PULSES):
        return False
    
    # 허맥류 + 실맥류 충돌
    if (pulse1 in DEFICIENT_PULSES and pulse2 in EXCESS_PULSES) or \
       (pulse1 in EXCESS_PULSES and pulse2 in DEFICIENT_PULSES):
        return False
    
    return True


def get_pulse_description(compound_pulse: str) -> str:
    """
    복합맥의 한글 설명을 반환합니다.
    
    Args:
        compound_pulse: 복합맥명
    
    Returns:
        맥의 설명 문자열
    """
    descriptions = {
        "완맥": "완맥(緩脈)",
        "부대": "부대맥(浮大脈)",
        "부색": "부색맥(浮澀脈)",
        "부삭": "부삭맥(浮數脈)",
        "부긴실": "부긴실맥(浮緊實脈)",
        "부허": "부허맥(浮虛脈)",
        "홍대": "홍대맥(洪大脈)",
        "홍삭": "홍삭맥(洪數脈)",
        "침실": "침실맥(沈實脈)",
        "침긴": "침긴맥(沈緊脈)",
        "침세": "침세맥(沈細脈)",
        "허대": "허대맥(虛大脈)",
        "미약": "미약맥(微弱脈)",
        "세약": "세약맥(細弱脈)",
        "대활": "대활맥(大滑脈)",
        "현긴": "현긴맥(弦緊脈)",
    }
    return descriptions.get(compound_pulse, compound_pulse)
