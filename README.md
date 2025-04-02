# 혼밥메이트 (MealMingle)

혼밥을 하는 사람들의 건강한 식습관과 정서적 안정을 위한 맞춤형 관리 시스템입니다.

## 주요 기능

- 📝 식사 기록 및 분석
- 🥗 영양소 분석 및 모니터링
- 😊 정서 상태 관리
- 👥 커뮤니티 활동

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/MealMingle.git
cd MealMingle
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 애플리케이션 실행
```bash
streamlit run app.py
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 사이드바에서 원하는 메뉴 선택
3. 각 기능에 맞게 데이터 입력 및 확인

## 데이터 저장

- 식사 기록과 감정 기록은 `data` 디렉토리에 JSON 파일로 저장됩니다.
- 개인정보는 로컬 환경에서만 관리됩니다.

## 라이선스

MIT License 