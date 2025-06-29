import streamlit as st
import random
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

def run():
    # MongoDB 연결
    MONGO_URI = "mongodb+srv://sajw1994:dWU6s4KKERQn4ynF@cluster0.c9zb3hn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    def save_to_mongodb(result_type, description, user_info):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client['automation_db']
            collection = db['inspection_records']
            
            data = {
                'result_type': result_type,
                'description': description,
                'user_info': user_info,
                'created_at': datetime.now(),
                'city': user_info.get('city', '성남시'),
                'source': '테토에겐'  # 구분을 위해 source 필드 추가
            }
            
            result = collection.insert_one(data)
            client.close()
            return True
        except Exception as e:
            st.error(f"데이터 저장 중 오류: {e}")
            return False
    
    def get_statistics():
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client['automation_db']
            collection = db['inspection_records']
            
            # 테토에겐 데이터만 집계
            pipeline = [
                {"$match": {"source": "테토에겐"}},
                {"$group": {"_id": "$result_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            results = list(collection.aggregate(pipeline))
            
            seongnam_pipeline = [
                {"$match": {"city": "성남시", "source": "테토에겐"}},
                {"$group": {"_id": "$result_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            seongnam_results = list(collection.aggregate(seongnam_pipeline))
            
            client.close()
            return results, seongnam_results
        except Exception as e:
            st.error(f"통계 조회 중 오류: {e}")
            return [], []
    
    # CSS 스타일 (MBTI 검사기 스타일 참고)
    st.markdown("""
    <style>
    .big-font { font-size: 1.5rem !important; }
    .teto-btn-row { display: flex; gap: 1.2rem; margin: 1.2rem 0 2.2rem 0; justify-content: center; }
    .teto-btn {
        font-size: 1.15rem !important;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.7em 1.7em;
        margin: 0 0.2em;
        cursor: pointer;
        transition: background 0.2s, color 0.2s, box-shadow 0.2s;
        background: #f4f4ff;
        color: #333;
        box-shadow: 0 2px 8px #e0e0ff33;
    }
    .teto-btn.selected {
        color: #fff !important;
        box-shadow: 0 4px 16px #bbaaff44;
    }
    .fadein-q {
        animation: fadein 0.7s;
    }
    @keyframes fadein {
        from { opacity: 0; transform: translateY(30px);}
        to { opacity: 1; transform: translateY(0);}
    }
    .percent-bar {
        height: 32px;
        border-radius: 16px;
        background: #f0f0ff;
        margin-bottom: 0.5em;
        overflow: hidden;
        display: flex;
        align-items: center;
    }
    .percent-bar-inner {
        height: 100%;
        border-radius: 16px;
        background: linear-gradient(90deg, #9D5CFF 10%, #5CFFD1 90%);
        color: #fff;
        font-weight: bold;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 1em;
        transition: width 0.5s;
    }
    .result-card {
        margin-top: 2em;
        padding: 1.5em 1.5em 1.2em 1.5em;
        background: #f8f6ff;
        border-radius: 18px;
        border: 1.5px solid #e3e6f3;
    }
    /* 바 그래프 관련 스타일 */
    .custom-bar-bg { width: 100%; height: 32px; background: #e0e0e0; border-radius: 16px; position: relative; margin-bottom: 0.5em; }
    .custom-bar-fill-left { height: 100%; border-radius: 16px 0 0 16px !important; background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%); position: absolute; left: 0; top: 0; }
    .custom-bar-fill-right { height: 100%; border-radius: 0 16px 16px 0 !important; background: linear-gradient(90deg, #ef4444 0%, #f87171 100%); position: absolute; right: 0; top: 0; }
    .custom-bar-label { position: absolute; width: 100%; text-align: center; top: 0; line-height: 32px; font-weight: bold; color: #222; }
    @media (prefers-color-scheme: dark) {
        .test-container, .question-card {
            color: #f4f6fb !important;
        }
        .test-container h3, .test-container p, .test-container li {
            color: #f4f6fb !important;
        }
        .question-card h4 {
            color: #f4f6fb !important;
        }
        .teto-result-desc, .result-card, .teto-result-desc * {
            color: #f4f6fb !important;
        }
        .custom-bar-bg { background: #333 !important; }
        .custom-bar-label { color: #fff !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🎭 테토에겐 테스트")
    st.markdown('<div class="big-font">당신은 테토남, 에겐남, 테토녀, 에겐녀 중 누구일까요?<br>각 문항마다 더 나와 비슷한 쪽을 선택하세요.</div>', unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📝 테스트하기", "📊 통계보기"])
    
    with tab1:
        # 테스트 질문들 (연애 관련 포함, 보강)
        questions = [
            {
                "question": "친구들과 만날 때 나는...",
                "options": [
                    "활발하게 대화를 이끌어가는 편이다",
                    "조용히 듣고 있다가 적절한 타이밍에 말한다"
                ]
            },
            {
                "question": "새로운 사람을 만날 때...",
                "options": [
                    "먼저 다가가서 인사를 건넨다",
                    "상대방이 먼저 다가올 때까지 기다린다"
                ]
            },
            {
                "question": "문제가 생겼을 때 나는...",
                "options": [
                    "즉시 해결책을 찾으려고 노력한다",
                    "차분히 상황을 파악한 후 대응한다"
                ]
            },
            {
                "question": "여가 시간에 나는...",
                "options": [
                    "새로운 활동이나 취미를 시도한다",
                    "편안하고 익숙한 활동을 즐긴다"
                ]
            },
            {
                "question": "감정 표현에 대해...",
                "options": [
                    "솔직하게 감정을 표현하는 편이다",
                    "감정을 조절해서 표현한다"
                ]
            },
            {
                "question": "계획을 세울 때...",
                "options": [
                    "즉흥적으로 행동하는 편이다",
                    "미리 계획을 세우고 실행한다"
                ]
            },
            {
                "question": "스트레스 상황에서...",
                "options": [
                    "다른 사람과 이야기하며 해소한다",
                    "혼자만의 시간을 가지며 해소한다"
                ]
            },
            {
                "question": "의사결정을 할 때...",
                "options": [
                    "직감과 감정에 따라 결정한다",
                    "논리적 분석 후 결정한다"
                ]
            },
            # 연애 관련 질문 추가
            {
                "question": "연인과의 갈등이 생겼을 때 나는...",
                "options": [
                    "바로 대화를 시도하며 감정을 솔직하게 표현한다",
                    "잠시 시간을 갖고 차분히 생각한 뒤 조심스럽게 이야기한다"
                ]
            },
            {
                "question": "데이트 약속이 갑자기 취소되면...",
                "options": [
                    "아쉬워서 바로 다른 계획을 세운다",
                    "혼자만의 시간을 즐기며 여유를 갖는다"
                ]
            },
            {
                "question": "연인에게 서프라이즈 이벤트를...",
                "options": [
                    "자주 준비하며 감동을 주고 싶어 한다",
                    "특별한 날에만 신중하게 준비한다"
                ]
            },
        ]
        
        # 세션 상태 초기화
        if 'test_started' not in st.session_state:
            st.session_state.test_started = False
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
        if 'answers' not in st.session_state:
            st.session_state.answers = []
        if 'test_completed' not in st.session_state:
            st.session_state.test_completed = False
        if 'result_saved' not in st.session_state:
            st.session_state.result_saved = False
        
        # 테스트 시작
        if not st.session_state.test_started:
            st.markdown("""
            <div style="margin-top:2em; padding:1.5em 1.5em 1.2em 1.5em; background:#f8f6ff; border-radius:18px; border:1.5px solid #e3e6f3;">
                <div style="font-size:1.25rem; font-weight:700; color:#7a5cff; margin-bottom:0.5em;">테토에겐 테스트란?</div>
                <div style="font-size:1.08rem; color:#444; margin-bottom:1em;">테토에겐은 성격 유형을 4가지로 분류하는 테스트입니다:</div>
                <ul style="font-size:1.05rem; color:#333; margin-bottom:1em;">
                    <li><strong>테토남</strong>: 활발하고 외향적인 남성형</li>
                    <li><strong>에겐남</strong>: 차분하고 내향적인 남성형</li>
                    <li><strong>테토녀</strong>: 활발하고 외향적인 여성형</li>
                    <li><strong>에겐녀</strong>: 차분하고 내향적인 여성형</li>
                </ul>
                <div style="font-size:1.08rem; color:#444;">총 8개의 질문에 답하시면 됩니다. 솔직하게 답해주세요!</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("테스트 시작하기", type="primary", use_container_width=True):
                st.session_state.test_started = True
                st.rerun()
        
        # 테스트 진행
        elif not st.session_state.test_completed and st.session_state.current_question < len(questions):
            question = questions[st.session_state.current_question]
            
            # 진행 상황 표시
            st.markdown(
                f"""
                <div style="text-align:center; margin-bottom:0.7em; font-size:1.15rem; color:#7a5cff; font-weight:600;">
                    <span>문항 {st.session_state.current_question+1} / {len(questions)}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(f'<div class="big-font fadein-q"><b>{st.session_state.current_question+1}. {question["question"]}</b></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="small")
            
            with col1:
                if st.button(f"A: {question['options'][0]}", key=f"teto_btn_{st.session_state.current_question}_0", use_container_width=True):
                    st.session_state.answers.append(0)
                    st.session_state.current_question += 1
                    st.rerun()
            
            with col2:
                if st.button(f"B: {question['options'][1]}", key=f"teto_btn_{st.session_state.current_question}_1", use_container_width=True):
                    st.session_state.answers.append(1)
                    st.session_state.current_question += 1
                    st.rerun()
            
            # 진행률 표시
            progress = st.session_state.current_question / len(questions)
            st.progress(progress)
            
            # 이전 버튼
            if st.session_state.current_question > 0:
                if st.button("이전", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.session_state.answers.pop()
                    st.rerun()
        
        # 결과 계산 및 표시
        elif st.session_state.test_completed or st.session_state.current_question >= len(questions):
            if not st.session_state.test_completed:
                st.session_state.test_completed = True
                # 테토 점수: answers에서 0의 개수
                teto_score = st.session_state.answers.count(0)
                # 결과 결정 (7~8: 테토남, 5~6: 에겐남, 3~4: 테토녀, 0~2: 에겐녀)
                if teto_score >= 7:
                    result = "테토남"
                    description = """
                    <b>활력과 리더십의 화신!</b><br>
                    당신은 언제나 중심에서 분위기를 이끄는 에너지 넘치는 리더입니다.<br>
                    새로운 도전을 두려워하지 않고, 사람들과의 소통에서 진정한 즐거움을 느끼죠.<br>
                    당신의 긍정적 에너지는 주변을 밝게 비추는 태양과 같습니다.<br>
                    <b>"내가 가는 곳이 곧 무대!"</b><br>
                    앞으로도 당신만의 열정과 추진력으로 멋진 변화를 만들어가세요!
                    """
                elif teto_score >= 5:
                    result = "에겐남"
                    description = """
                    <b>분석과 신중함의 대가!</b><br>
                    당신은 깊이 있는 사고와 논리로 세상을 바라보는 전략가입니다.<br>
                    조용하지만 강한 내면의 힘으로, 중요한 순간에 묵직한 한 방을 보여줍니다.<br>
                    주변 사람들은 당신의 신뢰감과 안정감에 큰 의지를 하죠.<br>
                    <b>"말보다 행동, 즉흥보다 계획!"</b><br>
                    당신의 신중함이 모두에게 든든한 버팀목이 됩니다.
                    """
                elif teto_score >= 3:
                    result = "테토녀"
                    description = """
                    <b>사교성과 창의력의 아이콘!</b><br>
                    당신은 어디서든 빛나는 존재, 모두의 친구입니다.<br>
                    감정 표현이 풍부하고, 새로운 아이디어로 주변을 놀라게 하죠.<br>
                    당신의 따뜻한 미소와 유쾌함은 모두에게 긍정의 바이러스를 전파합니다.<br>
                    <b>"내가 있으면 분위기가 살아난다!"</b><br>
                    앞으로도 당신만의 매력으로 세상을 환하게 밝혀주세요!
                    """
                else:
                    result = "에겐녀"
                    description = """
                    <b>섬세함과 공감의 마법사!</b><br>
                    당신은 조용하지만 깊은 공감력으로 사람들의 마음을 어루만집니다.<br>
                    세심한 배려와 따뜻한 시선으로, 주변에 안정감을 선사하죠.<br>
                    혼자만의 시간도 소중히 여기며, 내면의 성장을 추구합니다.<br>
                    <b>"작지만 강한, 조용한 힘!"</b><br>
                    당신의 섬세함이 세상을 더 아름답게 만듭니다.
                    """
                st.session_state.result = result
                st.session_state.description = description
            
            # 결과와 해설을 먼저 표시
            st.markdown(f"<div class='big-font'><b>당신의 테토에겐 유형은 <span style='color:#7a5cff'>{st.session_state.result}</span> 입니다!</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='teto-result-desc' style='font-size:1.08rem; color:#444; margin-bottom:1.5em;'>{st.session_state.description}</div>", unsafe_allow_html=True)
            
            # 저장은 결과와 해설을 보여준 뒤에 진행
            if not st.session_state.result_saved:
                user_info = {"city": "성남시", "gender": "미상", "age_group": "미상"}
                if save_to_mongodb(st.session_state.result, st.session_state.description, user_info):
                    st.session_state.save_message = "✅ 결과가 성공적으로 저장되었습니다!"
                else:
                    st.session_state.save_message = "❌ 결과 저장에 실패했습니다."
                st.session_state.result_saved = True
            
            # 저장 메시지는 아래에 info로 작게 표시
            if st.session_state.get('save_message'):
                st.info(st.session_state.save_message)
            
            if st.button("다시 테스트하기", use_container_width=True):
                st.session_state.test_started = False
                st.session_state.current_question = 0
                st.session_state.answers = []
                st.session_state.test_completed = False
                st.session_state.result_saved = False
                st.session_state.save_message = ""
                st.rerun()
    
    with tab2:
        st.markdown("### 📊 성남시 테토에겐 통계")
        if st.button("통계 새로고침", type="primary"):
            st.rerun()
        _, seongnam_results = get_statistics()
        # 남성/여성 분리 집계
        nam_count = {"테토남": 0, "에겐남": 0}
        nyeo_count = {"테토녀": 0, "에겐녀": 0}
        for item in seongnam_results:
            if item["_id"] in nam_count:
                nam_count[item["_id"]] = item["count"]
            elif item["_id"] in nyeo_count:
                nyeo_count[item["_id"]] = item["count"]
        total_nam = sum(nam_count.values())
        total_nyeo = sum(nyeo_count.values())
        # 남성 바
        st.markdown("#### 👨 남성 비율")
        if total_nam > 0:
            left_pct = int(round(nam_count["테토남"] / total_nam * 100))
            right_pct = 100 - left_pct
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-weight:600;'><span>테토남</span><span>에겐남</span></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='custom-bar-bg'>
                <div class='custom-bar-fill-left' style='width:{left_pct}%;'></div>
                <div class='custom-bar-fill-right' style='width:{right_pct}%;'></div>
                <div class='custom-bar-label'>테토남 {left_pct}%  |  에겐남 {right_pct}%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("아직 남성 데이터가 없습니다.")
        # 여성 바
        st.markdown("#### 👩 여성 비율")
        if total_nyeo > 0:
            left_pct = int(round(nyeo_count["테토녀"] / total_nyeo * 100))
            right_pct = 100 - left_pct
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-weight:600;'><span>테토녀</span><span>에겐녀</span></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='custom-bar-bg'>
                <div class='custom-bar-fill-left' style='width:{left_pct}%; background: linear-gradient(90deg, #10b981 0%, #34d399 100%);'></div>
                <div class='custom-bar-fill-right' style='width:{right_pct}%; background: linear-gradient(90deg, #a21caf 0%, #f472b6 100%);'></div>
                <div class='custom-bar-label'>테토녀 {left_pct}%  |  에겐녀 {right_pct}%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("아직 여성 데이터가 없습니다.")

if __name__ == "__main__":
    run()
