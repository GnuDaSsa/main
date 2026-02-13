import streamlit as st
import random
from pymongo import MongoClient
from datetime import datetime

def run():
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
                'source': '테토에겐'
            }
            collection.insert_one(data)
            client.close()
            return True
        except Exception:
            return False

    def get_statistics():
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client['automation_db']
            collection = db['inspection_records']
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
        except Exception:
            return [], []

    # 10문항 시나리오형 질문 (전부 점수 반영)
    questions = [
        {
            "situation": "금요일 퇴근 후, 나는...",
            "A": "친구들한테 '오늘 어디 갈까?' 바로 연락함",
            "B": "집에서 혼자 치맥하며 유튜브 정주행이 최고의 힐링",
            "emoji": "🍻"
        },
        {
            "situation": "단톡방에 모임 공지가 올라왔다!",
            "A": "'나 갈게!!' 0.5초 만에 참석 버튼 누름",
            "B": "일단 읽씹하고... 누가 오나 파악부터 한다",
            "emoji": "📱"
        },
        {
            "situation": "처음 보는 사람이 옆자리에 앉았을 때...",
            "A": "'안녕하세요~ 여기 자주 오세요?' 자연스러운 말 걸기",
            "B": "이어폰 끼고 나만의 세계에 들어감. 평화 그 자체",
            "emoji": "👋"
        },
        {
            "situation": "팀 프로젝트 발표를 맡게 됐다!",
            "A": "오 신난다! 발표는 내 무대지~ PPT에 개그 포인트도 넣어야지",
            "B": "자료 준비는 잘 하는데... 발표는 다른 사람 하면 안 될까",
            "emoji": "🎤"
        },
        {
            "situation": "연인과 데이트 코스를 정할 때...",
            "A": "핫플 맛집 투어 + 팝업스토어 + 방탈출! 빡센 하루",
            "B": "집 근처 카페에서 대화하다가 산책하는 소소한 하루",
            "emoji": "💕"
        },
        {
            "situation": "스트레스 만렙일 때 나의 해소법은?",
            "A": "친구 불러서 수다 떨거나 노래방 가서 소리 지르기",
            "B": "방 정리하거나 일기 쓰면서 혼자 감정 정리",
            "emoji": "😤"
        },
        {
            "situation": "SNS에 사진을 올릴 때 나는...",
            "A": "셀카, 먹스타그램, 일상 공유를 일상적으로 올림",
            "B": "6개월에 한 번? 올려도 풍경 사진 위주",
            "emoji": "📸"
        },
        {
            "situation": "갑자기 3일 연휴가 생겼다!",
            "A": "바로 여행 계획! 누구랑 갈지 단톡방 소집",
            "B": "아무 계획 없이 집에서 쉬는 게 진정한 휴식",
            "emoji": "🏖️"
        },
        {
            "situation": "좋아하는 사람이 생겼을 때...",
            "A": "주변에 다 말하고, 적극적으로 다가감. 모 아니면 도!",
            "B": "혼자 끙끙 앓다가 몇 달 후에야 가까워지는 스타일",
            "emoji": "💘"
        },
        {
            "situation": "회의 중 내 의견이 무시당했을 때...",
            "A": "바로 다시 어필함! 내 의견의 근거를 명확하게 설명",
            "B": "일단 넘어가고, 나중에 글이나 메일로 정리해서 전달",
            "emoji": "🗣️"
        },
    ]

    RESULTS = {
        "테토남": {
            "emoji": "🔥",
            "color": "#EF4444",
            "gradient": "linear-gradient(135deg, #EF4444, #F97316)",
            "title": "에너지 폭발 리더형",
            "desc": "어딜 가든 분위기의 중심! 사람들이 자연스럽게 당신 주변에 모이고, 당신의 에너지는 전염력이 있음. 새로운 도전을 두려워하지 않는 행동파.",
            "traits": ["#인싸_중의_인싸", "#분위기_메이커", "#도전_만렙", "#행동이_빠른"],
            "motto": "내가 가는 곳이 곧 핫플레이스"
        },
        "에겐남": {
            "emoji": "🧊",
            "color": "#3B82F6",
            "gradient": "linear-gradient(135deg, #3B82F6, #8B5CF6)",
            "title": "차분한 전략가형",
            "desc": "조용하지만 강한 남자. 말수는 적어도 한 마디 한 마디에 무게감이 있음. 깊은 사고력으로 핵심을 꿰뚫는 인간 ChatGPT.",
            "traits": ["#말보다_행동", "#신뢰감_100%", "#전략적_사고", "#묵직한_존재감"],
            "motto": "조용히, 그러나 확실하게"
        },
        "테토녀": {
            "emoji": "✨",
            "color": "#EC4899",
            "gradient": "linear-gradient(135deg, #EC4899, #F59E0B)",
            "title": "감성 에너지 아이콘",
            "desc": "밝은 에너지와 풍부한 감성을 동시에 가진 매력 덩어리! 사람 챙기는 것도, 분위기 띄우는 것도 당신이 제일 잘함. 인간 비타민.",
            "traits": ["#무드_메이커", "#감성_충만", "#사람_좋아", "#창의력_폭발"],
            "motto": "내가 웃으면 세상이 밝아진다"
        },
        "에겐녀": {
            "emoji": "🌙",
            "color": "#8B5CF6",
            "gradient": "linear-gradient(135deg, #8B5CF6, #06B6D4)",
            "title": "섬세한 공감 마법사",
            "desc": "조용하지만 깊은 공감력으로 사람들의 마음을 치유하는 힐러. 혼자만의 세계가 풍요롭고, 섬세한 감각으로 남들이 못 보는 걸 봄.",
            "traits": ["#공감_능력_만렙", "#힐링_담당", "#섬세한_감각", "#내면이_풍요"],
            "motto": "작지만 강한, 조용한 힘"
        },
    }

    NUM_QUESTIONS = len(questions)

    # CSS
    st.markdown("""
    <style>
    .teto-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: 0.1em;
        background: linear-gradient(135deg, #ec4899, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .teto-subtitle {
        text-align: center;
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1.5em;
    }
    .q-card {
        background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(236,72,153,0.06));
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 20px;
        padding: 1.8em 1.5em;
        margin: 1em 0;
        text-align: center;
        animation: popIn 0.4s ease-out;
    }
    .q-emoji { font-size: 2.5rem; margin-bottom: 0.3em; }
    .q-num {
        font-size: 0.8rem;
        color: #a78bfa;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.4em;
    }
    .q-text {
        font-size: 1.35rem;
        font-weight: 800;
    }
    .progress-wrap {
        display: flex;
        align-items: center;
        gap: 0.8em;
        margin: 1.2em 0;
    }
    .progress-bg {
        flex: 1;
        height: 6px;
        background: rgba(148,163,184,0.2);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, #ec4899, #8b5cf6);
        transition: width 0.4s;
    }
    .progress-num {
        font-size: 0.85rem;
        font-weight: 700;
        color: #a78bfa;
    }
    .res-hero {
        text-align: center;
        padding: 2em 0.5em;
        animation: popIn 0.5s ease-out;
    }
    .res-emoji { font-size: 4rem; }
    .res-type { font-size: 2.2rem; font-weight: 900; margin: 0.2em 0; }
    .res-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5em; }
    .res-card {
        border-radius: 20px;
        padding: 1.5em;
        margin: 1em 0;
        border: 1px solid rgba(255,255,255,0.08);
        line-height: 1.8;
        font-size: 1.05rem;
    }
    .res-motto {
        text-align: center;
        font-style: italic;
        font-size: 1.1rem;
        color: #94a3b8;
        padding: 0.8em;
        margin: 0.8em 0;
        border-radius: 12px;
        background: rgba(148,163,184,0.08);
    }
    .tag-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5em;
        justify-content: center;
        margin: 1em 0;
    }
    .tag {
        padding: 0.4em 1em;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 700;
    }
    .stat-bar-wrap { margin: 0.8em 0; }
    .stat-bar-label {
        display: flex;
        justify-content: space-between;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.3em;
    }
    .stat-bar-bg {
        width: 100%;
        height: 32px;
        background: rgba(148,163,184,0.15);
        border-radius: 16px;
        position: relative;
        overflow: hidden;
    }
    .stat-bar-left {
        height: 100%;
        border-radius: 16px 0 0 16px;
        position: absolute;
        left: 0;
        top: 0;
    }
    .stat-bar-right {
        height: 100%;
        border-radius: 0 16px 16px 0;
        position: absolute;
        right: 0;
        top: 0;
    }
    .stat-bar-text {
        position: absolute;
        width: 100%;
        text-align: center;
        line-height: 32px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    @keyframes popIn {
        from { opacity: 0; transform: scale(0.95) translateY(16px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="teto-title">테토에겐 테스트</div>', unsafe_allow_html=True)
    st.markdown('<div class="teto-subtitle">나는 테토남? 에겐남? 테토녀? 에겐녀?<br>10가지 상황에서 골라보세요!</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🎯 테스트하기", "📊 통계보기"])

    with tab1:
        if 'teto_started' not in st.session_state:
            st.session_state.teto_started = False
        if 'teto_q' not in st.session_state:
            st.session_state.teto_q = 0
        if 'teto_ans' not in st.session_state:
            st.session_state.teto_ans = []
        if 'teto_done' not in st.session_state:
            st.session_state.teto_done = False
        if 'teto_saved' not in st.session_state:
            st.session_state.teto_saved = False

        if not st.session_state.teto_started:
            st.markdown("""
            <div style="text-align:center; padding:2em 1em; animation: popIn 0.5s ease-out;">
                <div style="font-size:3rem; margin-bottom:0.3em;">🎭</div>
                <div style="font-size:1.1rem; line-height:1.8; color:#94a3b8;">
                    <b style="color:#ec4899;">테토남</b> · <b style="color:#3b82f6;">에겐남</b> · <b style="color:#f59e0b;">테토녀</b> · <b style="color:#8b5cf6;">에겐녀</b><br>
                    10개 상황에 솔직하게 답해주세요!<br>
                    약 1~2분이면 끝나요 ⏱️
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("시작하기", type="primary", use_container_width=True):
                st.session_state.teto_started = True
                st.rerun()

        elif not st.session_state.teto_done and st.session_state.teto_q < NUM_QUESTIONS:
            idx = st.session_state.teto_q
            q = questions[idx]
            pct = int((idx / NUM_QUESTIONS) * 100)

            st.markdown(f"""
            <div class="progress-wrap">
                <div class="progress-bg"><div class="progress-fill" style="width:{pct}%"></div></div>
                <div class="progress-num">{idx+1}/{NUM_QUESTIONS}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="q-card">
                <div class="q-emoji">{q['emoji']}</div>
                <div class="q-num">QUESTION {idx+1}</div>
                <div class="q-text">{q['situation']}</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="medium")
            with col1:
                if st.button(f"A. {q['A']}", key=f"teto_a_{idx}", use_container_width=True):
                    st.session_state.teto_ans.append(1)
                    st.session_state.teto_q += 1
                    if st.session_state.teto_q >= NUM_QUESTIONS:
                        st.session_state.teto_done = True
                    st.rerun()
            with col2:
                if st.button(f"B. {q['B']}", key=f"teto_b_{idx}", use_container_width=True):
                    st.session_state.teto_ans.append(0)
                    st.session_state.teto_q += 1
                    if st.session_state.teto_q >= NUM_QUESTIONS:
                        st.session_state.teto_done = True
                    st.rerun()

            if idx > 0:
                if st.button("← 이전", key="teto_prev"):
                    st.session_state.teto_q -= 1
                    st.session_state.teto_ans.pop()
                    st.rerun()

        elif st.session_state.teto_done:
            score = sum(st.session_state.teto_ans)
            if score >= 8:
                result_key = "테토남"
            elif score >= 6:
                result_key = "테토녀"
            elif score >= 4:
                result_key = "에겐남"
            else:
                result_key = "에겐녀"

            r = RESULTS[result_key]

            st.markdown(f"""
            <div class="res-hero">
                <div class="res-emoji">{r['emoji']}</div>
                <div class="res-type" style="color:{r['color']}">{result_key}</div>
                <div class="res-title" style="color:{r['color']}">{r['title']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="res-card" style="background:{r['gradient'].replace(')', ',0.1)')}">{r['desc']}</div>
            """, unsafe_allow_html=True)

            tags_html = "".join(
                f'<span class="tag" style="background:{r["color"]}22; color:{r["color"]}; border:1px solid {r["color"]}44;">{t}</span>'
                for t in r['traits']
            )
            st.markdown(f'<div class="tag-wrap">{tags_html}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="res-motto">"{r["motto"]}"</div>', unsafe_allow_html=True)

            # 점수 표시
            st.markdown(f"""
            <div style="text-align:center; font-size:0.9rem; color:#64748b; margin:0.5em 0;">
                테토 점수: {score}/{NUM_QUESTIONS}
            </div>
            """, unsafe_allow_html=True)

            if not st.session_state.teto_saved:
                user_info = {"city": "성남시", "gender": "미상", "age_group": "미상"}
                save_to_mongodb(result_key, r['desc'], user_info)
                st.session_state.teto_saved = True

            if st.button("다시 테스트하기", use_container_width=True):
                st.session_state.teto_started = False
                st.session_state.teto_q = 0
                st.session_state.teto_ans = []
                st.session_state.teto_done = False
                st.session_state.teto_saved = False
                st.rerun()

    with tab2:
        st.markdown("### 📊 성남시 테토에겐 통계")
        if st.button("통계 새로고침", type="primary"):
            st.rerun()
        _, seongnam_results = get_statistics()
        nam_count = {"테토남": 0, "에겐남": 0}
        nyeo_count = {"테토녀": 0, "에겐녀": 0}
        for item in seongnam_results:
            if item["_id"] in nam_count:
                nam_count[item["_id"]] = item["count"]
            elif item["_id"] in nyeo_count:
                nyeo_count[item["_id"]] = item["count"]
        total_nam = sum(nam_count.values())
        total_nyeo = sum(nyeo_count.values())

        st.markdown("#### 🔥 테토남 vs 🧊 에겐남")
        if total_nam > 0:
            left_pct = int(round(nam_count["테토남"] / total_nam * 100))
            right_pct = 100 - left_pct
            st.markdown(f"""
            <div class="stat-bar-wrap">
                <div class="stat-bar-label"><span style="color:#EF4444;">테토남</span><span style="color:#3B82F6;">에겐남</span></div>
                <div class="stat-bar-bg">
                    <div class="stat-bar-left" style="width:{left_pct}%; background:linear-gradient(90deg,#EF4444,#F97316);"></div>
                    <div class="stat-bar-right" style="width:{right_pct}%; background:linear-gradient(90deg,#3B82F6,#8B5CF6);"></div>
                    <div class="stat-bar-text">{left_pct}% : {right_pct}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("아직 남성 데이터가 없습니다.")

        st.markdown("#### ✨ 테토녀 vs 🌙 에겐녀")
        if total_nyeo > 0:
            left_pct = int(round(nyeo_count["테토녀"] / total_nyeo * 100))
            right_pct = 100 - left_pct
            st.markdown(f"""
            <div class="stat-bar-wrap">
                <div class="stat-bar-label"><span style="color:#EC4899;">테토녀</span><span style="color:#8B5CF6;">에겐녀</span></div>
                <div class="stat-bar-bg">
                    <div class="stat-bar-left" style="width:{left_pct}%; background:linear-gradient(90deg,#EC4899,#F59E0B);"></div>
                    <div class="stat-bar-right" style="width:{right_pct}%; background:linear-gradient(90deg,#8B5CF6,#06B6D4);"></div>
                    <div class="stat-bar-text">{left_pct}% : {right_pct}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("아직 여성 데이터가 없습니다.")

if __name__ == "__main__":
    run()
