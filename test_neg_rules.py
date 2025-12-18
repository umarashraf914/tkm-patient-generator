"""
Quick test script for Page 26 negative correlation rules
"""
import sys
sys.path.insert(0, '.')

from constraints.negative_correlations import (
    _apply_appetite_motivation_rules,
    _apply_age_related_rules,
    _apply_social_history_rules,
    _apply_pain_related_rules,
    _apply_excretion_rules,
    _apply_physical_mental_rules,
    _apply_sensory_rules,
    _apply_cold_heat_consistency_rules,
    _apply_skin_face_consistency_rules
)

class MockSession:
    def __init__(self):
        # Demographics
        self.age = 25
        self.sex = 'Male (남)'
        self.job = 'Office (사무직)'
        
        # Test contradictory values
        self.appetite = 'None (없음)'
        self.motivation = 'High (높음)'  # SHOULD CHANGE
        
        self.social_alcohol_freq = 'None (비음주)'
        self.social_alcohol_amt = 5.0  # SHOULD BE 0
        self.social_smoke_daily = 0.0
        self.social_exercise_int = 'High (고)'
        self.social_exercise_time = 0  # SHOULD BE > 0
        
        self.physical_strength = 'Weak (허약)'
        self.fatigue_level = 'None (없음)'  # SHOULD CHANGE
        self.mental_clarity = 'Clear (맑음/청명)'
        self.memory = 'Bad (나쁨)'  # SHOULD CHANGE
        
        self.tinnitus_freq = 0
        self.tinnitus_sev = 5  # SHOULD BE 0
        
        self.heat_sensitivity = 5
        self.cold_sensitivity = 2
        self.temp = 35.5  # SHOULD INCREASE
        self.cold_heat_body = 'Hot (열 熱)'
        self.cold_heat_pref = 'Cold Sens (오한/추위탐)'  # SHOULD CHANGE
        self.drink_temp = 'Hot (열수)'
        
        self.skin_dry = 'Scaly (각질)'
        self.face_gloss = 'Shiny (윤기)'  # SHOULD CHANGE
        self.lip_dry = False
        
        self.abd_pain_sev = 0
        self.abd_pain_type = 'Sharp (예리통)'  # SHOULD BE None
        self.abd_tenderness = True
        
        self.urine_freq_day = 2
        self.urine_freq_night = 4  # SHOULD DECREASE
        self.stool_discomfort = False
        self.stool_form = 'Normal (보통)'
        self.urine_stream = 'Normal (정상)'
        self.urine_residual = False
        
        self.history_conditions = []
        self.meds_specific = []

def test_rules():
    session = MockSession()
    
    print('=== BEFORE ===')
    print(f'Appetite={session.appetite}, Motivation={session.motivation}')
    print(f'Alcohol={session.social_alcohol_amt}, Exercise time={session.social_exercise_time}')
    print(f'Strength={session.physical_strength}, Fatigue={session.fatigue_level}')
    print(f'Memory={session.memory}')
    print(f'Tinnitus freq={session.tinnitus_freq}, sev={session.tinnitus_sev}')
    print(f'Temp={session.temp}, Cold/heat pref={session.cold_heat_pref}')
    print(f'Face gloss={session.face_gloss}')
    print(f'Abd pain type={session.abd_pain_type}')
    print(f'Urine night={session.urine_freq_night}')
    
    # Apply rules
    _apply_appetite_motivation_rules(session)
    _apply_social_history_rules(session)
    _apply_physical_mental_rules(session)
    _apply_sensory_rules(session)
    _apply_cold_heat_consistency_rules(session)
    _apply_skin_face_consistency_rules(session)
    _apply_pain_related_rules(session)
    _apply_excretion_rules(session)
    
    print('\n=== AFTER ===')
    print(f'Motivation: {session.motivation} (was High)')
    print(f'Alcohol: {session.social_alcohol_amt} (was 5.0)')
    print(f'Exercise time: {session.social_exercise_time} (was 0)')
    print(f'Fatigue: {session.fatigue_level} (was None)')
    print(f'Memory: {session.memory} (was Bad)')
    print(f'Tinnitus sev: {session.tinnitus_sev} (was 5)')
    print(f'Temp: {session.temp} (was 35.5)')
    print(f'Cold/heat pref: {session.cold_heat_pref} (was Cold Sens)')
    print(f'Face gloss: {session.face_gloss} (was Shiny)')
    print(f'Abd pain type: {session.abd_pain_type} (was Sharp)')
    print(f'Urine night: {session.urine_freq_night} (was 4)')
    
    print('\n✅ All rules applied successfully!')

if __name__ == '__main__':
    test_rules()
