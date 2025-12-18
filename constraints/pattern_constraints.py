"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - Disease Pattern-Specific Constraints
Based on Clinical Guidelines Pages 15-16, 23
═══════════════════════════════════════════════════════════════════════════════

This module contains pattern-specific constraints for each disease type:
- 감기 (Cold) - Wind-Cold, Wind-Heat patterns
- 비염 (Rhinitis) - Various water retention patterns
- 요통 (Back Pain) - 한열허실 based patterns
- 소화불량 (Dyspepsia) - Spleen-stomach patterns
"""

import random


# ═══════════════════════════════════════════════════════════════════════════════
# COLD (감기) CONSTRAINTS - Page 15
# ═══════════════════════════════════════════════════════════════════════════════

def apply_cold_constraints(session):
    """
    Apply cold (감기) pattern-specific constraints (Page 15).
    
    Patterns:
    - 0: Wind-Cold (풍한형) - 惡寒重, 無汗
    - 1: Wind-Heat (풍열형) - 身熱, 有汗
    - 2: Wind-Dryness (풍조형) - Dry symptoms
    """
    if "Cold" not in session.disease:
        return
    
    current_pattern = session.pattern_idx
    
    if current_pattern == 0:
        _apply_wind_cold_pattern(session)
    elif current_pattern == 1:
        _apply_wind_heat_pattern(session)
    elif current_pattern == 2:
        _apply_wind_dryness_pattern(session)


def _apply_wind_cold_pattern(session):
    """
    Apply Wind-Cold (풍한) pattern constraints.
    
    Page 15: 오한이 심하고 땀이 없다 (惡寒重, 無汗)
    - Chills dominant over fever
    - No sweating
    - White/clear phlegm
    - Prefers warm drinks
    - Joint pain common (骨節疼痛)
    """
    # Chills should be more severe than fever
    if session.fever_sev > session.chills_sev:
        session.chills_sev, session.fever_sev = session.fever_sev, session.chills_sev
    
    # Tongue and phlegm characteristics
    session.tongue_coat_color = "White"
    session.phlegm_color = "White/Clear (희박/맑음)"
    
    # No sweating (無汗)
    session.sweating = False
    session.sweat_amt = "None (무한)"
    
    # Joint pain correlation (骨節疼痛)
    if random.random() < 0.6:
        if "Joint Pain (관절통)" not in session.cold_symptoms_spec:
            session.cold_symptoms_spec.append("Joint Pain (관절통)")
    
    # Prefers warm/hot drinks (avoids cold)
    if session.drink_temp == "Icy":
        session.drink_temp = random.choice(["Warm", "Hot"])


def _apply_wind_heat_pattern(session):
    """
    Apply Wind-Heat (풍열) pattern constraints.
    
    Page 15: 身熱 (body heat/fever dominant)
    - Fever dominant over chills
    - Sweating present
    - Yellow/sticky phlegm
    - May prefer cool drinks
    """
    # Fever should be more severe than chills
    if session.chills_sev > session.fever_sev:
        session.chills_sev, session.fever_sev = session.fever_sev, session.chills_sev
    
    # Tongue and phlegm characteristics
    session.tongue_coat_color = random.choice(["White", "Yellow"])
    session.phlegm_color = "Yellow/Sticky (황담/끈적)"
    
    # Sweating present (有汗)
    session.sweating = True
    if session.sweat_amt == "None (무한)":
        session.sweat_amt = "Normal (보통)"
    
    # May prefer cool drinks
    if session.drink_temp == "Hot":
        session.drink_temp = random.choice(["Warm", "Icy"])


def _apply_wind_dryness_pattern(session):
    """
    Apply Wind-Dryness (풍조/온燥) pattern constraints.
    
    Page 15: Dry cough, little phlegm, dry/painful throat
    - Mild or no fever/chills
    - Dry throat and lips
    - Dry skin
    - Increased mouth dryness
    """
    # Mild fever/chills
    session.fever_sev = random.randint(1, 2)
    session.chills_sev = random.randint(1, 2)
    
    # Little phlegm, dry symptoms
    session.phlegm_amt = random.randint(0, 1)
    session.throat_dry = True
    session.lip_dry = True
    
    # Dry skin
    if session.skin_dry == "Normal (정상)":
        session.skin_dry = random.choice(["Dry (건조)", "Scaly (각질)"])
    
    # Increased mouth dryness
    session.mouth_dry = random.randint(2, 4)


# ═══════════════════════════════════════════════════════════════════════════════
# RHINITIS (비염) CONSTRAINTS - Page 23
# ═══════════════════════════════════════════════════════════════════════════════

def apply_rhinitis_constraints(session):
    """
    Apply rhinitis (비염) pattern-specific constraints.
    
    Patterns (수체형 variations):
    - 0: Yuebi (월비가반하탕) - Heat/sticky
    - 1: Shegan (사간마황탕) - Cold/asthma
    - 2: Minor Blue Dragon (소청룡탕) - Cold/watery
    - 3: Ling-Gan (영감강미신하인탕) - Cold/deficiency
    - 4: Mahuang-Fuzi (마황부자세신탕) - Kidney Yang deficiency
    """
    if "Rhinitis" not in session.disease:
        return
    
    pattern_handlers = {
        0: _apply_yuebi_pattern,
        1: _apply_shegan_pattern,
        2: _apply_minor_blue_dragon_pattern,
        3: _apply_linggan_pattern,
        4: _apply_mahuang_fuzi_pattern
    }
    
    handler = pattern_handlers.get(session.pattern_idx)
    if handler:
        handler(session)


def _apply_yuebi_pattern(session):
    """Yuebi (월비가반하탕) - Heat/sticky pattern."""
    session.snot_type = "Yellow/Thick (누렇고 찐득)"
    if session.tongue_coat_color == "White":
        session.tongue_coat_color = "Yellow"


def _apply_shegan_pattern(session):
    """Shegan (사간마황탕) - Cold/asthma pattern."""
    session.snot_type = random.choice(["Clear/Watery (맑음/물)", "White/Sticky (희고 끈적)"])


def _apply_minor_blue_dragon_pattern(session):
    """
    Minor Blue Dragon (소청룡탕) - Cold/watery pattern.
    Key sign: 맑은 콧물이 줄줄 (profuse clear discharge)
    """
    session.snot_type = "Clear/Watery (맑음/물)"
    session.tongue_coat_color = "White"
    if session.cold_heat_pref == "Heat Sens":
        session.cold_heat_pref = random.choice(["Cold Sens", "Balanced"])


def _apply_linggan_pattern(session):
    """Ling-Gan (영감강미신하인탕) - Cold/deficiency pattern."""
    session.snot_type = "Clear/Watery (맑음/물)"
    session.cold_heat_pref = "Cold Sens"
    session.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])


def _apply_mahuang_fuzi_pattern(session):
    """
    Mahuang-Fuzi (마황부자세신탕) - Kidney Yang deficiency pattern.
    신양허: 수족냉, 피로
    """
    session.cold_hands_feet = True
    session.cold_heat_pref = "Cold Sens"
    session.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])


# ═══════════════════════════════════════════════════════════════════════════════
# BACK PAIN (요통) CONSTRAINTS - Pages 15-16
# ═══════════════════════════════════════════════════════════════════════════════

def apply_back_pain_constraints(session):
    """
    Apply back pain (요통) pattern-specific constraints (Pages 15-16).
    
    Patterns (한열허실 based):
    - 0: 신허 (Kidney Deficiency)
    - 1: 담음 (Phlegm)
    - 2: 식적 (Food Stagnation)
    - 3: 기 (Qi)
    - 4: 좌섬 (Sprain)
    - 5: 어혈 (Blood Stasis)
    - 6: 풍 (Wind)
    - 7: 한 (Cold)
    - 8: 습 (Dampness)
    - 9: 습열 (Damp-Heat)
    """
    if "Back Pain" not in session.disease:
        return
    
    # Ensure pain severity is capped at 7 per KTAS rules
    if session.pain_sev >= 7:
        session.pain_sev = 7
    
    # Ensure back pain is present for back pain diagnosis
    if session.pain_back[0] < 3:
        session.pain_back = [random.randint(3, 5), session.pain_sev]
        session.pain_back_f = session.pain_back[0]
        session.pain_back_i = session.pain_back[1]
    
    pain_nature_list = session.get("pain_nature", [])
    
    # Pattern-specific handler mapping
    pattern_handlers = {
        0: _apply_kidney_deficiency_pattern,
        1: _apply_phlegm_pattern,
        2: _apply_food_stagnation_pattern,
        3: _apply_qi_pattern,
        4: _apply_sprain_pattern,
        5: _apply_blood_stasis_pattern,
        6: _apply_wind_pattern,
        7: _apply_cold_pattern,
        8: _apply_dampness_pattern,
        9: _apply_damp_heat_pattern
    }
    
    handler = pattern_handlers.get(session.pattern_idx)
    if handler:
        handler(session, pain_nature_list)


def _apply_kidney_deficiency_pattern(session, pain_nature_list):
    """
    신허 (Kidney Deficiency) pattern.
    Page 15: Continuous ache, hard to move, sexual overexertion cause
    舌大 (large tongue), 맥세 (thin pulse)
    """
    session.back_pain_cause = "Kidney Deficiency (신허)"
    session.tongue_size = "Enlarged (대)"
    session.pulse_width = "Thin"
    session.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])


def _apply_phlegm_pattern(session, pain_nature_list):
    """
    담음 (Phlegm) pattern.
    Page 15: Pain radiates up/down along meridians
    맥滑 또는 伏 (slippery or hidden pulse)
    """
    session.back_pain_cause = "No Specific Cause (발병 요인 없음)"
    if "Moving (유주통) - Phlegm" not in pain_nature_list:
        session.pain_nature.append("Moving (유주통) - Phlegm")
    session.pulse_smooth = "Smooth (활)"


def _apply_food_stagnation_pattern(session, pain_nature_list):
    """
    식적 (Food Stagnation) pattern.
    Page 15: Caused by overeating/alcohol
    Difficulty bending/straightening, 맥滑 (slippery pulse)
    """
    session.back_pain_cause = "Overeating/Alcohol (음주/과식)"
    session.pulse_smooth = "Smooth (활)"
    session.appetite = random.choice(["None", "Low"])
    session.bloating = random.randint(2, 4)


def _apply_qi_pattern(session, pain_nature_list):
    """
    기 (Qi) pattern.
    Page 15: Frustration cause, worse with standing/walking
    맥沈伏 또는 弦 (sinking-hidden or wiry pulse)
    """
    session.back_pain_cause = "Frustration/Stress (울체)"
    if "Worse Standing (오래 서있으면 악화) - Qi" not in pain_nature_list:
        session.pain_nature.append("Worse Standing (오래 서있으면 악화) - Qi")
    session.pulse_depth = "Sinking"
    session.pulse_tension = random.choice(["Tense (긴)", "Normal"])


def _apply_sprain_pattern(session, pain_nature_list):
    """
    좌섬 (Sprain) pattern.
    Page 15: Lifting heavy things, injury - sudden onset
    맥沈伏 實 (sinking-hidden, replete pulse)
    """
    session.back_pain_cause = "Injury/Sprain (좌섬/외상)"
    session.onset = random.choice(["1 day ago", "2-3 days ago"])
    session.pulse_depth = "Sinking"
    session.pulse_strength = "Strong"


def _apply_blood_stasis_pattern(session, pain_nature_list):
    """
    어혈 (Blood Stasis) pattern.
    Page 15: Fall, hit, or chronic injury
    Less pain during day, worse at night; stabbing pain
    맥澀 (choppy pulse)
    """
    session.back_pain_cause = "Trauma/Fall (외상/낙상)"
    session.back_pain_timing = "Worse at Night (야간 악화)"
    
    if "Stabbing (자통) - Blood Stasis" not in pain_nature_list:
        session.pain_nature.append("Stabbing (자통) - Blood Stasis")
    if "Worse at Night (야간통) - Blood Stasis" not in pain_nature_list:
        session.pain_nature.append("Worse at Night (야간통) - Blood Stasis")
    
    session.pulse_smooth = "Rough (삽)"
    session.tongue_color = random.choice(["Dark Red", "Pale Red"])


def _apply_wind_pattern(session, pain_nature_list):
    """
    풍 (Wind) pattern.
    Page 16: Pain moves around, may radiate to legs
    맥浮 (floating pulse)
    """
    session.back_pain_cause = "No Specific Cause (발병 요인 없음)"
    if "Moving (유주통) - Phlegm" not in pain_nature_list:
        session.pain_nature.append("Moving (유주통) - Phlegm")
    session.back_radiation = True
    session.pulse_depth = "Floating"


def _apply_cold_pattern(session, pain_nature_list):
    """
    한 (Cold) pattern.
    Page 16: Hard to turn body, warmth helps
    맥沈緊 (sinking-tight pulse)
    """
    session.back_pain_cause = "No Specific Cause (발병 요인 없음)"
    
    if "Fixed/Cold (한통) - Cold" not in pain_nature_list:
        session.pain_nature.append("Fixed/Cold (한통) - Cold")
    if "Better w/ Warmth (득온즉감) - Cold" not in pain_nature_list:
        session.pain_nature.append("Better w/ Warmth (득온즉감) - Cold")
    
    session.pulse_depth = "Sinking"
    session.pulse_tension = "Tense (긴)"
    session.cold_heat_pref = "Cold Sens"
    session.cold_hands_feet = True


def _apply_dampness_pattern(session, pain_nature_list):
    """
    습 (Dampness) pattern.
    Page 16: Damp environment, heavy like a stone, cold feeling
    맥緩 (slow pulse)
    """
    session.back_pain_cause = "Damp Environment (습한 환경)"
    
    if "Heavy/Stone-like (중통) - Dampness" not in pain_nature_list:
        session.pain_nature.append("Heavy/Stone-like (중통) - Dampness")
    
    session.cold_heat_pref = "Cold Sens"
    session.pulse_tension = "Soft (유)"
    session.tongue_coat_thick = random.choice(["Thick", "Greasy"])


def _apply_damp_heat_pattern(session, pain_nature_list):
    """
    습열 (Damp-Heat) pattern.
    Page 16: Greasy food, sitting long worsens it
    맥緩 또는 沈 (slow or sinking pulse)
    """
    session.back_pain_cause = "Greasy Food/Sedentary (기름진 음식/오래 앉음)"
    session.pulse_depth = random.choice(["Middle", "Sinking"])
    session.pulse_tension = "Soft (유)"
    session.tongue_coat_color = "Yellow"
    session.tongue_coat_thick = "Greasy"


# ═══════════════════════════════════════════════════════════════════════════════
# DYSPEPSIA (소화불량) CONSTRAINTS - Page 16
# ═══════════════════════════════════════════════════════════════════════════════

def apply_dyspepsia_constraints(session):
    """
    Apply dyspepsia (소화불량) pattern-specific constraints (Page 16).
    
    Patterns:
    - 0: 비위허약/위허기허 (Spleen-Stomach Weakness)
    - 1: 비위기허 (Spleen-Stomach Qi Deficiency)
    - 2: 간위불화 (Liver-Stomach Disharmony)
    - 3: 비위습열 (Spleen-Stomach Damp-Heat)
    - 4: 한열착잡 (Cold-Heat Complex)
    - 5: 음식정체/식적 (Food Stagnation)
    """
    if "Dyspepsia" not in session.disease:
        return
    
    dyspepsia_specs = session.get("dyspepsia_spec", [])
    
    pattern_handlers = {
        0: _apply_spleen_stomach_weakness_pattern,
        1: _apply_spleen_stomach_qi_def_pattern,
        2: _apply_liver_stomach_disharmony_pattern,
        3: _apply_spleen_stomach_damp_heat_pattern,
        4: _apply_cold_heat_complex_pattern,
        5: _apply_dyspepsia_food_stagnation_pattern
    }
    
    handler = pattern_handlers.get(session.pattern_idx)
    if handler:
        handler(session, dyspepsia_specs)


def _apply_spleen_stomach_weakness_pattern(session, dyspepsia_specs):
    """
    비위허약/위허기허 (Spleen-Stomach Weakness) pattern.
    Page 16: No appetite, eats little, bloating after eating
    舌苔淡白 薄潤, 脈細弱
    """
    session.appetite = random.choice(["None", "Low"])
    session.diet_amt = "Little (적음)"
    session.bloating = random.randint(2, 4)
    session.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
    session.limb_weakness = True
    
    # Tongue: Pale with thin white coat
    session.tongue_color = "Pale"
    session.tongue_coat_color = "White"
    session.tongue_coat_thick = "Thin"
    
    # Pulse: Thin-weak
    session.pulse_width = "Thin"
    session.pulse_strength = "Weak"


def _apply_spleen_stomach_qi_def_pattern(session, dyspepsia_specs):
    """
    비위기허 (Spleen-Stomach Qi Deficiency) pattern.
    Page 16: Stomach pain, sighing, easily tired
    舌淡苔白, 脈細弱
    """
    session.epigastric_pain = random.randint(2, 4)
    session.sighing_freq = random.randint(2, 4)
    session.fatigue_level = random.choice(["Moderate (중등도)", "Severe (심함)"])
    session.mental_clarity = "Foggy (흐릿)"
    session.emot_anger = random.randint(3, 5)
    
    # Tongue: Pale white
    session.tongue_color = "Pale"
    session.tongue_coat_color = "White"
    
    # Pulse: Thin-weak
    session.pulse_width = "Thin"
    session.pulse_strength = "Weak"


def _apply_liver_stomach_disharmony_pattern(session, dyspepsia_specs):
    """
    간위불화 (Liver-Stomach Disharmony) pattern.
    Page 16: Acid reflux, frequent belching, easily angered
    舌淡紅 苔薄白, 脈弦
    """
    session.acid_reflux = True
    session.belching = random.randint(3, 5)
    
    if "Acid Reflux (신물) - Liver/Food" not in dyspepsia_specs:
        session.dyspepsia_spec.append("Acid Reflux (신물) - Liver/Food")
    
    session.emot_anger = random.randint(3, 5)
    session.bitter_taste = True
    session.mouth_dry = random.randint(2, 4)
    
    if "Bitter Taste (구고) - Heat" not in dyspepsia_specs:
        session.dyspepsia_spec.append("Bitter Taste (구고) - Heat")
    
    # Tongue: Red with thin white coat
    session.tongue_color = "Pale Red"
    session.tongue_coat_color = "White"
    session.tongue_coat_thick = "Thin"
    
    # Pulse: Wiry
    session.pulse_tension = "Tense (긴)"


def _apply_spleen_stomach_damp_heat_pattern(session, dyspepsia_specs):
    """
    비위습열 (Spleen-Stomach Damp-Heat) pattern.
    Page 16: Acid reflux, nausea, vomiting, body heat
    舌紅 苔黃膩, 脈滑數
    """
    session.acid_reflux = True
    session.nausea = random.randint(3, 5)
    session.nausea_sev = random.randint(3, 5)
    
    if "Nausea/Vomiting (구역/구토) - Damp-Heat" not in dyspepsia_specs:
        session.dyspepsia_spec.append("Nausea/Vomiting (구역/구토) - Damp-Heat")
    
    session.cold_heat_body = "Hot (열)"
    session.bitter_taste = True
    session.mouth_dry = random.randint(2, 4)
    
    # Tongue: Red with yellow greasy coat
    session.tongue_color = "Red"
    session.tongue_coat_color = "Yellow"
    session.tongue_coat_thick = "Greasy"
    
    # Pulse: Slippery-rapid
    session.pulse_smooth = "Smooth (활)"


def _apply_cold_heat_complex_pattern(session, dyspepsia_specs):
    """
    한열착잡 (Cold-Heat Complex) pattern.
    Page 16: Acid reflux, nausea, cold limbs
    舌淡 苔黃, 脈弦
    """
    session.acid_reflux = True
    session.epigastric_pain = random.randint(2, 4)
    session.cold_limbs_dyspepsia = True
    session.cold_hands_feet = True
    
    if "Cold Limbs (수족냉증) - Deficiency" not in dyspepsia_specs:
        session.dyspepsia_spec.append("Cold Limbs (수족냉증) - Deficiency")
    
    # Tongue: Pale with yellow coat
    session.tongue_color = "Pale"
    session.tongue_coat_color = "Yellow"
    
    # Pulse: Wiry
    session.pulse_tension = "Tense (긴)"


def _apply_dyspepsia_food_stagnation_pattern(session, dyspepsia_specs):
    """
    음식정체/식적 (Food Stagnation) pattern.
    Page 16-17: Acid reflux with foul smell, no appetite
    苔厚膩, 脈滑
    """
    session.acid_reflux = True
    session.foul_belch = True
    session.belching = random.randint(3, 5)
    session.belching_smell = "Foul (부패취)"
    
    if "Foul Belching (부패취) - Food Stag" not in dyspepsia_specs:
        session.dyspepsia_spec.append("Foul Belching (부패취) - Food Stag")
    
    session.nausea = random.randint(2, 4)
    session.appetite = "None"
    
    # Tongue: Thick greasy coat
    session.tongue_coat_thick = "Greasy"
    
    # Pulse: Slippery
    session.pulse_smooth = "Smooth (활)"
