import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# 조건부 임포트 - 웹캠/화상 기능 필요한 라이브러리
try:
    from streamlit_webrtc import webrtc_streamer
    import cv2
    webrtc_available = True
except ImportError:
    webrtc_available = False

from PIL import Image
import random

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="혼밥메이트 - 혼밥 관리 시스템",
    page_icon="🍽️",
    layout="wide"
)

# 전역 스타일 설정
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #4CAF50;
        font-family: 'Noto Sans KR', sans-serif;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .result-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 저장 경로
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# 사용자 데이터 초기화
def init_user_data():
    if not (DATA_DIR / "users.json").exists():
        with open(DATA_DIR / "users.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_users():
    with open(DATA_DIR / "users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_DIR / "users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# 기본 데이터 구조
def init_data():
    if not (DATA_DIR / "meals.json").exists():
        with open(DATA_DIR / "meals.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    if not (DATA_DIR / "emotions.json").exists():
        with open(DATA_DIR / "emotions.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_meals():
    with open(DATA_DIR / "meals.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_meals(meals):
    with open(DATA_DIR / "meals.json", "w", encoding="utf-8") as f:
        json.dump(meals, f, ensure_ascii=False, indent=2)

def load_emotions():
    with open(DATA_DIR / "emotions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_emotions(emotions):
    with open(DATA_DIR / "emotions.json", "w", encoding="utf-8") as f:
        json.dump(emotions, f, ensure_ascii=False, indent=2)

# 로그인 페이지
def login_page():
    st.title("로그인")
    
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            users = load_users()
            for user in users:
                if user["username"] == username and user["password"] == password:
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    return True
            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
    return False

# 회원가입 페이지
def register_page():
    st.title("회원가입")
    
    with st.form("register_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        confirm_password = st.text_input("비밀번호 확인", type="password")
        email = st.text_input("이메일")
        
        submitted = st.form_submit_button("가입하기")
        
        if submitted:
            if password != confirm_password:
                st.error("비밀번호가 일치하지 않습니다.")
                return False
                
            users = load_users()
            if any(user["username"] == username for user in users):
                st.error("이미 존재하는 아이디입니다.")
                return False
                
            new_user = {
                "id": len(users) + 1,
                "username": username,
                "password": password,
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            
            users.append(new_user)
            save_users(users)
            st.success("회원가입이 완료되었습니다!")
            return True
    return False

# 정서 안정성 이미지
def get_random_emotional_image():
    images = [
        "https://source.unsplash.com/random/800x600/?nature,peaceful",
        "https://source.unsplash.com/random/800x600/?meditation",
        "https://source.unsplash.com/random/800x600/?mindfulness",
        "https://source.unsplash.com/random/800x600/?relaxation",
        "https://source.unsplash.com/random/800x600/?happiness"
    ]
    return random.choice(images)

# 음식 인식 및 분석을 위한 함수 추가
def analyze_food_image(image):
    """
    OpenCV를 사용하여 음식 이미지를 분석하고 음식 종류와 영양소 정보를 반환합니다.
    실제 상용 시스템에서는 ML 모델을 사용하지만, 여기서는 이미지 특성을 기반으로 단순 분류합니다.
    """
    if cv2 is not None:
        # PIL 이미지를 OpenCV 형식으로 변환
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # 이미지 특성 추출을 위한 처리
        avg_color = np.mean(img_cv, axis=(0, 1))
        hsv_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        avg_hsv = np.mean(hsv_img, axis=(0, 1))
        
        # 색상 기반 단순 분류 
        # 실제 프로젝트에서는 CNN 등의 ML 모델을 사용해야 함
        h_value = avg_hsv[0]
        s_value = avg_hsv[1]
        v_value = avg_hsv[2]
        
        # 간단한 색상 기반 분류
        foods = [
            {"name": "샐러드", "calories": 120, "protein": 5, "carbs": 15, "fat": 3},
            {"name": "구운 고기", "calories": 350, "protein": 35, "carbs": 0, "fat": 22},
            {"name": "파스타", "calories": 380, "protein": 12, "carbs": 70, "fat": 10},
            {"name": "국/찌개", "calories": 250, "protein": 18, "carbs": 20, "fat": 12},
            {"name": "김밥/초밥", "calories": 320, "protein": 10, "carbs": 60, "fat": 8},
            {"name": "과일", "calories": 100, "protein": 1, "carbs": 25, "fat": 0}
        ]
        
        # 색상, 채도, 명도를 기반으로 음식 종류 결정
        # 실제 구현에서는 더 정교한 알고리즘이 필요함
        if 20 <= h_value <= 40 and s_value > 100:  # 갈색/노란색 계열
            if v_value > 150:
                return foods[2]  # 파스타
            else:
                return foods[1]  # 구운 고기
        elif h_value < 20 and s_value < 80:  # 붉은색 계열, 낮은 채도
            return foods[3]  # 국/찌개
        elif 40 <= h_value <= 80:  # 녹색/황색 계열
            if s_value > 100:
                return foods[0]  # 샐러드
            else:
                return foods[5]  # 과일
        elif 0 <= h_value <= 30 and 60 <= s_value <= 150:
            return foods[4]  # 김밥/초밥
        else:
            # 위의 조건에 맞지 않으면 랜덤하게 음식 선택
            idx = int(h_value) % len(foods)
            return foods[idx]
    
    # OpenCV를 사용할 수 없는 경우
    return None

# 메인 페이지
def main():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if st.session_state.user_id is None:
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            if login_page():
                st.rerun()
        
        with tab2:
            if register_page():
                st.rerun()
    else:
        st.title(f"🍽️ 혼밥메이트 - 환영합니다, {st.session_state.username}님!")
        
        # 로그아웃 버튼
        if st.sidebar.button("로그아웃"):
            st.session_state.user_id = None
            st.rerun()
        
        # 사이드바 메뉴
        menu = st.sidebar.selectbox(
            "메뉴 선택",
            ["홈", "식사 기록", "영양 분석", "정서 관리", "커뮤니티", "설정"]
        )
        
        if menu == "홈":
            show_home()
        elif menu == "식사 기록":
            show_meal_record()
        elif menu == "영양 분석":
            show_nutrition_analysis()
        elif menu == "정서 관리":
            show_emotional_management()
        elif menu == "커뮤니티":
            show_community()
        elif menu == "설정":
            show_settings()

def show_home():
    st.header("환영합니다! 🍽️")
    st.write("""
    혼밥메이트는 혼밥을 하는 분들의 건강한 식습관과 정서적 안정을 위한 맞춤형 관리 시스템입니다.
    
    ### 주요 기능
    - 📝 식사 기록 및 분석
    - 🥗 영양소 분석 및 모니터링
    - 😊 정서 상태 관리
    - 👥 커뮤니티 활동
    """)
    
    # 오늘의 통계
    col1, col2, col3 = st.columns(3)
    
    with col1:
        meals = load_meals()
        today = datetime.now().date()
        today_meals = len([m for m in meals if datetime.strptime(m['date'], '%Y-%m-%d').date() == today])
        st.metric(label="오늘의 식사", value=f"{today_meals}회")
    
    with col2:
        emotions = load_emotions()
        today_emotions = len([e for e in emotions if datetime.strptime(e['date'], '%Y-%m-%d').date() == today])
        st.metric(label="오늘의 감정 기록", value=f"{today_emotions}회")
    
    with col3:
        avg_mood = np.mean([e['mood'] for e in emotions]) if emotions else 0
        st.metric(label="평균 기분 점수", value=f"{avg_mood:.1f}/5.0")

def show_meal_record():
    st.header("식사 기록")
    
    # 이미지 미리보기 및 분석 영역을 폼 밖으로 이동
    meal_photo = st.file_uploader("식사 사진", type=['jpg', 'jpeg', 'png'])
    
    # 분석 결과 저장용 변수
    food_analysis = None
    
    # 미리보기 및 분석 정보 표시
    if meal_photo is not None:
        # 이미지 표시 (use_column_width 대신 use_container_width 사용)
        image = Image.open(meal_photo)
        st.image(image, caption="업로드된 식사 사진", use_container_width=True)
        
        # 음식 분석 결과
        if webrtc_available and cv2 is not None:
            st.subheader("음식 분석 결과")
            
            # 음식 인식 실행
            food_analysis = analyze_food_image(image)
            
            if food_analysis:
                # 인식된 음식 정보 표시
                st.success(f"인식된 음식: {food_analysis['name']}")
                
                # 분석 결과 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("예상 칼로리", f"{food_analysis['calories']} kcal")
                    st.metric("단백질", f"{food_analysis['protein']}g")
                with col2:
                    st.metric("탄수화물", f"{food_analysis['carbs']}g") 
                    st.metric("지방", f"{food_analysis['fat']}g")
                
                # 분석 결과에 따른 맞춤형 코멘트
                if food_analysis['protein'] > 20:
                    st.info("단백질이 풍부한 식사입니다. 근육 발달과 포만감 유지에 좋습니다.")
                elif food_analysis['carbs'] > 50:
                    st.info("탄수화물이 많은 식사입니다. 에너지원으로 좋지만, 과다 섭취는 피하세요.")
                elif food_analysis['fat'] > 15:
                    st.info("지방 함량이 높은 식사입니다. 소화에 시간이 더 걸릴 수 있습니다.")
                else:
                    st.info("균형 잡힌 식사로 보입니다. 다양한 영양소를 골고루 섭취하세요.")
            else:
                st.warning("음식을 인식하지 못했습니다. 다른 사진을 시도해보세요.")
        else:
            # 더 나은 사용자 경험을 위해 기본 분석 제공
            st.subheader("기본 음식 분석")
            st.warning("상세 이미지 분석을 위해서는 OpenCV(cv2) 패키지가 필요합니다.")
            
            # 기본 예상 정보 제공
            col1, col2 = st.columns(2)
            with col1:
                st.metric("예상 칼로리", "300-500 kcal")
                st.metric("단백질", "10-20g")
            with col2:
                st.metric("탄수화물", "40-60g") 
                st.metric("지방", "10-15g")
            
            st.info("참고: 이 정보는 OpenCV 없이 제공되는 기본 추정치입니다. 정확한 분석을 위해 'pip install opencv-python'을 실행하여 OpenCV를 설치하세요.")
    
    with st.form("meal_record"):
        col1, col2 = st.columns(2)
        
        with col1:
            meal_type = st.selectbox("식사 유형", ["아침", "점심", "저녁", "간식"])
            meal_time = st.time_input("식사 시간")
            meal_date = st.date_input("날짜")
            
        with col2:
            meal_location = st.selectbox("식사 장소", ["집", "외식", "배달"])
            mood = st.slider("식사 시 기분", 1, 5, 3)
            
        meal_content = st.text_area("식사 내용")
        
        submitted = st.form_submit_button("기록하기")
        
        if submitted:
            meal_data = {
                "id": len(load_meals()) + 1,
                "user_id": st.session_state.user_id,
                "type": meal_type,
                "time": meal_time.strftime("%H:%M"),
                "date": meal_date.strftime("%Y-%m-%d"),
                "location": meal_location,
                "mood": mood,
                "content": meal_content,
                "has_photo": meal_photo is not None,
                "created_at": datetime.now().isoformat()
            }
            
            # 음식 분석 결과가 있으면 추가
            if food_analysis:
                meal_data["food_type"] = food_analysis["name"]
                meal_data["calories"] = food_analysis["calories"]
                meal_data["protein"] = food_analysis["protein"]
                meal_data["carbs"] = food_analysis["carbs"]
                meal_data["fat"] = food_analysis["fat"]
            
            # 이미지 저장 (옵션)
            if meal_photo is not None:
                # 이미지 폴더 생성
                img_dir = DATA_DIR / "images"
                img_dir.mkdir(exist_ok=True)
                
                # 이미지 저장
                img_path = f"meal_{meal_data['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                img_full_path = img_dir / img_path
                
                with open(img_full_path, "wb") as f:
                    f.write(meal_photo.getbuffer())
                
                meal_data["photo_path"] = str(img_path)
            
            meals = load_meals()
            meals.append(meal_data)
            save_meals(meals)
            
            st.success("식사가 성공적으로 기록되었습니다! 🎉")

def show_nutrition_analysis():
    st.header("영양 분석")
    
    # 영양소 데이터 시각화
    nutrition_data = {
        "단백질": 30,
        "지방": 20,
        "탄수화물": 50
    }
    
    # 영양소 파이 차트
    fig = px.pie(
        values=list(nutrition_data.values()),
        names=list(nutrition_data.keys()),
        title="영양소 비율"
    )
    st.plotly_chart(fig)
    
    # 영양소 상세 정보
    st.subheader("영양소 상세 정보")
    for nutrient, percentage in nutrition_data.items():
        st.write(f"- {nutrient}: {percentage}%")
    
    # 식사 패턴 분석
    st.subheader("식사 패턴 분석")
    meals = load_meals()
    if meals:
        df = pd.DataFrame(meals)
        df['date'] = pd.to_datetime(df['date'])
        daily_meals = df.groupby('date').size()
        
        fig = px.line(
            daily_meals,
            title="일별 식사 횟수"
        )
        st.plotly_chart(fig)

def show_emotional_management():
    st.header("정서 관리")
    
    # 기분 기록
    st.subheader("오늘의 기분")
    with st.form("emotion_record"):
        mood = st.slider("기분 점수", 1, 5, 3)
        emotion_diary = st.text_area("오늘의 감정을 기록해보세요")
        
        submitted = st.form_submit_button("기록하기")
        
        if submitted:
            emotion_data = {
                "id": len(load_emotions()) + 1,
                "user_id": st.session_state.user_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "mood": mood,
                "diary": emotion_diary,
                "created_at": datetime.now().isoformat()
            }
            
            emotions = load_emotions()
            emotions.append(emotion_data)
            save_emotions(emotions)
            
            st.success("감정이 성공적으로 기록되었습니다! 🎉")
    
    # 정서 안정성 이미지
    st.subheader("오늘의 마음 상태")
    emotional_image = get_random_emotional_image()
    st.image(emotional_image, caption="당신의 마음을 진정시키는 이미지", use_container_width=True)
    
    # 화상 통화 기능
    st.subheader("화상 상담")
    if webrtc_available:
        webrtc_streamer(
            key="emotion_chat",
            video_frame_callback=None
        )
    else:
        st.error("화상 통화 기능을 사용할 수 없습니다. streamlit-webrtc와 OpenCV(cv2) 패키지가 필요합니다.")
        st.info("설치 방법: pip install streamlit-webrtc opencv-python")
    
    # 긍정적 활동 추천
    st.subheader("추천 활동")
    activities = [
        "가벼운 스트레칭",
        "짧은 산책",
        "즐거운 음악 듣기",
        "친구와 통화하기"
    ]
    
    for activity in activities:
        if st.button(activity):
            st.success(f"{activity}를 시작해보세요!")

def show_community():
    st.header("커뮤니티")
    
    # 게시글 목록
    st.subheader("최근 게시글")
    posts = [
        {"title": "오늘의 혼밥", "author": "사용자1", "likes": 5},
        {"title": "맛있는 레시피 공유", "author": "사용자2", "likes": 3}
    ]
    
    for post in posts:
        with st.expander(f"{post['title']} - {post['author']} (좋아요: {post['likes']})"):
            st.write("게시글 내용...")

def show_settings():
    st.header("설정")
    
    # 알림 설정
    st.subheader("알림 설정")
    notification_time = st.time_input("식사 알림 시간")
    
    # 개인정보 설정
    st.subheader("개인정보")
    age = st.number_input("나이", min_value=1, max_value=100)
    gender = st.radio("성별", ["남성", "여성"])
    
    # 목표 설정
    st.subheader("목표 설정")
    target_weight = st.number_input("목표 체중(kg)", min_value=30.0, max_value=200.0, step=0.1)

if __name__ == "__main__":
    init_data()
    init_user_data()
    main() 
