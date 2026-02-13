import streamlit as st

def run():
    # 12문항 시나리오형 MBTI 질문 (차원당 3문항, A/B 이지선다)
    QUESTIONS = [
        # E/I
        {
            "situation": "회사 회식 자리에서 나는...",
            "A": "분위기 메이커! 건배사부터 2차 장소 섭외까지 내가 다 함",
            "B": "조용히 옆자리 한 명이랑 깊은 얘기 나누는 게 최고",
            "dim": ("E", "I")
        },
        {
            "situation": "주말에 갑자기 하루가 비었다!",
            "A": "바로 카톡 단톡방에 '오늘 누구 놀 사람?' 폭격",
            "B": "드디어 나만의 시간... 넷플릭스 + 배달앱 = 천국",
            "dim": ("E", "I")
        },
        {
            "situation": "새 팀에 배정받은 첫날...",
            "A": "점심시간에 먼저 말 걸고 커피 한 잔 어때요? 시전",
            "B": "일단 분위기 파악하고 천천히 한 명씩 친해지는 스타일",
            "dim": ("E", "I")
        },
        # S/N
        {
            "situation": "친구가 '우리 여행 가자!' 했을 때 나는...",
            "A": "바로 항공권 가격 비교하고 숙소 후기 검색 시작",
            "B": "'거기 가면 이런 것도 하고 저런 것도 하고~' 상상 먼저",
            "dim": ("S", "N")
        },
        {
            "situation": "새 프로젝트 브리핑을 받을 때...",
            "A": "일정, 예산, 담당자부터 확인. 구체적인 게 좋아",
            "B": "큰 그림이 뭔지, 이걸 왜 하는지 맥락이 먼저 궁금함",
            "dim": ("S", "N")
        },
        {
            "situation": "맛집을 고를 때 나는...",
            "A": "별점 4.5 이상, 후기 500개 이상, 검증된 곳만 감",
            "B": "분위기 좋아 보이는 데, 한번 모험해볼까? 감으로 고름",
            "dim": ("S", "N")
        },
        # T/F
        {
            "situation": "친구가 '나 시험 망했어...' 라고 할 때",
            "A": "'몇 점인데? 다음엔 이렇게 공부해봐' 해결책 제시",
            "B": "'에이 힘들었겠다... 맛있는 거 먹으러 가자' 공감 먼저",
            "dim": ("T", "F")
        },
        {
            "situation": "팀 회의에서 의견 충돌이 생겼다!",
            "A": "데이터랑 근거 들고 와서 논리적으로 설득함",
            "B": "모두의 의견을 들어보고 분위기가 안 상하게 조율함",
            "dim": ("T", "F")
        },
        {
            "situation": "후배가 실수를 반복할 때...",
            "A": "정확히 뭐가 문제인지 팩트 위주로 짚어줌",
            "B": "기분 상하지 않게 돌려서 말하거나 같이 해결해줌",
            "dim": ("T", "F")
        },
        # J/P
        {
            "situation": "여행 갈 때 나의 스타일은?",
            "A": "출발 2주 전부터 시간대별 일정표 완성! 맛집도 예약 끝",
            "B": "비행기랑 숙소만 잡고 나머지는 현지에서 즉흥으로~",
            "dim": ("J", "P")
        },
        {
            "situation": "시험 or 마감이 다가올 때...",
            "A": "일찍부터 조금씩 나눠서 준비해둠. 밀리면 불안",
            "B": "마감 직전에 몰아서 하면 오히려 집중력 폭발함",
            "dim": ("J", "P")
        },
        {
            "situation": "오늘 할 일이 5개쯤 있을 때...",
            "A": "체크리스트 쓰고 하나씩 완료 표시하는 그 쾌감",
            "B": "일단 하고 싶은 거부터! 리스트는 만들어도 안 봄",
            "dim": ("J", "P")
        },
    ]

    MBTI_INFO = {
        "ISTJ": {
            "emoji": "📋",
            "nickname": "생활 루틴의 제왕",
            "desc": "계획표 없으면 불안한 당신! 약속 시간 10분 전 도착은 기본이고, 정리정돈은 거의 본능 수준. 믿음직한 인간 달력이자 조직의 버팀목.",
            "vibe": "매일 같은 카페, 같은 메뉴, 그게 나의 안식처",
            "good": ["ESFP", "ESTP"],
            "bad": ["ENFP", "ENTP"],
            "color": "#3B82F6"
        },
        "ISFJ": {
            "emoji": "🫶",
            "nickname": "팀의 숨은 히어로",
            "desc": "남들 안 챙기는 걸 챙기는 세심함의 끝판왕. 조용하지만 당신이 없으면 모든 게 무너짐. 따뜻한 마음으로 주변을 지키는 수호천사형.",
            "vibe": "별말 안 했는데 내가 좋아하는 음료를 기억해주는 사람",
            "good": ["ESFP", "ESTP"],
            "bad": ["ENTP", "ENFP"],
            "color": "#EC4899"
        },
        "INFJ": {
            "emoji": "🔮",
            "nickname": "인간 독심술사",
            "desc": "말 안 해도 상대방 기분을 읽는 초능력자. 겉은 조용하지만 속은 이상과 신념으로 가득 찬 깊은 우물 같은 사람. 통찰력 만렙.",
            "vibe": "카페 구석 자리에서 인류의 미래를 고민하는 중",
            "good": ["ENFP", "ENTP"],
            "bad": ["ESTP", "ESFP"],
            "color": "#8B5CF6"
        },
        "INTJ": {
            "emoji": "🧠",
            "nickname": "혼자서 다 하는 전략가",
            "desc": "머릿속에 이미 3수 앞까지 계산 끝난 체스 마스터. 비효율을 참지 못하고, 혼자 일하는 게 제일 빠름. 쿨한 겉모습 속 완벽주의자.",
            "vibe": "회의 5분 만에 핵심 파악하고 해결책까지 제시 완료",
            "good": ["ENFP", "ENTP"],
            "bad": ["ESFP", "ESTP"],
            "color": "#1E293B"
        },
        "ISTP": {
            "emoji": "🛠️",
            "nickname": "쿨한 해결사",
            "desc": "말보다 행동이 앞서는 실전형 인간. 위기 상황에서 오히려 빛나고, 쓸데없는 감정 소모는 노땡큐. 필요할 때 딱 나타나는 해결사.",
            "vibe": "말수 적지만 일 처리는 누구보다 빠른 사람",
            "good": ["ESFJ", "ENFJ"],
            "bad": ["ENFP", "ENTP"],
            "color": "#64748B"
        },
        "ISFP": {
            "emoji": "🎨",
            "nickname": "감성 자유영혼",
            "desc": "남들 눈치 안 보고 내 취향대로 사는 진정한 자유인. 예술적 감각이 뛰어나고, 조용하지만 자기만의 세계가 확실한 감성 충만형.",
            "vibe": "플레이리스트가 곧 내 인생 자서전",
            "good": ["ESFJ", "ENFJ"],
            "bad": ["ENTJ", "ESTJ"],
            "color": "#F59E0B"
        },
        "INFP": {
            "emoji": "🌙",
            "nickname": "몽상가 이상주의자",
            "desc": "현실은 현실이고 내 머릿속엔 또 다른 세계가 있음. 감정이 풍부하고 공감 능력 만렙. 상상력으로 세상을 바꾸고 싶은 순수한 영혼.",
            "vibe": "버스 창밖 보면서 단편 소설 한 편 뚝딱 구상 중",
            "good": ["ENFJ", "ENTJ"],
            "bad": ["ESTJ", "ESFJ"],
            "color": "#A78BFA"
        },
        "INTP": {
            "emoji": "💡",
            "nickname": "생각이 멈추지 않는 분석가",
            "desc": "쓸데없는 것까지 '왜?'를 달고 사는 탐구왕. 관심 분야 파면 밤새 위키피디아 서핑은 기본. 논리적 사고의 끝판왕이지만 현실 감각은 가끔 미아.",
            "vibe": "샤워하다가 갑자기 우주의 원리가 궁금해진 사람",
            "good": ["ENTJ", "ENFJ"],
            "bad": ["ESFJ", "ESTJ"],
            "color": "#06B6D4"
        },
        "ESTP": {
            "emoji": "🔥",
            "nickname": "액션 히어로 본능형",
            "desc": "생각보다 몸이 먼저 나가는 행동대장. 스릴을 즐기고, 어떤 상황에서도 당황하지 않는 타고난 적응력의 소유자. 인생은 즐기는 거야!",
            "vibe": "번지점프? 당연히 첫 번째로 뛰어내리지",
            "good": ["ISFJ", "ISTJ"],
            "bad": ["INFJ", "INFP"],
            "color": "#EF4444"
        },
        "ESFP": {
            "emoji": "🎉",
            "nickname": "분위기 메이커 만렙",
            "desc": "이 사람만 오면 모임 텐션이 200% 올라감. 지금 이 순간을 최대한 즐기는 천생 엔터테이너. 주변에 웃음이 끊이지 않는 에너지 뱅크.",
            "vibe": "노래방 가면 마이크 놓을 줄 모르는 사람",
            "good": ["ISFJ", "ISTJ"],
            "bad": ["INFJ", "INTJ"],
            "color": "#F97316"
        },
        "ENFP": {
            "emoji": "🦋",
            "nickname": "텐션 만렙 아이디어 뱅크",
            "desc": "5분마다 새로운 아이디어가 폭발하는 창의력 대장. 사람 만나는 걸 좋아하고, 열정 하나만큼은 우주 끝까지 가는 긍정 에너지 폭발형.",
            "vibe": "새벽 3시에 갑자기 사업 아이디어 떠올라서 메모하는 중",
            "good": ["INFJ", "INTJ"],
            "bad": ["ISTJ", "ISFJ"],
            "color": "#10B981"
        },
        "ENTP": {
            "emoji": "⚡",
            "nickname": "논쟁 마스터 혁신가",
            "desc": "토론이 취미이자 특기인 말빨 끝판왕. 남들이 안 된다고 하면 오히려 더 불타오르는 반골 기질. 새로운 걸 만드는 데 천부적 재능.",
            "vibe": "악마의 변호인 역할을 너무 재밌게 하는 사람",
            "good": ["INFJ", "INTJ"],
            "bad": ["ISFJ", "ISTJ"],
            "color": "#FBBF24"
        },
        "ESTJ": {
            "emoji": "👔",
            "nickname": "조직의 든든한 기둥",
            "desc": "효율과 체계를 사랑하는 타고난 리더. '이건 이렇게 해야 돼'가 입버릇. 책임감 하나로 조직을 이끄는 현실 세계의 보스.",
            "vibe": "팀 프로젝트에서 자연스럽게 리더가 되어있는 사람",
            "good": ["ISFP", "INFP"],
            "bad": ["INFP", "ENFP"],
            "color": "#334155"
        },
        "ESFJ": {
            "emoji": "🤗",
            "nickname": "인간관계 만렙 케어형",
            "desc": "주변 사람들 챙기는 게 본능인 천생 인싸. 생일 절대 안 까먹고, 모임 후기 올리는 것도 당연히 내 몫. 모두의 엄마/아빠 같은 존재.",
            "vibe": "단톡방에서 공지 올리고 출석 체크하는 총무",
            "good": ["ISFP", "INFP"],
            "bad": ["INTP", "ISTP"],
            "color": "#FB7185"
        },
        "ENFJ": {
            "emoji": "🌟",
            "nickname": "타고난 인플루언서",
            "desc": "말 한마디로 사람 마음을 움직이는 카리스마의 소유자. 남 돕는 게 행복이고, 팀의 분위기를 이끄는 자연스러운 리더. 공감 + 실행력 겸비.",
            "vibe": "후배 고민 상담하다 보면 새벽 2시인 사람",
            "good": ["INFP", "ISFP"],
            "bad": ["ISTP", "INTP"],
            "color": "#7C3AED"
        },
        "ENTJ": {
            "emoji": "🦅",
            "nickname": "CEO형 빌런 리더",
            "desc": "목표가 생기면 무조건 달성하는 추진력 괴물. 전략적 사고 + 실행력 조합으로 어디서든 리더가 됨. 비효율을 참지 못하는 완벽주의자.",
            "vibe": "신입인데 벌써 업무 프로세스 개선안 제출한 사람",
            "good": ["INTP", "INFP"],
            "bad": ["ISFP", "INFP"],
            "color": "#0F172A"
        },
    }

    NUM_QUESTIONS = len(QUESTIONS)

    # 세션 상태 초기화
    if "mbti_answers" not in st.session_state:
        st.session_state.mbti_answers = [None] * NUM_QUESTIONS
    if "mbti_step" not in st.session_state:
        st.session_state.mbti_step = 0
    if "mbti_done" not in st.session_state:
        st.session_state.mbti_done = False

    # CSS
    st.markdown("""
    <style>
    .mbti-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: 0.2em;
        background: linear-gradient(135deg, #7c3aed, #ec4899, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .mbti-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2em;
    }
    .situation-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(236,72,153,0.08));
        border: 1px solid rgba(124,58,237,0.25);
        border-radius: 20px;
        padding: 2em 1.5em;
        margin: 1em 0;
        animation: slideUp 0.5s ease-out;
    }
    .situation-label {
        font-size: 0.85rem;
        color: #a78bfa;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5em;
    }
    .situation-text {
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 0.3em;
    }
    .progress-container {
        display: flex;
        align-items: center;
        gap: 0.8em;
        margin: 1.5em 0;
    }
    .progress-bar-bg {
        flex: 1;
        height: 8px;
        background: rgba(148,163,184,0.2);
        border-radius: 4px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #7c3aed, #ec4899);
        transition: width 0.4s ease;
    }
    .progress-text {
        font-size: 0.9rem;
        font-weight: 700;
        color: #a78bfa;
        min-width: 3em;
        text-align: right;
    }
    .result-hero {
        text-align: center;
        padding: 2em 1em;
        animation: slideUp 0.6s ease-out;
    }
    .result-emoji {
        font-size: 4rem;
        margin-bottom: 0.2em;
    }
    .result-type {
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: 0.05em;
        margin-bottom: 0.1em;
    }
    .result-nickname {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5em;
    }
    .result-card {
        border-radius: 20px;
        padding: 1.5em;
        margin: 1em 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .result-vibe {
        font-style: italic;
        font-size: 1.05rem;
        color: #94a3b8;
        text-align: center;
        margin: 1em 0;
        padding: 1em;
        border-radius: 12px;
        background: rgba(148,163,184,0.08);
    }
    .compat-section {
        display: flex;
        gap: 1em;
        margin-top: 1em;
    }
    .compat-card {
        flex: 1;
        padding: 1em;
        border-radius: 14px;
        text-align: center;
    }
    .compat-good {
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.3);
    }
    .compat-bad {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.3);
    }
    .compat-label {
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.3em;
    }
    .compat-types {
        font-size: 1.1rem;
        font-weight: 800;
    }
    .dim-bar-row {
        display: flex;
        align-items: center;
        margin: 0.6em 0;
        gap: 0.5em;
    }
    .dim-label {
        font-size: 1rem;
        font-weight: 800;
        width: 2em;
        text-align: center;
    }
    .dim-bar-bg {
        flex: 1;
        height: 28px;
        background: rgba(148,163,184,0.15);
        border-radius: 14px;
        overflow: hidden;
        position: relative;
    }
    .dim-bar-fill {
        height: 100%;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 0.8em;
        font-size: 0.85rem;
        font-weight: 700;
        color: #fff;
        transition: width 0.6s ease;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(24px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # 결과 화면
    if st.session_state.mbti_done:
        answers = st.session_state.mbti_answers
        scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        for i, q in enumerate(QUESTIONS):
            chosen = answers[i]
            if chosen == 0:
                scores[q["dim"][0]] += 1
            else:
                scores[q["dim"][1]] += 1

        mbti = ""
        mbti += "E" if scores["E"] >= scores["I"] else "I"
        mbti += "S" if scores["S"] >= scores["N"] else "N"
        mbti += "T" if scores["T"] >= scores["F"] else "F"
        mbti += "J" if scores["J"] >= scores["P"] else "P"

        info = MBTI_INFO[mbti]
        pairs = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]

        st.markdown(f"""
        <div class="result-hero">
            <div class="result-emoji">{info['emoji']}</div>
            <div class="result-type" style="color:{info['color']}">{mbti}</div>
            <div class="result-nickname" style="color:{info['color']}">{info['nickname']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card" style="background: linear-gradient(135deg, {info['color']}15, {info['color']}08);">
            <div style="font-size:1.1rem; line-height:1.7;">{info['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-vibe">"{info['vibe']}"</div>
        """, unsafe_allow_html=True)

        # 차원별 비율 바
        st.markdown("#### 나의 성향 비율")
        for t1, t2 in pairs:
            total = scores[t1] + scores[t2]
            if total == 0:
                pct1 = 50
            else:
                pct1 = int(round(scores[t1] / total * 100))
            pct2 = 100 - pct1
            c1 = "#7c3aed" if pct1 >= pct2 else "rgba(148,163,184,0.4)"
            c2 = "#ec4899" if pct2 > pct1 else "rgba(148,163,184,0.4)"
            st.markdown(f"""
            <div class="dim-bar-row">
                <div class="dim-label" style="color:{c1}">{t1}</div>
                <div class="dim-bar-bg">
                    <div class="dim-bar-fill" style="width:{pct1}%; background:{c1};">{pct1}%</div>
                </div>
                <div class="dim-bar-bg">
                    <div class="dim-bar-fill" style="width:{pct2}%; background:{c2};">{pct2}%</div>
                </div>
                <div class="dim-label" style="color:{c2}">{t2}</div>
            </div>
            """, unsafe_allow_html=True)

        # 궁합
        st.markdown(f"""
        <div class="compat-section">
            <div class="compat-card compat-good">
                <div class="compat-label" style="color:#10b981;">찰떡궁합 💚</div>
                <div class="compat-types" style="color:#10b981;">{', '.join(info['good'])}</div>
            </div>
            <div class="compat-card compat-bad">
                <div class="compat-label" style="color:#ef4444;">환장궁합 💔</div>
                <div class="compat-types" style="color:#ef4444;">{', '.join(info['bad'])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("다시 검사하기", use_container_width=True):
            st.session_state.mbti_answers = [None] * NUM_QUESTIONS
            st.session_state.mbti_step = 0
            st.session_state.mbti_done = False
            st.rerun()
        return

    # 테스트 진행 화면
    st.markdown('<div class="mbti-title">MBTI 시나리오 테스트</div>', unsafe_allow_html=True)
    st.markdown('<div class="mbti-subtitle">12개 상황, 직감으로 골라주세요!</div>', unsafe_allow_html=True)

    idx = st.session_state.mbti_step
    q = QUESTIONS[idx]
    pct = int((idx / NUM_QUESTIONS) * 100)

    # 프로그레스 바
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{pct}%"></div>
        </div>
        <div class="progress-text">{idx+1}/{NUM_QUESTIONS}</div>
    </div>
    """, unsafe_allow_html=True)

    # 질문 카드
    st.markdown(f"""
    <div class="situation-card">
        <div class="situation-label">SITUATION {idx+1}</div>
        <div class="situation-text">{q['situation']}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if st.button(f"A. {q['A']}", key=f"mbti_a_{idx}", use_container_width=True):
            st.session_state.mbti_answers[idx] = 0
            if idx < NUM_QUESTIONS - 1:
                st.session_state.mbti_step = idx + 1
            else:
                st.session_state.mbti_done = True
            st.rerun()
    with col2:
        if st.button(f"B. {q['B']}", key=f"mbti_b_{idx}", use_container_width=True):
            st.session_state.mbti_answers[idx] = 1
            if idx < NUM_QUESTIONS - 1:
                st.session_state.mbti_step = idx + 1
            else:
                st.session_state.mbti_done = True
            st.rerun()

    # 이전 버튼
    if idx > 0:
        if st.button("← 이전", key="mbti_prev"):
            st.session_state.mbti_step = idx - 1
            st.rerun()
