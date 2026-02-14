import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from mongo_env import get_mongo_uri, get_collection


# Keep all 11 questions as-is (verbatim).
QUESTIONS = [
    {
        "question": "친구들과 만날 때 나는...",
        "options": [
            "활발하게 대화를 이끌어가는 편이다",
            "조용히 듣고 있다가 적절한 타이밍에 말한다",
        ],
    },
    {
        "question": "새로운 사람을 만날 때...",
        "options": [
            "먼저 다가가서 인사를 건넨다",
            "상대방이 먼저 다가올 때까지 기다린다",
        ],
    },
    {
        "question": "문제가 생겼을 때 나는...",
        "options": [
            "즉시 해결책을 찾으려고 노력한다",
            "차분히 상황을 파악한 후 대응한다",
        ],
    },
    {
        "question": "여가 시간에 나는...",
        "options": [
            "새로운 활동이나 취미를 시도한다",
            "편안하고 익숙한 활동을 즐긴다",
        ],
    },
    {
        "question": "감정 표현에 대해...",
        "options": [
            "솔직하게 감정을 표현하는 편이다",
            "감정을 조절해서 표현한다",
        ],
    },
    {
        "question": "계획을 세울 때...",
        "options": [
            "즉흥적으로 행동하는 편이다",
            "미리 계획을 세우고 실행한다",
        ],
    },
    {
        "question": "스트레스 상황에서...",
        "options": [
            "다른 사람과 이야기하며 해소한다",
            "혼자만의 시간을 가지며 해소한다",
        ],
    },
    {
        "question": "의사결정을 할 때...",
        "options": [
            "직감과 감정에 따라 결정한다",
            "논리적 분석 후 결정한다",
        ],
    },
    {
        "question": "연인과의 갈등이 생겼을 때 나는...",
        "options": [
            "바로 대화를 시도하며 감정을 솔직하게 표현한다",
            "잠시 시간을 갖고 차분히 생각한 뒤 조심스럽게 이야기한다",
        ],
    },
    {
        "question": "데이트 약속이 갑자기 취소되면...",
        "options": [
            "아쉬워서 바로 다른 계획을 세운다",
            "혼자만의 시간을 즐기며 여유를 갖는다",
        ],
    },
    {
        "question": "연인에게 서프라이즈 이벤트를...",
        "options": [
            "자주 준비하며 감동을 주고 싶어 한다",
            "특별한 날에만 신중하게 준비한다",
        ],
    },
]


RESULT_META = {
    "테토남": {
        "emoji": "🔥",
        "gradient": "linear-gradient(90deg, #75e8ff 0%, #ff77e6 100%)",
        "glow": "rgba(255, 119, 230, 0.25)",
    },
    "에겐남": {
        "emoji": "🧊",
        "gradient": "linear-gradient(90deg, #75e8ff 0%, #8b5cf6 100%)",
        "glow": "rgba(117, 232, 255, 0.22)",
    },
    "테토녀": {
        "emoji": "✨",
        "gradient": "linear-gradient(90deg, #ff77e6 0%, #75e8ff 100%)",
        "glow": "rgba(117, 232, 255, 0.18)",
    },
    "에겐녀": {
        "emoji": "🌙",
        "gradient": "linear-gradient(90deg, #ff77e6 0%, #371569 100%)",
        "glow": "rgba(55, 21, 105, 0.35)",
    },
}


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        :root{
            --bg0: #070a1b;
            --bg1: #0c1242;
            --bg2: #371569;
            --cyan: #75e8ff;
            --pink: #ff77e6;
            --glass: rgba(255,255,255,0.08);
            --glass2: rgba(255,255,255,0.06);
            --stroke: rgba(255,255,255,0.16);
            --text: rgba(245,248,255,0.92);
            --muted: rgba(245,248,255,0.70);
            --shadow: rgba(0,0,0,0.35);
        }

        html, body, [data-testid="stAppViewContainer"]{
            background: radial-gradient(1200px 600px at 15% 10%, rgba(117,232,255,0.20), transparent 60%),
                        radial-gradient(900px 500px at 85% 15%, rgba(255,119,230,0.18), transparent 55%),
                        linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 55%, var(--bg0) 100%) !important;
            color: var(--text) !important;
        }
        [data-testid="stHeader"]{ background: transparent !important; }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div{
            color: var(--text);
        }
        a { color: var(--cyan) !important; }

        @keyframes fadeIn { from {opacity:0;} to {opacity:1;} }
        @keyframes slideUp { from {opacity:0; transform: translateY(22px);} to {opacity:1; transform: translateY(0);} }
        @keyframes pulse { 0% {transform: translateY(0) scale(1);} 55% {transform: translateY(-2px) scale(1.012);} 100% {transform: translateY(0) scale(1);} }
        .anim-fadeIn{ animation: fadeIn .55s ease-out both; }
        .anim-slideUp{ animation: slideUp .60s cubic-bezier(0.2, 0.9, 0.2, 1) both; }

        .glass-card{
            background: linear-gradient(180deg, var(--glass), var(--glass2));
            border: 1px solid var(--stroke);
            box-shadow: 0 14px 40px var(--shadow);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 22px;
        }
        .hero{ padding: 1.25rem 1.35rem 1.1rem 1.35rem; }
        .hero-title{
            font-size: 2.1rem;
            letter-spacing: -0.02em;
            font-weight: 800;
            margin: 0 0 .4rem 0;
        }
        .hero-title span{
            background: linear-gradient(90deg, var(--cyan), var(--pink));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .hero-sub{
            font-size: 1.05rem;
            line-height: 1.55;
            color: var(--muted);
            margin: 0;
        }
        .pill-row{
            display:flex;
            gap: .5rem;
            flex-wrap: wrap;
            margin-top: .9rem;
        }
        .pill{
            padding: .38rem .62rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(255,255,255,0.05);
            font-size: .92rem;
            color: rgba(245,248,255,0.82);
        }

        .q-wrap{ margin-top: .3rem; padding: 1.15rem 1.25rem; }
        .q-top{
            display:flex;
            align-items:center;
            justify-content: space-between;
            gap: .75rem;
            margin-bottom: .75rem;
        }
        .q-count{
            font-weight: 700;
            color: rgba(245,248,255,0.86);
            letter-spacing: .02em;
        }
        .q-hint{ font-size: .95rem; color: var(--muted); }
        .q-text{
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.015em;
            margin: .2rem 0 1rem 0;
        }

        div[data-testid="stProgress"] > div{
            background: rgba(255,255,255,0.08) !important;
            border-radius: 999px !important;
            height: 12px !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            overflow: hidden !important;
        }
        div[data-testid="stProgress"] div[role="progressbar"]{
            background: linear-gradient(90deg, var(--cyan), var(--pink)) !important;
            border-radius: 999px !important;
        }

        .opt-shell{ margin-top: .25rem; }
        .opt-shell div[data-testid="stButton"] > button{
            width: 100% !important;
            padding: 1.05rem 1.05rem !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            background: rgba(255,255,255,0.06) !important;
            color: rgba(245,248,255,0.95) !important;
            box-shadow: 0 12px 30px rgba(0,0,0,0.25) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
            text-align: left !important;
            line-height: 1.35 !important;
            font-weight: 750 !important;
            letter-spacing: -0.01em;
            min-height: 76px;
        }
        .opt-shell div[data-testid="stButton"] > button:hover{
            transform: translateY(-2px);
            box-shadow: 0 18px 42px rgba(0,0,0,0.35) !important;
            border-color: rgba(117,232,255,0.35) !important;
            animation: pulse 1.0s ease-in-out infinite;
        }
        .opt-a div[data-testid="stButton"] > button{
            background: linear-gradient(135deg, rgba(117,232,255,0.22), rgba(12,18,66,0.45)) !important;
        }
        .opt-b div[data-testid="stButton"] > button{
            background: linear-gradient(135deg, rgba(255,119,230,0.22), rgba(55,21,105,0.52)) !important;
        }

        .soft-btn div[data-testid="stButton"] > button{
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            background: rgba(255,255,255,0.06) !important;
            color: rgba(245,248,255,0.92) !important;
            transition: transform .16s ease, border-color .16s ease;
        }
        .soft-btn div[data-testid="stButton"] > button:hover{
            transform: translateY(-1px);
            border-color: rgba(255,119,230,0.35) !important;
        }

        .modal-title{
            font-size: 2.0rem;
            font-weight: 900;
            letter-spacing: -0.02em;
            margin: 0;
            line-height: 1.15;
        }
        .modal-title .grad{
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .modal-kicker{
            margin: .25rem 0 .7rem 0;
            color: rgba(245,248,255,0.74);
            font-size: 1.02rem;
        }
        .modal-desc{
            margin-top: .75rem;
            color: rgba(245,248,255,0.90);
            font-size: 1.03rem;
            line-height: 1.65;
        }
        .modal-desc b{ color: rgba(245,248,255,0.98); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_state() -> None:
    defaults = {
        "test_started": False,
        "current_question": 0,
        "answers": [],
        "test_completed": False,
        "result_saved": False,
        "save_message": "",
        "result": None,
        "description": None,
        "show_result_modal": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _calculate_result(answers: list[int]) -> tuple[str, str]:
    teto_score = answers.count(0)

    # Keep the same mapping logic:
    # 7~11: 테토남, 5~6: 에겐남, 3~4: 테토녀, 0~2: 에겐녀
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

    return result, description


@st.dialog("테토에겐 결과", width="large")
def _show_teto_result_dialog():
    rtype = st.session_state.result
    meta = RESULT_META.get(rtype, RESULT_META["에겐남"])

    st.markdown(
        f"""
        <div class="modal-kicker">당신의 유형</div>
        <h2 class="modal-title">{meta["emoji"]} <span class="grad" style="background:{meta["gradient"]};">{rtype}</span></h2>
        <div class="modal-kicker" style="margin-top:.35rem;">테토에겐 테스트 결과</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="margin-top:.7rem; padding: .75rem .9rem; border-radius: 18px;
                    border: 1px solid rgba(255,255,255,0.14);
                    background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
                    box-shadow: 0 18px 60px {meta["glow"]};">
          <div class="modal-desc">{st.session_state.description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("닫기", key="close_teto_dialog", use_container_width=True):
        st.session_state.show_result_modal = False
        st.rerun()


def run():
    # Keep importing from mongo_env + keep MongoDB save logic
    mongo_uri = get_mongo_uri()
    if not mongo_uri:
        st.error("MongoDB 연결 정보(MONGODB_URI)가 설정되어 있지 않습니다.")
        st.info("로컬: `.env` 설정 / 배포: Streamlit Secrets 설정을 추가하세요.")
        return

    def save_to_mongodb(result_type: str, description: str, user_info: dict) -> bool:
        try:
            collection = get_collection("automation_db", "inspection_records")
            if collection is None:
                st.error("MongoDB 연결에 실패했습니다.")
                return False

            data = {
                "result_type": result_type,
                "description": description,
                "user_info": user_info,
                "created_at": datetime.now(),
                "city": user_info.get("city", "성남시"),
                "source": "테토에겐",
            }
            collection.insert_one(data)
            return True
        except Exception as e:
            st.error(f"데이터 저장 중 오류: {e}")
            return False

    def get_statistics_seongnam() -> list[dict]:
        try:
            collection = get_collection("automation_db", "inspection_records")
            if collection is None:
                return []

            pipeline = [
                {"$match": {"city": "성남시", "source": "테토에겐"}},
                {"$group": {"_id": "$result_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            return list(collection.aggregate(pipeline))
        except Exception as e:
            st.error(f"통계 조회 중 오류: {e}")
            return []

    _inject_css()
    _init_state()

    st.markdown(
        """
        <div class="glass-card hero anim-fadeIn">
          <div class="hero-title">🎭 <span>테토에겐 테스트</span></div>
          <p class="hero-sub">당신은 <b>테토남</b>, <b>에겐남</b>, <b>테토녀</b>, <b>에겐녀</b> 중 누구일까요?<br>
          11개의 질문에서 더 나와 비슷한 쪽을 선택하세요.</p>
          <div class="pill-row">
            <div class="pill">그라데이션</div>
            <div class="pill">글래스모피즘</div>
            <div class="pill">질문 애니메이션</div>
            <div class="pill">모달 결과</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🧪 테스트", "📊 통계"])

    with tab1:
        if not st.session_state.test_started:
            st.markdown(
                """
                <div class="glass-card q-wrap anim-slideUp" style="margin-top: 1.0rem;">
                  <div class="q-text" style="margin:0 0 .65rem 0;">테스트 안내</div>
                  <div class="q-hint">각 문항에서 A/B 중 하나를 선택하면 다음 질문으로 넘어갑니다. 이전으로 돌아가 답변을 수정할 수도 있어요.</div>
                  <div class="pill-row" style="margin-top: .85rem;">
                    <div class="pill"><b>테토남</b>: 활발하고 외향적인 남성형</div>
                    <div class="pill"><b>에겐남</b>: 차분하고 내향적인 남성형</div>
                    <div class="pill"><b>테토녀</b>: 활발하고 외향적인 여성형</div>
                    <div class="pill"><b>에겐녀</b>: 차분하고 내향적인 여성형</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("테스트 시작", type="primary", use_container_width=True):
                st.session_state.test_started = True
                st.rerun()

        elif (not st.session_state.test_completed) and st.session_state.current_question < len(QUESTIONS):
            q_idx = int(st.session_state.current_question)
            q = QUESTIONS[q_idx]

            st.progress(q_idx / len(QUESTIONS))

            st.markdown(
                f"""
                <div class="glass-card q-wrap anim-slideUp">
                  <div class="q-top">
                    <div class="q-count">Q {q_idx+1} / {len(QUESTIONS)}</div>
                    <div class="q-hint">더 가까운 쪽을 고르세요</div>
                  </div>
                  <div class="q-text anim-fadeIn">{q_idx+1}. {q["question"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.markdown('<div class="opt-shell opt-a anim-fadeIn">', unsafe_allow_html=True)
                clicked_a = st.button(
                    f"A  {q['options'][0]}",
                    key=f"teto_btn_{q_idx}_0",
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
                if clicked_a:
                    st.session_state.answers.append(0)
                    st.session_state.current_question += 1
                    st.rerun()

            with col2:
                st.markdown('<div class="opt-shell opt-b anim-fadeIn">', unsafe_allow_html=True)
                clicked_b = st.button(
                    f"B  {q['options'][1]}",
                    key=f"teto_btn_{q_idx}_1",
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
                if clicked_b:
                    st.session_state.answers.append(1)
                    st.session_state.current_question += 1
                    st.rerun()

            if st.session_state.current_question > 0:
                st.markdown('<div class="soft-btn" style="margin-top: .8rem;">', unsafe_allow_html=True)
                if st.button("이전", use_container_width=True):
                    st.session_state.current_question -= 1
                    if st.session_state.answers:
                        st.session_state.answers.pop()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            if not st.session_state.test_completed:
                st.session_state.test_completed = True
                result, description = _calculate_result(st.session_state.answers)
                st.session_state.result = result
                st.session_state.description = description
                st.session_state.show_result_modal = True

            if (
                (not st.session_state.result_saved)
                and st.session_state.result
                and st.session_state.description
            ):
                user_info = {"city": "성남시", "gender": "미상", "age_group": "미상"}
                ok = save_to_mongodb(st.session_state.result, st.session_state.description, user_info)
                st.session_state.save_message = "✅ 결과가 성공적으로 저장되었습니다!" if ok else "⚠️ 결과 저장에 실패했습니다."
                st.session_state.result_saved = True

            st.markdown(
                """
                <div class="glass-card q-wrap anim-slideUp" style="margin-top: 1.0rem;">
                  <div class="q-text" style="margin:0 0 .55rem 0;">테스트 완료</div>
                  <div class="q-hint">결과는 팝업(모달)로 표시됩니다. 닫은 뒤 다시 테스트할 수도 있어요.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.session_state.get("save_message"):
                st.info(st.session_state.save_message)

            st.markdown('<div class="soft-btn" style="margin-top: .8rem;">', unsafe_allow_html=True)
            if st.button("다시 테스트", use_container_width=True):
                st.session_state.test_started = False
                st.session_state.current_question = 0
                st.session_state.answers = []
                st.session_state.test_completed = False
                st.session_state.result_saved = False
                st.session_state.save_message = ""
                st.session_state.result = None
                st.session_state.description = None
                st.session_state.show_result_modal = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Show result dialog
        if st.session_state.get("show_result_modal") and st.session_state.get("result"):
            _show_teto_result_dialog()

    with tab2:
        st.markdown(
            """
            <div class="glass-card q-wrap anim-slideUp" style="margin-top: .8rem;">
              <div class="q-text" style="margin:0 0 .4rem 0;">성남시 유형 분포</div>
              <div class="q-hint">4가지 유형을 <b>전체 합계 대비 퍼센트</b>로 계산합니다 (합계 100%).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="soft-btn" style="margin-top: .7rem;">', unsafe_allow_html=True)
        if st.button("통계 새로고침", type="primary", use_container_width=True):
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        raw = get_statistics_seongnam()
        type_order = ["테토남", "에겐남", "테토녀", "에겐녀"]
        counts = {t: 0 for t in type_order}
        for item in raw:
            t = item.get("_id")
            if t in counts:
                counts[t] = int(item.get("count", 0))

        total = sum(counts.values())
        if total <= 0:
            st.info("아직 통계 데이터가 없습니다.")
        else:
            labels = type_order
            values = [counts[t] for t in labels]
            colors = ["#75e8ff", "#6d5efc", "#ff77e6", "#371569"]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.62,
                        sort=False,
                        marker=dict(
                            colors=colors,
                            line=dict(color="rgba(255,255,255,0.22)", width=1),
                        ),
                        textinfo="percent+label",
                        textfont=dict(color="rgba(245,248,255,0.92)", size=13),
                        hovertemplate="%{label}<br>%{value}명 (%{percent})<extra></extra>",
                    )
                ]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
                font=dict(color="rgba(245,248,255,0.90)"),
                annotations=[
                    dict(
                        text=f"<b>{total}</b><br><span style='font-size:12px;color:rgba(245,248,255,0.70)'>TOTAL</span>",
                        x=0.5,
                        y=0.5,
                        font=dict(size=18, color="rgba(245,248,255,0.92)"),
                        showarrow=False,
                    )
                ],
            )

            st.plotly_chart(fig, use_container_width=True)

            pct_rows = []
            for t in labels:
                pct = round((counts[t] / total) * 100, 1)
                pct_rows.append({"유형": t, "건수": counts[t], "비율(%)": pct})
            st.dataframe(pct_rows, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    run()

