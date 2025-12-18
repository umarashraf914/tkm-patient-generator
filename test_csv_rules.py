"""
Test script for CSV-based generation rules
"""
from generation_rules import generate_patient_from_rules, load_rules

# Test generating a cold patient with 풍한형 pattern
print("=== 감기 (풍한형) Patient Data Sample ===")
patient_data = generate_patient_from_rules('감기', '풍한형')

sample_keys = [
    '인구학적 정보__성별', 
    '인구학적 정보__나이', 
    '활력징후__체온', 
    '감기환자_감기주소증 유형_발열', 
    '감기환자_감기주소증 유형_오한', 
    '감기환자_감기주소증 유형_콧물 색'
]

for key in sample_keys:
    if key in patient_data:
        item = patient_data[key]
        print(f'{key}:')
        print(f'  Option: {item["option_number"]}')
        desc = item["quantitative"]
        if len(desc) > 80:
            desc = desc[:80] + "..."
        print(f'  Description: {desc}')
        print()

# Test 알레르기비염 with 소청룡탕 pattern
print("\n=== 알레르기비염 (소청룡탕) Patient Data Sample ===")
patient_data2 = generate_patient_from_rules('알레르기비염', '소청룡탕')

sample_keys2 = [
    '인구학적 정보__성별', 
    '인구학적 정보__나이', 
    '알레르기 비염환자_알레르기 비염 주소증 유형_재채기',
    '알레르기 비염환자_알레르기 비염 주소증 유형_콧물 알레르기',
    '알레르기 비염환자_알레르기 비염 주소증 유형_콧물 색 알레르기 비염',
]

for key in sample_keys2:
    if key in patient_data2:
        item = patient_data2[key]
        print(f'{key}:')
        print(f'  Option: {item["option_number"]}')
        desc = item["quantitative"]
        if len(desc) > 80:
            desc = desc[:80] + "..."
        print(f'  Description: {desc}')
        print()

print("=== CSV Rules Integration Test Complete ===")
