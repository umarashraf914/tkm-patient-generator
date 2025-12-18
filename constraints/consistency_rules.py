"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - General Consistency Rules
Clinical Logic Constraints for Realistic Patient Data
═══════════════════════════════════════════════════════════════════════════════

This module ensures clinical consistency across various data points:
- Fever-Temperature consistency
- Women's health constraints
- Mental/Appetite constraints
- BMI/Body composition constraints
- Sleep constraints
- Excretion constraints
- Pulse-Tongue consistency
"""

import random


def apply_consistency_rules(session):
    """
    Apply general clinical consistency rules.
    
    Args:
        session: Streamlit session_state object
    """
    _apply_fever_temperature_consistency(session)
    _apply_womens_health_constraints(session)
    _apply_snot_rhinitis_constraints(session)
    _apply_mental_appetite_constraints(session)
    _apply_bmi_body_constraints(session)
    _apply_sleep_constraints(session)
    _apply_excretion_constraints(session)
    _apply_pulse_tongue_constraints(session)


def _apply_fever_temperature_consistency(session):
    """
    Ensure fever severity matches actual temperature reading.
    
    Rules:
    - High Fever (level 4-5) must have elevated temp (≥38.0°C)
    - Low/No Fever (level 1-2) should have normal temperature (<38.5°C)
    - Medium fever (level 3) = mild temp elevation (37.4-38.4°C)
    """
    if session.fever_sev >= 4 and session.temp < 38.0:
        session.temp = round(random.uniform(38.0, 39.5), 1)
    
    if session.fever_sev <= 2 and session.temp >= 38.5:
        session.temp = round(random.uniform(36.0, 37.3), 1)
    
    if session.fever_sev == 3 and (session.temp < 37.4 or session.temp >= 38.5):
        session.temp = round(random.uniform(37.4, 38.4), 1)


def _apply_womens_health_constraints(session):
    """
    Apply women's health constraints based on age and sex.
    
    Rules:
    - Women's health only applies to females aged 14-50
    - Males have no menstrual data
    - Women >50 marked as menopause
    """
    if session.sex == "Female (여)":
        if session.age < 14 or session.age > 50:
            session.mens_regular = "Menopause" if session.age > 50 else "N/A"
            session.mens_pain_score = 0
            session.mens_duration = 0
        else:
            if session.mens_regular == "Menopause":
                session.mens_regular = random.choice(["Regular", "Irregular"])
    else:
        # Male patients - reset all women's health variables
        session.mens_pain_score = 0
        session.mens_duration = 0


def _apply_snot_rhinitis_constraints(session):
    """
    Apply snot/rhinitis consistency rules.
    
    Rules:
    - No snot (severity ≤1) means clear/none type
    """
    if session.snot_sev <= 1:
        session.snot_type = "Clear/Watery (맑음/물)"


def _apply_mental_appetite_constraints(session):
    """
    Apply mental state and appetite consistency rules.
    
    Rules:
    - No appetite + High motivation is impossible
    - Severe fatigue should lower motivation
    - Poor memory + High stress coping is inconsistent
    """
    if session.appetite == "None" and session.motivation == "High (높음)":
        session.motivation = "Low (낮음)"
    
    if session.fatigue_level == "Severe (심함)" and session.motivation == "High (높음)":
        session.motivation = random.choice(["Normal (보통)", "Low (낮음)"])
    
    if session.memory == "Bad (나쁨)" and session.stress_coping == "Good (좋음)":
        session.stress_coping = random.choice(["Average (보통)", "Poor (나쁨)"])


def _apply_bmi_body_constraints(session):
    """
    Apply BMI and body composition consistency rules.
    
    Rules:
    - Low BMI (<18.5) + Solid body is inconsistent
    - High BMI (>30) + Soft body is inconsistent
    """
    height_m = session.height / 100
    bmi = session.weight / (height_m * height_m)
    
    if bmi < 18.5 and session.body_solidity == "Solid (단단)":
        session.body_solidity = "Soft (물렁)"
    if bmi > 30 and session.body_solidity == "Soft (물렁)":
        session.body_solidity = random.choice(["Normal (보통)", "Solid (단단)"])


def _apply_sleep_constraints(session):
    """
    Apply sleep-related consistency rules.
    
    Rules:
    - Very short sleep (≤4 hours) affects waking state
    - Good sleep (≥8 hours, deep) should feel refreshed
    - Insomnia = shallow sleep
    - Frequent night urination = poor sleep
    - Frequent dreams/nightmares = shallow sleep
    """
    if session.sleep_hours <= 4:
        session.sleep_waking_state = random.choice(["Tired", "Heavy"])
    
    if session.sleep_hours >= 8 and session.sleep_depth == "Deep (깊음)":
        session.sleep_waking_state = "Refreshed"
    
    if session.insomnia_onset or session.insomnia_maintain:
        session.sleep_depth = "Shallow/Light (얕음)"
    
    if session.urine_freq_night >= 3:
        session.sleep_depth = "Shallow/Light (얕음)"
        if session.sleep_waking_state == "Refreshed":
            session.sleep_waking_state = "Tired"
    
    if session.dreams in ["Frequent (자주)", "Nightmares (악몽)"]:
        session.sleep_depth = "Shallow/Light (얕음)"


def _apply_excretion_constraints(session):
    """
    Apply excretion-related consistency rules.
    
    Rules:
    - Constipation + Loose stool is inconsistent
    - Frequent stool (2-3/day) shouldn't be hard
    """
    if session.stool_freq == "Constipation" and session.stool_form == "Loose":
        session.stool_form = "Hard"
    
    if session.stool_freq == "2-3/day" and session.stool_form == "Hard":
        session.stool_form = random.choice(["Normal", "Loose"])


def _apply_pulse_tongue_constraints(session):
    """
    Apply pulse-tongue TKM diagnostic consistency rules.
    
    Rules:
    - Strong pulse + Pale tongue (deficiency sign) is rare
    - Weak pulse + Red tongue (heat sign) is inconsistent
    """
    if session.pulse_strength == "Strong" and session.tongue_color == "Pale":
        session.tongue_color = random.choice(["Pale Red", "Red"])
    
    if session.pulse_strength == "Weak" and session.tongue_color == "Red":
        session.tongue_color = random.choice(["Pale", "Pale Red"])
