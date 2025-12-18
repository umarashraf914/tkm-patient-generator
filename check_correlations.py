"""Check all correlations from images against implementation"""
from symptom_correlations import CORRELATION_COEFFICIENTS

# All correlations visible in the images - COMPLETE LIST
required_correlations = [
    # Image 2: 식욕-소화 클러스터
    (("appetite_good", "ocd"), -0.404),
    (("appetite_good", "obesity"), 0.687),
    (("appetite_good", "abdominal_obesity"), 0.373),
    (("appetite_good", "water_intake"), 0.311),
    (("appetite_good", "food_amount"), 0.349),
    (("appetite_good", "digestion_good"), 0.374),
    (("digestion_good", "dyspepsia"), -0.537),
    (("digestion_good", "heartburn"), -0.325),
    (("digestion_good", "nausea_vomit"), -0.345),
    (("heartburn", "dyspepsia"), 0.329),
    (("heartburn", "nausea_vomit"), 0.326),
    (("nausea_vomit", "dyspepsia"), 0.349),
    (("nausea_vomit", "belching"), 0.309),
    (("nausea_vomit", "upper_abd_pain"), 0.332),
    (("dyspepsia", "upper_abd_pain"), 0.372),
    (("dyspepsia", "lower_abd_pain"), 0.310),
    (("belching", "upper_abd_pain"), 0.455),
    (("belching", "gas_bloating"), 0.325),
    (("belching", "lower_abd_pain"), 0.300),
    (("abdominal_obesity", "food_amount"), 0.359),
    (("abdominal_obesity", "obesity"), 0.689),
    
    # Image 3: 호흡기 클러스터
    (("dyspnea", "thirst"), 0.307),
    (("dyspnea", "cough"), 0.319),
    (("dyspnea", "chest_pain"), 0.431),
    (("cough", "phlegm"), 0.438),
    (("cough", "throat_obstruction"), 0.351),
    (("phlegm", "throat_obstruction"), 0.443),
    
    # Image 4: 흉민-스트레스-수면 클러스터
    (("chest_tight", "headache"), 0.356),
    (("chest_tight", "upper_abd_pain"), 0.385),
    (("chest_tight", "stress"), 0.322),
    (("chest_tight", "sleep_quality"), 0.373),
    (("chest_tight", "dreams"), 0.332),
    (("chest_tight", "chest_pain"), 0.359),
    (("chest_tight", "dyspnea"), 0.431),
    (("chest_pain", "dreams"), 0.301),
    (("stress", "belching"), 0.323),
    (("stress", "activity_level"), 0.323),
    (("stress", "sleep_quality"), 0.430),
    (("sleep_quality", "sleep_disorder"), 0.695),
    (("sleep_disorder", "dreams"), 0.327),
    (("dreams", "anxiety"), 0.481),
    (("dreams", "depression"), 0.358),
    (("anxiety", "depression"), 0.312),
    (("anxiety", "chest_pain"), 0.326),
    
    # Image 5: 기타 클러스터들
    (("fatigue", "pain"), 0.435),
    (("fatigue", "weakness"), 0.320),
    (("hearing_loss", "tinnitus"), 0.329),
    (("sweat_amount", "heat"), -0.372),
    (("hypertension", "diabetes"), 0.340),
    (("hypertension", "dyslipidemia"), 0.447),
    (("diabetes", "dyslipidemia"), 0.414),
]

print("Checking all image correlations against code...")
print()

missing = []
implemented = []

for (k1, k2), r in required_correlations:
    found = False
    if (k1, k2) in CORRELATION_COEFFICIENTS:
        found = True
    elif (k2, k1) in CORRELATION_COEFFICIENTS:
        found = True
    
    if found:
        implemented.append(((k1, k2), r))
    else:
        missing.append(((k1, k2), r))

print(f"Implemented: {len(implemented)}/{len(required_correlations)}")
print(f"Missing: {len(missing)}")
print()

if missing:
    print("MISSING CORRELATIONS (need to add):")
    for (k1, k2), r in missing:
        print(f'    ("{k1}", "{k2}"): {r},')
else:
    print("ALL CORRELATIONS IMPLEMENTED!")
