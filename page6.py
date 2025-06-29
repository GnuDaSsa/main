import streamlit as st
import random

def run():
    # MBTI 질문 pool (각 지표별 12개 이상, 총 48개)
    QUESTIONS_POOL = [
        # E/I (외향/내향)
        ("여럿이 모임을 즐긴다.", "E"),
        ("혼자만의 시간이 꼭 필요하다.", "I"),
        ("새로운 사람을 만나는 것이 어렵지 않다.", "E"),
        ("혼자 있을 때 에너지가 충전된다.", "I"),
        ("여러 사람 앞에서 이야기하는 것이 어렵지 않다.", "E"),
        ("조용한 환경이 더 편하다.", "I"),
        ("즉흥적으로 대화를 시작하는 편이다.", "E"),
        ("깊은 대화를 소수와 나누는 것이 좋다.", "I"),
        ("여행은 여럿이 함께 가는 게 좋다.", "E"),
        ("혼자만의 취미 시간이 소중하다.", "I"),
        ("사람들과 함께 있을 때 에너지가 난다.", "E"),
        ("혼자 있을 때 생각이 정리된다.", "I"),
        ("파티나 모임을 즐긴다.", "E"),
        ("조용한 공간에서 책 읽기를 좋아한다.", "I"),
        ("즉흥적으로 약속을 잡는 편이다.", "E"),
        ("계획된 시간에 혼자 있는 걸 선호한다.", "I"),
        ("SNS에 내 일상을 자주 공유한다.", "E"),
        ("SNS는 보기만 하고 잘 올리지 않는다.", "I"),
        ("새로운 환경에 쉽게 적응한다.", "E"),
        ("변화보다는 익숙함이 좋다.", "I"),
        ("사람들과 함께 있을 때 아이디어가 떠오른다.", "E"),
        ("혼자 있을 때 창의력이 발휘된다.", "I"),
        ("모르는 사람과 대화하는 것이 어렵지 않다.", "E"),
        ("낯선 사람과 대화가 부담스럽다.", "I"),
        # S/N (감각/직관)
        ("사실과 현실에 집중하는 편이다.", "S"),
        ("상상하거나 미래를 꿈꾸는 걸 좋아한다.", "N"),
        ("구체적인 설명이 이해하기 쉽다.", "S"),
        ("추상적인 개념을 생각하는 걸 좋아한다.", "N"),
        ("경험에서 배우는 것을 선호한다.", "S"),
        ("새로운 아이디어를 떠올리는 걸 즐긴다.", "N"),
        ("세부사항을 잘 챙기는 편이다.", "S"),
        ("큰 그림을 보는 것이 중요하다.", "N"),
        ("실용적인 것이 좋다.", "S"),
        ("가능성을 상상하는 것이 즐겁다.", "N"),
        ("현실적인 해결책을 선호한다.", "S"),
        ("미래의 가능성에 집중한다.", "N"),
        ("구체적인 예시가 있어야 이해가 쉽다.", "S"),
        ("상상력을 자주 발휘한다.", "N"),
        ("사실에 근거한 판단을 한다.", "S"),
        ("직감적으로 결정을 내린다.", "N"),
        ("현재에 집중하는 편이다.", "S"),
        ("미래를 계획하는 것이 즐겁다.", "N"),
        ("실제 경험이 중요하다.", "S"),
        ("이론이나 가설을 생각하는 걸 좋아한다.", "N"),
        ("디테일에 강하다.", "S"),
        ("새로운 트렌드에 민감하다.", "N"),
        ("현실적인 목표를 세운다.", "S"),
        ("혁신적인 아이디어를 추구한다.", "N"),
        # T/F (사고/감정)
        ("결정할 때 논리와 이성을 중시한다.", "T"),
        ("상대방의 감정에 공감하는 편이다.", "F"),
        ("객관적인 사실이 중요하다.", "T"),
        ("사람들의 기분을 신경 쓴다.", "F"),
        ("비판적으로 생각하는 편이다.", "T"),
        ("타인의 입장을 먼저 생각한다.", "F"),
        ("논리적 오류를 잘 찾아낸다.", "T"),
        ("분위기를 해치지 않으려 노력한다.", "F"),
        ("공정함이 중요하다.", "T"),
        ("조화가 중요하다.", "F"),
        ("논리적으로 토론하는 걸 좋아한다.", "T"),
        ("감정적으로 공감하는 대화를 선호한다.", "F"),
        ("객관적인 근거를 중시한다.", "T"),
        ("상대방의 감정에 민감하다.", "F"),
        ("비판적 사고를 자주 한다.", "T"),
        ("타인의 감정을 먼저 고려한다.", "F"),
        ("결정할 때 감정보다 논리를 우선한다.", "T"),
        ("상대방의 기분을 상하게 하지 않으려 한다.", "F"),
        ("논리적 설명이 설득력 있다고 느낀다.", "T"),
        ("감정적 호소에 쉽게 공감한다.", "F"),
        ("객관적 사실을 중시한다.", "T"),
        ("분위기 파악을 잘 한다.", "F"),
        ("비판적 피드백을 잘 준다.", "T"),
        ("타인의 감정에 쉽게 흔들린다.", "F"),
        # J/P (판단/인식)
        ("계획적으로 움직이는 것이 편하다.", "J"),
        ("즉흥적으로 행동하는 걸 좋아한다.", "P"),
        ("정해진 일정이 있으면 마음이 편하다.", "J"),
        ("상황에 따라 유연하게 대처한다.", "P"),
        ("목표를 세우고 실천하는 걸 좋아한다.", "J"),
        ("새로운 기회가 생기면 바로 도전한다.", "P"),
        ("마감일을 지키는 편이다.", "J"),
        ("마감 직전에 집중이 잘 된다.", "P"),
        ("정돈된 환경이 좋다.", "J"),
        ("약속 없는 자유 시간이 필요하다.", "P"),
        ("계획을 세우고 따르는 걸 선호한다.", "J"),
        ("즉흥적인 변화를 즐긴다.", "P"),
        ("일정을 미리 정해두는 편이다.", "J"),
        ("상황에 따라 계획을 바꾼다.", "P"),
        ("정리정돈을 잘 한다.", "J"),
        ("즉흥적으로 결정하는 걸 좋아한다.", "P"),
        ("계획이 틀어지면 불안하다.", "J"),
        ("계획 없이 떠나는 여행을 좋아한다.", "P"),
        ("목표 달성을 위해 노력한다.", "J"),
        ("새로운 경험을 추구한다.", "P"),
        ("일정을 지키는 것이 중요하다.", "J"),
        ("즉흥적으로 약속을 잡는다.", "P"),
        ("정해진 규칙을 따르는 편이다.", "J"),
        ("상황에 따라 융통성 있게 행동한다.", "P"),
    ]

    NUM_QUESTIONS = 48
    CHOICES = [
        ("매우 그렇다", 2, "#7a5cff"),
        ("그렇다", 1, "#a98cff"),
        ("중간", 0, "#cccccc"),
        ("아니다", -1, "#ffb6b6"),
        ("전혀 아니다", -2, "#ff5c5c"),
    ]

    MBTI_INFO = {
        "ISTJ": {
            "desc": "신중하고 책임감이 강하며, 원칙과 규칙을 중시하는 현실주의자입니다. 계획적이고 꼼꼼하며, 조직 내에서 신뢰받는 유형입니다.",
            "celeb": ["이병헌", "나문희", "모건 프리먼", "조지 워싱턴"],
            "good": ["ESFP", "ESTP"],
            "bad": ["ENFP", "ENTP"]
        },
        "ISFJ": {
            "desc": "따뜻하고 헌신적이며, 타인을 배려하는 성향이 강합니다. 조용하지만 책임감이 크고, 실용적이며 세심합니다.",
            "celeb": ["아이유", "수지", "앤 해서웨이", "비욘세"],
            "good": ["ESFP", "ESTP"],
            "bad": ["ENTP", "ENFP"]
        },
        "INFJ": {
            "desc": "이상주의적이고 통찰력이 뛰어나며, 깊은 공감 능력을 가진 조용한 리더형입니다. 가치와 의미를 중시합니다.",
            "celeb": ["방탄소년단 RM", "마크 트웨인", "마틴 루터 킹", "니콜 키드먼"],
            "good": ["ENFP", "ENTP"],
            "bad": ["ESTP", "ESFP"]
        },
        "INTJ": {
            "desc": "독립적이고 전략적이며, 미래지향적 사고를 가진 완벽주의자입니다. 논리적이고 체계적인 계획을 선호합니다.",
            "celeb": ["엘론 머스크", "마크 저커버그", "스티븐 호킹", "아인슈타인"],
            "good": ["ENFP", "ENTP"],
            "bad": ["ESFP", "ESTP"]
        },
        "ISTP": {
            "desc": "논리적이고 현실적이며, 문제 해결에 능한 실용주의자입니다. 즉흥적이고 유연하게 상황에 대처합니다.",
            "celeb": ["정해인", "클린트 이스트우드", "브루스 윌리스", "마이클 조던"],
            "good": ["ESFJ", "ENFJ"],
            "bad": ["ENFP", "ENTP"]
        },
        "ISFP": {
            "desc": "온화하고 겸손하며, 감성적이고 예술적인 성향이 강합니다. 자유롭고 조용한 환경을 선호합니다.",
            "celeb": ["뷔(방탄소년단)", "정우성", "마릴린 먼로", "브리트니 스피어스"],
            "good": ["ESFJ", "ENFJ"],
            "bad": ["ENTJ", "ENFJ"]
        },
        "INFP": {
            "desc": "이상주의적이고 창의적이며, 깊은 내면의 신념을 가진 성찰가입니다. 감정이 풍부하고 타인에게 공감합니다.",
            "celeb": ["정국(방탄소년단)", "조앤 K. 롤링", "윌리엄 셰익스피어", "조니 뎁"],
            "good": ["ENFJ", "ENTJ"],
            "bad": ["ESTJ", "ESFJ"]
        },
        "INTP": {
            "desc": "논리적이고 분석적이며, 독창적인 아이디어를 추구하는 사색가입니다. 이론과 원리를 탐구하는 것을 즐깁니다.",
            "celeb": ["양세형", "빌 게이츠", "아이작 뉴턴", "앨버트 아인슈타인"],
            "good": ["ENTJ", "ENFJ"],
            "bad": ["ESFJ", "ESTJ"]
        },
        "ESTP": {
            "desc": "적극적이고 현실적이며, 즉각적인 행동과 도전을 즐기는 활동가입니다. 위기 상황에서 침착하게 대처합니다.",
            "celeb": ["김종국", "마돈나", "어니스트 헤밍웨이", "도널드 트럼프"],
            "good": ["ISFJ", "ISTJ"],
            "bad": ["INFJ", "INFP"]
        },
        "ESFP": {
            "desc": "사교적이고 에너지 넘치며, 현재를 즐기는 낙천주의자입니다. 타인과 어울리며 긍정적인 분위기를 만듭니다.",
            "celeb": ["박명수", "마일리 사이러스", "엘튼 존", "카메론 디아즈"],
            "good": ["ISFJ", "ISTJ"],
            "bad": ["INFJ", "INTJ"]
        },
        "ENFP": {
            "desc": "열정적이고 창의적이며, 새로운 가능성을 추구하는 아이디어 뱅크입니다. 타인과의 소통을 즐깁니다.",
            "celeb": ["유재석", "로버트 다우니 주니어", "윌 스미스", "로빈 윌리엄스"],
            "good": ["INFJ", "INTJ"],
            "bad": ["ISTJ", "ISFJ"]
        },
        "ENTP": {
            "desc": "논쟁을 즐기고, 창의적이며, 새로운 아이디어를 탐구하는 혁신가입니다. 토론과 변화를 좋아합니다.",
            "celeb": ["김구라", "토마스 에디슨", "마크 트웨인", "레오나르도 다 빈치"],
            "good": ["INFJ", "INTJ"],
            "bad": ["ISFJ", "ISTJ"]
        },
        "ESTJ": {
            "desc": "체계적이고 현실적이며, 리더십이 뛰어난 관리자형입니다. 규칙과 질서를 중시하고, 책임감이 강합니다.",
            "celeb": ["박지성", "미셸 오바마", "조지 W. 부시", "엠마 왓슨"],
            "good": ["ISFP", "INFP"],
            "bad": ["INFP", "ISFP"]
        },
        "ESFJ": {
            "desc": "친절하고 사교적이며, 타인을 돕는 것을 즐기는 협력가입니다. 공동체와 조화를 중요하게 생각합니다.",
            "celeb": ["박보영", "테일러 스위프트", "휴 그랜트", "제니퍼 가너"],
            "good": ["ISFP", "INFP"],
            "bad": ["INTP", "ISTP"]
        },
        "ENFJ": {
            "desc": "이타적이고 카리스마 넘치며, 타인을 이끄는 리더형입니다. 타인의 감정에 민감하고, 협동을 중시합니다.",
            "celeb": ["방탄소년단 진", "버락 오바마", "오프라 윈프리", "벤 애플렉"],
            "good": ["INFP", "ISFP"],
            "bad": ["ISTP", "INTP"]
        },
        "ENTJ": {
            "desc": "결단력 있고 전략적인 리더형입니다. 목표 달성을 위해 체계적으로 계획하고 추진합니다.",
            "celeb": ["빌 클린턴", "스티브 잡스", "고든 램지", "마거릿 대처"],
            "good": ["INTP", "INFP"],
            "bad": ["ISFP", "INFP"]
        },
    }

    # 질문 순서 랜덤화 (세션별 고정)
    if "mbti_q_order" not in st.session_state or len(st.session_state.mbti_q_order) != NUM_QUESTIONS:
        by_type = {"E":[], "I":[], "S":[], "N":[], "T":[], "F":[], "J":[], "P":[]}
        for q, t in QUESTIONS_POOL:
            by_type[t].append((q, t))
        selected = []
        per_type = NUM_QUESTIONS // 4 // 2
        for t1, t2 in [("E","I"),("S","N"),("T","F"),("J","P")]:
            selected += random.sample(by_type[t1], per_type)
            selected += random.sample(by_type[t2], per_type)
        random.shuffle(selected)
        st.session_state.mbti_q_order = selected

    QUESTIONS = st.session_state.mbti_q_order

    # 상태 초기화
    if "mbti_answers" not in st.session_state or len(st.session_state.mbti_answers) != NUM_QUESTIONS:
        st.session_state.mbti_answers = [None] * NUM_QUESTIONS
    if "mbti_step" not in st.session_state:
        st.session_state.mbti_step = 0

    st.markdown("""
        <style>
        .big-font { font-size: 1.5rem !important; }
        .mbti-btn-row { display: flex; gap: 1.2rem; margin: 1.2rem 0 2.2rem 0; justify-content: center; }
        .mbti-btn {
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
        .mbti-btn.selected {
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
        </style>
    """, unsafe_allow_html=True)

    st.title("MBTI 검사 (질문 순서 랜덤, 정밀도 향상)")
    st.markdown('<div class="big-font">각 문항마다 더 나와 비슷한 쪽을 선택하세요.<br>질문은 한 번에 하나씩, 이전 버튼으로 답을 수정할 수 있습니다.</div>', unsafe_allow_html=True)

    idx = st.session_state.mbti_step
    q, code = QUESTIONS[idx]

    # 진행 상황 표시
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:0.7em; font-size:1.15rem; color:#7a5cff; font-weight:600;">
            <span>문항 {idx+1} / {NUM_QUESTIONS}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f'<div class="big-font fadein-q"><b>{idx+1}. {q}</b></div>', unsafe_allow_html=True)
    btn_cols = st.columns(len(CHOICES), gap="small")
    selected = st.session_state.mbti_answers[idx]
    for i, (label, val, color) in enumerate(CHOICES):
        btn_style = f"mbti-btn"
        if selected == i:
            btn_style += " selected"
        with btn_cols[i]:
            if st.button(label, key=f"mbti_btn_{idx}_{i}", help=label, use_container_width=True):
                st.session_state.mbti_answers[idx] = i
                if idx < NUM_QUESTIONS - 1:
                    st.session_state.mbti_step = idx + 1
                st.rerun()
    st.markdown(f"""
        <style>
        [data-testid="stButton"][key="mbti_btn_{idx}_0"] button.mbti-btn {{background:{CHOICES[0][2]};}}
        [data-testid="stButton"][key="mbti_btn_{idx}_1"] button.mbti-btn {{background:{CHOICES[1][2]};}}
        [data-testid="stButton"][key="mbti_btn_{idx}_2"] button.mbti-btn {{background:{CHOICES[2][2]};}}
        [data-testid="stButton"][key="mbti_btn_{idx}_3"] button.mbti-btn {{background:{CHOICES[3][2]};}}
        [data-testid="stButton"][key="mbti_btn_{idx}_4"] button.mbti-btn {{background:{CHOICES[4][2]};}}
        </style>
    """, unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns([1,2,1])
    with nav1:
        if st.button("이전", disabled=(idx==0), use_container_width=True):
            st.session_state.mbti_step = max(0, idx-1)
            st.rerun()

    # 모든 답변이 완료되면 결과 표시
    if "mbti_answers" in st.session_state and None not in st.session_state.mbti_answers:
        if st.button("결과 보기", use_container_width=True):
            scores = {"E":0, "I":0, "S":0, "N":0, "T":0, "F":0, "J":0, "P":0}
            for idx2, (q2, code2) in enumerate(QUESTIONS):
                val = st.session_state.mbti_answers[idx2]
                score = CHOICES[val][1]
                if code2 in scores:
                    scores[code2] += score

            e_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "E")
            i_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "I")
            s_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "S")
            n_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "N")
            t_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "T")
            f_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "F")
            j_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "J")
            p_score = sum(CHOICES[st.session_state.mbti_answers[i]][1] for i, (_, c) in enumerate(QUESTIONS) if c == "P")

            e_pct = int(round((e_score + 10) / 20 * 100))
            i_pct = 100 - e_pct
            s_pct = int(round((s_score + 10) / 20 * 100))
            n_pct = 100 - s_pct
            t_pct = int(round((t_score + 10) / 20 * 100))
            f_pct = 100 - t_pct
            j_pct = int(round((j_score + 10) / 20 * 100))
            p_pct = 100 - j_pct

            mbti = ""
            mbti += "E" if e_pct >= i_pct else "I"
            mbti += "S" if s_pct >= n_pct else "N"
            mbti += "T" if t_pct >= f_pct else "F"
            mbti += "J" if j_pct >= p_pct else "P"

            st.markdown(f"<div class='big-font'><b>당신의 MBTI는 <span style='color:#7a5cff'>{mbti}</span> 입니다!</b></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="big-font"><b>각 지표별 비율</b></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{e_pct}%">E {e_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{i_pct}%">I {i_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{s_pct}%">S {s_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{n_pct}%">N {n_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{t_pct}%">T {t_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{f_pct}%">F {f_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{j_pct}%">J {j_pct}%</div></div>
            <div class="percent-bar"><div class="percent-bar-inner" style="width:{p_pct}%">P {p_pct}%</div></div>
            """, unsafe_allow_html=True)

            info = MBTI_INFO.get(mbti, None)
            if info:
                st.markdown(f"""
                <div style="margin-top:2em; padding:1.5em 1.5em 1.2em 1.5em; background:#f8f6ff; border-radius:18px; border:1.5px solid #e3e6f3;">
                    <div style="font-size:1.25rem; font-weight:700; color:#7a5cff; margin-bottom:0.5em;">[{mbti}] 해설</div>
                    <div style="font-size:1.08rem; color:#444; margin-bottom:1em;">{info['desc']}</div>
                    <div style="font-size:1.08rem; color:#7a5cff; font-weight:600; margin-bottom:0.3em;">대표 연예인/유명인</div>
                    <div style="font-size:1.05rem; color:#333; margin-bottom:1em;">{', '.join(info['celeb'])}</div>
                    <div style="font-size:1.08rem; color:#7a5cff; font-weight:600; margin-bottom:0.3em;">잘 맞는 MBTI</div>
                    <div style="font-size:1.05rem; color:#333; margin-bottom:1em;">{', '.join(info['good'])}</div>
                    <div style="font-size:1.08rem; color:#7a5cff; font-weight:600; margin-bottom:0.3em;">상성이 좋지 않은 MBTI</div>
                    <div style="font-size:1.05rem; color:#333;">{', '.join(info['bad'])}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("MBTI 해설 정보를 찾을 수 없습니다.")

            # 결과의 맨 마지막에만 '다시 검사하기' 버튼
            if st.button("다시 검사하기", use_container_width=True):
                for key in ["mbti_answers", "mbti_step", "mbti_q_order"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
                return