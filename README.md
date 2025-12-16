# 🏥 TKM Virtual Patient Generator

A Streamlit-based application for generating realistic Traditional Korean Medicine (TKM) clinical scenarios for medical education and training.

## Features

- **4 Disease Categories**: Common Cold (감기), Allergic Rhinitis (비염), Back Pain (요통), Functional Dyspepsia (소화불량)
- **KCD Code Compliant**: Follows official Korean Classification of Diseases (Pages 21-22)
- **Pattern-Based Diagnosis**: 한열허실 (Cold-Heat-Deficiency-Excess) classification (Page 23)
- **KTAS Emergency Exclusion**: Automatically excludes emergency-level vital signs
- **Comprehensive Clinical Variables**: 60+ variables from official TKM clinical documentation

## Pattern Classifications

| Disease | Patterns | Representative Prescriptions |
|---------|----------|------------------------------|
| 감기 (Cold) | 풍한형, 풍열형 | 행소산, 삼소음, 은교산 |
| 비염 (Rhinitis) | 수체형 | 월비가반하탕, 소청룡탕 |
| 요통 (Back Pain) | 한/열/기허/양허/음허/식적/담음/기체/어혈 | 오적산, 팔미지황원 등 |
| 소화불량 (Dyspepsia) | 한/열/기허/양허/음허/식적/담음/기체/어혈 | 이진탕, 소적건비환 등 |

## How to Use

1. Click "🎲 Randomize" to generate a new virtual patient
2. Adjust parameters in the sidebar
3. Click "Generate Clinical Scenario" to create AI-generated case

## Deployment

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## License

For educational and research purposes only.
