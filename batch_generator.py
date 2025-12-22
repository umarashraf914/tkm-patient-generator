"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - Batch Generation Script
800 환자 케이스 일괄 생성 (질환별 200개씩)
═══════════════════════════════════════════════════════════════════════════════

사용법:
    python batch_generator.py

출력:
    output/
    ├── 감기/
    │   ├── 감기_001.pdf ~ 감기_200.pdf
    │   └── 감기_전체.pdf (통합본)
    ├── 알레르기비염/
    │   ├── 알레르기비염_001.pdf ~ 알레르기비염_200.pdf
    │   └── 알레르기비염_전체.pdf
    ├── 기능성소화불량/
    │   └── ...
    └── 요통/
        └── ...
"""

import os
import sys
import time
import json
import hashlib
import warnings
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict

# Suppress font subsetting warnings (harmless - from fonttools library)
warnings.filterwarnings("ignore", message=".*MERG.*subset.*")
warnings.filterwarnings("ignore", category=UserWarning, module="fontTools")
logging.getLogger("fontTools.subset").setLevel(logging.ERROR)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from fpdf import FPDF

# Import project modules
from config import SESSION_DEFAULTS
from randomizer import randomize_inputs, randomize_from_csv_rules
from constraints import apply_all_constraint_rules
from data_mappings import get_desc
from constants import DISEASE_PATTERNS
from pdf_generator import generate_patient_pdf_korean

# Gemini model name
GEMINI_MODEL = "gemini-2.0-flash"


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DISEASES = ["감기", "알레르기비염", "기능성 소화불량", "요통"]
CASES_PER_DISEASE = 200
OUTPUT_DIR = Path("output")
API_DELAY = 1.5  # Seconds between API calls to avoid rate limiting

# Disease name mapping (display name -> CSV key name)
DISEASE_NAME_MAP = {
    "감기": "감기",
    "알레르기비염": "알레르기비염",
    "기능성 소화불량": "기능성소화불량",  # CSV uses no space
    "요통": "요통",
}

def normalize_disease_name(disease: str) -> str:
    """Normalize disease name to match CSV_PATHS keys."""
    return DISEASE_NAME_MAP.get(disease, disease.replace(" ", ""))


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Session State (simulates Streamlit session_state)
# ═══════════════════════════════════════════════════════════════════════════════

class MockSessionState:
    """Mock Streamlit session_state for batch processing."""
    
    def __init__(self):
        # Initialize with default values
        for key, value in SESSION_DEFAULTS.items():
            setattr(self, key, value)
        
        # Add missing attributes that might not be in SESSION_DEFAULTS
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """Ensure all required attributes exist."""
        # Women's health
        if not hasattr(self, 'mens_regular'):
            self.mens_regular = "규칙적"
        if not hasattr(self, 'mens_cycle'):
            self.mens_cycle = 28
        if not hasattr(self, 'mens_duration'):
            self.mens_duration = 5
        if not hasattr(self, 'mens_pain_score'):
            self.mens_pain_score = 3
        if not hasattr(self, 'mens_color'):
            self.mens_color = "적색"
        
        # Cold symptoms
        if not hasattr(self, 'fever_sev'):
            self.fever_sev = 2
        if not hasattr(self, 'chills_sev'):
            self.chills_sev = 2
        if not hasattr(self, 'snot_sev'):
            self.snot_sev = 2
        if not hasattr(self, 'cough_sev'):
            self.cough_sev = 2
        if not hasattr(self, 'sneeze_sev'):
            self.sneeze_sev = 2
        if not hasattr(self, 'nose_block_sev'):
            self.nose_block_sev = 2
        if not hasattr(self, 'nose_itch_sev'):
            self.nose_itch_sev = 2
        if not hasattr(self, 'pain_sev'):
            self.pain_sev = 3
        
        # Pattern
        if not hasattr(self, 'pattern_idx'):
            self.pattern_idx = 0
        if not hasattr(self, 'pattern_name'):
            self.pattern_name = "N/A"
        
        # Other common fields
        if not hasattr(self, 'cold_symptoms_spec'):
            self.cold_symptoms_spec = []
        if not hasattr(self, 'compound_pulse'):
            self.compound_pulse = "완맥"
    
    def get(self, key, default=None):
        return getattr(self, key, default)
    
    def __getattr__(self, name):
        """Return sensible defaults for missing attributes."""
        # This is called when an attribute doesn't exist
        defaults = {
            'mens_regular': '규칙적',
            'mens_cycle': 28,
            'mens_duration': 5,
            'mens_pain_score': 3,
            'mens_pain': 3,
            'mens_color': '적색',
            'mens_amt': '보통',
            'vision_blackout': False,
            'pattern_idx': 0,
            'pattern_name': 'N/A',
            'compound_pulse': '완맥',
            'episode': '특별한 계기 없이 발생',
            'cold_symptoms_spec': [],
            'additional_symptoms': [],
            'additional_comorbidities': [],
            'aggravating_factors': [],
            'relieving_factors': [],
            'pain_nature': [],
            'dyspepsia_spec': [],
            'cold_chief_type': [],
            'snot_color': '투명',
            'snot_type': '맑음',
            'phlegm_amt': 0,
            'phlegm_color': '없음',
            'cold_onset_specific': 'N/A',
            'sore_throat': False,
            'body_ache_cold': False,
            'body_heaviness_cold': False,
            'headache_cold': False,
            'neck_pain_cold': False,
            'cold_dyspnea': False,
            'cold_sweating_check': False,
            'smell_reduction': 0,
            'alternating_chills_fever': 0,
            'exam_stethoscope': '정상',
            'exam_throat_visual': '정상',
            'exam_tongue_depressor': '정상',
            'exam_rhinoscope_finding': '정상',
            'cold_hands_feet': False,
            'sweat_feeling': '보통',
            # Back pain related
            'morning_stiffness': 0,
            'pain_worse_morning': False,
            'pain_worse_activity': False,
            'pain_worse_rest': False,
            'radiating_pain': False,
            'numbness': 0,
            'weakness_leg': 0,
        }
        if name in defaults:
            return defaults[name]
        # Return 0 for numeric-looking fields, False for bool-looking, empty list for list-looking
        if name.endswith('_sev') or name.endswith('_freq') or name.endswith('_score'):
            return 0
        if name.startswith('is_') or name.endswith('_check'):
            return False
        # Return None for unknown attributes
        return None
    
    def __delattr__(self, name):
        """Handle delattr gracefully - just ignore if attribute doesn't exist."""
        try:
            object.__delattr__(self, name)
        except AttributeError:
            pass  # Ignore if attribute doesn't exist
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __contains__(self, key):
        return hasattr(self, key)
    
    def to_dict(self):
        """Convert to dictionary for hashing/comparison."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class MockStreamlit:
    """Mock Streamlit module for constraint functions."""
    
    def __init__(self):
        self.session_state = MockSessionState()


# ═══════════════════════════════════════════════════════════════════════════════
# Patient Generator
# ═══════════════════════════════════════════════════════════════════════════════

def generate_patient_hash(session: MockSessionState) -> str:
    """Generate a hash to check for duplicate patients."""
    # Key fields that define uniqueness
    key_fields = [
        'age', 'sex', 'disease', 'pattern_name',
        'height', 'weight', 'sbp', 'dbp', 'pulse_rate', 'temp',
        'compound_pulse', 'tongue_color', 'tongue_coat_color'
    ]
    data = {k: session.get(k) for k in key_fields}
    return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def generate_unique_patient(disease: str, existing_hashes: set, max_attempts: int = 50) -> Optional[MockSessionState]:
    """Generate a unique patient for the given disease."""
    
    # Normalize disease name for CSV lookup
    csv_disease_name = normalize_disease_name(disease)
    
    for attempt in range(max_attempts):
        # Create mock streamlit
        st_mock = MockStreamlit()
        session = st_mock.session_state
        
        # Set disease
        session.disease = disease
        
        # Randomize all fields
        randomize_inputs(st_mock)
        
        # Randomize from CSV rules for the disease (use normalized name)
        randomize_from_csv_rules(st_mock, csv_disease_name)
        
        # Apply all constraints
        apply_all_constraint_rules(st_mock)
        
        # Check uniqueness
        patient_hash = generate_patient_hash(session)
        if patient_hash not in existing_hashes:
            existing_hashes.add(patient_hash)
            return session
    
    print(f"  ⚠️ Could not generate unique patient after {max_attempts} attempts")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Gemini API Integration
# ═══════════════════════════════════════════════════════════════════════════════

def setup_gemini():
    """Setup Gemini API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Try to load from .env or secrets
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY"):
                        api_key = line.split("=", 1)[1].strip().strip('"\'')
                        break
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found!")
        print("   Set it as environment variable or create .env file")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)


def generate_scenario_with_gemini(model, session: MockSessionState) -> tuple[str, str]:
    """Generate patient scenario using Gemini API."""
    
    # Build prompt using same logic as patient_generator.py
    fever_desc = get_desc("fever_sev", session.fever_sev) or f"레벨 {session.fever_sev}"
    chills_desc = get_desc("chills_sev", session.chills_sev) or f"레벨 {session.chills_sev}"
    snot_desc = get_desc("snot_sev", session.snot_sev) or f"레벨 {session.snot_sev}"
    cough_desc = get_desc("cough_sev", session.cough_sev) or f"레벨 {session.cough_sev}"
    sneeze_desc = get_desc("rhinitis_sneeze", session.sneeze_sev) or f"레벨 {session.sneeze_sev}"
    nose_block_desc = get_desc("rhinitis_block", session.nose_block_sev) or f"레벨 {session.nose_block_sev}"
    nose_itch_desc = get_desc("rhinitis_itch", session.nose_itch_sev) or f"레벨 {session.nose_itch_sev}"
    rhinitis_snot_desc = get_desc("rhinitis_snot_sev", session.snot_sev) or f"레벨 {session.snot_sev}"
    
    # Calculate BMI
    bmi_str = "N/A"
    if session.get("height", 0) > 0:
        bmi = session.weight / ((session.height / 100) ** 2)
        bmi_str = f"{bmi:.1f}"
    
    # Build pattern info
    selected_pattern = "N/A"
    disease_key = None
    if "감기" in session.disease:
        disease_key = "감기"
    elif "비염" in session.disease:
        disease_key = "알레르기비염"
    elif "요통" in session.disease:
        disease_key = "요통"
    elif "소화불량" in session.disease:
        disease_key = "기능성소화불량"
    
    if disease_key and disease_key in DISEASE_PATTERNS:
        patterns = DISEASE_PATTERNS[disease_key]["patterns"]
        idx = session.get("pattern_idx", 0)
        if 0 <= idx < len(patterns):
            p = patterns[idx]
            # For 알레르기비염, prescription name IS the pattern name
            if disease_key == "알레르기비염":
                selected_pattern = p['name']
            else:
                selected_pattern = f"{p['name']} → {', '.join(p['prescriptions'])}"
    
    # Store pattern name for PDF
    session.pattern_name = selected_pattern
    
    system_prompt = _build_batch_prompt(session, selected_pattern,
                                        fever_desc, chills_desc, snot_desc, cough_desc,
                                        sneeze_desc, nose_block_desc, nose_itch_desc, rhinitis_snot_desc,
                                        bmi_str)
    
    # Call Gemini
    try:
        response = model.generate_content(system_prompt, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        
        summary = data.get('요약', '환자 시나리오')
        scenario = data.get('환자시나리오', data.get('초진기록', response.text))
        
        return summary, scenario
        
    except Exception as e:
        print(f"  ❌ Gemini API error: {e}")
        return None, None


def _get_menstrual_info(session):
    """폐경 여부에 따라 여성력 정보 반환"""
    if session.sex != "여":
        return "해당없음 (남성)"
    
    if session.get('mens_regular', '') == "폐경":
        return "폐경"
    else:
        return f"생리주기 {session.get('mens_cycle', 'N/A')}일, 규칙성 {session.get('mens_regular', 'N/A')}, 기간 {session.get('mens_duration', 'N/A')}일, 생리통 {session.get('mens_pain_score', 0)}/10"


def _build_batch_prompt(session, selected_pattern,
                        fever_desc, chills_desc, snot_desc, cough_desc,
                        sneeze_desc, nose_block_desc, nose_itch_desc, rhinitis_snot_desc,
                        bmi_str="N/A"):
    """Build the LLM prompt for batch patient generation (same as patient_generator.py)."""
    
    return f"""
    당신은 한의 임상 가상환자 시나리오 생성 전문가입니다.
    
    ## 역할
    한의사의 관점에서 환자 정보를 진료기록부 형식으로 정리하세요.
    ❌ 환자 시점 (예: "저는 열이 나고...")이 아닌
    ✅ 의사 시점 (예: "상기 환자는 발열을 호소하며...")으로 작성하세요.
    
    ⚠️ 중요: 변증(辨證), 치법(治法), 처방(處方)은 절대 생성하지 마세요!
    ⚠️ 중요: 모든 출력은 100% 한국어로만 작성하세요! 영어 금지!
    
    ## 환자 정보 (Patient Data)
    
    ### 1. 인구학적정보 및 활력징후
    - 나이/성별: {session.age}세 {session.sex}
    - 직업: {session.job}
    - 신장/체중/BMI: {session.height}cm / {session.weight}kg / BMI {bmi_str}
    - 발현시점: {session.onset}
    - 경과: {session.course}
    - 발병 에피소드: {session.get('episode', '특별한 계기 없이 발생')}
    - 활력징후: BP {session.sbp}/{session.dbp} mmHg, 맥박 {session.pulse_rate}회/분, 체온 {session.temp}°C
    
    ### 2. 병력 및 생활습관
    - 현병력: {session.history_conditions}
    - 약물력: {session.meds_specific}
    - 가족력: {session.family_hx}
    - 음주: {session.social_alcohol_freq}
    - 흡연: {session.social_smoke_daily}개피/일
    - 여성력: {_get_menstrual_info(session)}
    
    ### 3. 배설 및 식사
    - 식사횟수: {session.diet_freq}회/일, {session.diet_regular}
    - 대변: {session.stool_freq}, {session.stool_color}, {session.stool_form}
    - 소변: {session.urine_color}, 야간 {session.urine_freq_night}회
    
    ### 4. 수면, 땀, 한열
    - 수면: {session.sleep_hours}시간, {session.sleep_depth}, 기상시 {session.sleep_waking_state}
    - 땀: {session.sweat_amt}, {session.sweat_area}
    - 한열경향: {session.cold_heat_pref}
    
    ### 5. 맥진 및 설진
    - 맥상: {session.get('compound_pulse', '완맥')}
    - 설질: {session.tongue_color}, {session.tongue_size}
    - 설태: {session.tongue_coat_color}, {session.tongue_coat_thick}
    - 면색: {session.face_color}
    
    ### 6. 주소증
    - 질환명: {session.disease}
    
    **감기 증상:** 발열 {fever_desc}, 오한 {chills_desc}, 콧물 {snot_desc}, 기침 {cough_desc}
    **비염 증상:** 재채기 {sneeze_desc}, 코막힘 {nose_block_desc}, 코가려움 {nose_itch_desc}
    **요통 증상:** 통증강도 {session.pain_sev}/10, 통증양상 {session.get('pain_nature', [])}
    **소화불량 증상:** 복만/복통 {session.pain_sev}/5, 증상 {session.get('dyspepsia_spec', [])}
    
    ## 출력 형식 (JSON)
    {{
      "요약": "환자 요약 (예: 45세 남성, 3일전부터 오한, 발열 호소)",
      "환자시나리오": "【환자정보】...【주소증】...【발병 에피소드】...【현병력】...【과거력】...【가족력】...【사회력】...【계통적 문진】...【신체검진 소견】...【설진 소견】...【맥진 소견】..."
    }}
    """


# ═══════════════════════════════════════════════════════════════════════════════
# PDF Generation
# ═══════════════════════════════════════════════════════════════════════════════

def create_patient_pdf(session: MockSessionState, summary: str, scenario: str, output_path: Path) -> bool:
    """Create PDF for a single patient."""
    
    patient_info = {
        'disease': session.disease,
        'pattern': session.get('pattern_name', 'N/A'),
        'age': session.age,
        'sex': session.sex,
        'height': session.height,
        'weight': session.weight,
        'sbp': session.sbp,
        'dbp': session.dbp,
        'pulse_rate': session.pulse_rate,
        'temp': session.temp,
    }
    
    try:
        pdf_bytes = generate_patient_pdf_korean(summary, scenario, patient_info)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return True
    except Exception as e:
        print(f"  ❌ PDF creation error: {e}")
        return False


def merge_pdfs(pdf_files: list, output_path: Path):
    """Merge multiple PDFs into one."""
    try:
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        for pdf_file in pdf_files:
            if pdf_file.exists():
                merger.append(str(pdf_file))
        
        merger.write(str(output_path))
        merger.close()
        print(f"  ✅ Merged PDF: {output_path}")
        
    except ImportError:
        print("  ⚠️ PyPDF2 not installed. Skipping merge.")
        print("     Install with: pip install PyPDF2")
    except Exception as e:
        print(f"  ❌ Merge error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main Batch Generation
# ═══════════════════════════════════════════════════════════════════════════════

def batch_generate(diseases: list = None, cases_per_disease: int = None, start_from: int = 1):
    """
    Main batch generation function.
    
    Args:
        diseases: List of diseases to generate (default: all 4)
        cases_per_disease: Number of cases per disease (default: 200)
        start_from: Starting case number (for resuming)
    """
    diseases = diseases or DISEASES
    cases_per_disease = cases_per_disease or CASES_PER_DISEASE
    
    print("═" * 60)
    print("  TKM Patient Generator - Batch Generation")
    print("═" * 60)
    print(f"  질환: {', '.join(diseases)}")
    print(f"  질환당 케이스: {cases_per_disease}")
    print(f"  총 케이스: {len(diseases) * cases_per_disease}")
    print("═" * 60)
    
    # Setup Gemini
    print("\n🔧 Setting up Gemini API...")
    model = setup_gemini()
    print("  ✅ Gemini API ready")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Track statistics
    total_generated = 0
    total_failed = 0
    start_time = datetime.now()
    
    for disease in diseases:
        print(f"\n{'─' * 60}")
        print(f"📋 Generating: {disease}")
        print(f"{'─' * 60}")
        
        # Create disease folder
        disease_folder = OUTPUT_DIR / disease.replace(" ", "")
        disease_folder.mkdir(exist_ok=True)
        
        # Track unique patients
        existing_hashes = set()
        pdf_files = []
        
        for case_num in range(start_from, cases_per_disease + 1):
            print(f"\n  [{case_num}/{cases_per_disease}] Generating patient...", end=" ")
            
            # Generate unique patient
            session = generate_unique_patient(disease, existing_hashes)
            if not session:
                total_failed += 1
                continue
            
            print(f"✓ ", end="")
            
            # Generate scenario with Gemini
            print("Calling Gemini...", end=" ")
            summary, scenario = generate_scenario_with_gemini(model, session)
            
            if not scenario:
                total_failed += 1
                print("❌")
                continue
            
            print(f"✓ ", end="")
            
            # Create PDF
            pdf_filename = f"{disease.replace(' ', '')}_{case_num:03d}.pdf"
            pdf_path = disease_folder / pdf_filename
            
            print("Creating PDF...", end=" ")
            if create_patient_pdf(session, summary, scenario, pdf_path):
                pdf_files.append(pdf_path)
                total_generated += 1
                print(f"✓ {pdf_filename}")
            else:
                total_failed += 1
                print("❌")
            
            # Rate limiting
            time.sleep(API_DELAY)
        
        # Merge all PDFs for this disease
        if pdf_files:
            print(f"\n  📚 Merging {len(pdf_files)} PDFs...")
            merged_path = disease_folder / f"{disease.replace(' ', '')}_전체.pdf"
            merge_pdfs(pdf_files, merged_path)
    
    # Final statistics
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "═" * 60)
    print("  Generation Complete!")
    print("═" * 60)
    print(f"  ✅ Generated: {total_generated}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  ⏱️  Duration: {duration}")
    print(f"  📁 Output: {OUTPUT_DIR.absolute()}")
    print("═" * 60)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch generate TKM patient cases")
    parser.add_argument("--disease", "-d", type=str, help="Single disease to generate")
    parser.add_argument("--count", "-n", type=int, default=200, help="Cases per disease (default: 200)")
    parser.add_argument("--start", "-s", type=int, default=1, help="Starting case number (for resuming)")
    parser.add_argument("--test", "-t", action="store_true", help="Test mode: generate 2 cases per disease")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 TEST MODE: Generating 2 cases per disease")
        batch_generate(cases_per_disease=2)
    elif args.disease:
        # Single disease
        if args.disease not in DISEASES:
            print(f"❌ Unknown disease: {args.disease}")
            print(f"   Available: {', '.join(DISEASES)}")
            sys.exit(1)
        batch_generate(diseases=[args.disease], cases_per_disease=args.count, start_from=args.start)
    else:
        # All diseases
        batch_generate(cases_per_disease=args.count, start_from=args.start)
