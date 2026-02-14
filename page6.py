import streamlit as st
import random
import plotly.graph_objects as go
from datetime import datetime

from mongo_env import get_mongo_uri, get_collection

QUESTIONS_POOL = [
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
    ("매우 그렇다", 2),
    ("그렇다", 1),
    ("중간", 0),
    ("아니다", -1),
    ("전혀 아니다", -2),
]

CHOICE_COLORS = [
    "linear-gradient(135deg, rgba(117,232,255,0.30), rgba(12,18,66,0.50))",
    "linear-gradient(135deg, rgba(117,232,255,0.18), rgba(12,18,66,0.40))",
    "linear-gradient(135deg, rgba(255,255,255,0.10), rgba(12,18,66,0.35))",
    "linear-gradient(135deg, rgba(255,119,230,0.18), rgba(55,21,105,0.40))",
    "linear-gradient(135deg, rgba(255,119,230,0.30), rgba(55,21,105,0.50))",
]

MBTI_INFO = {
    "ISTJ": {
        "desc": "신중하고 책임감이 강하며, 원칙과 규칙을 중시하는 현실주의자입니다. 계획적이고 꼼꼼하며, 조직 내에서 신뢰받는 유형입니다.",
        "celeb": ["이병헌", "나문희", "모건 프리먼", "조지 워싱턴"],
        "good": ["ESFP", "ESTP"],
        "bad": ["ENFP", "ENTP"],
    },
    "ISFJ": {
        "desc": "따뜻하고 헌신적이며, 타인을 배려하는 성향이 강합니다. 조용하지만 책임감이 크고, 실용적이며 세심합니다.",
        "celeb": ["아이유", "수지", "앤 해서웨이", "비욘세"],
        "good": ["ESFP", "ESTP"],
        "bad": ["ENTP", "ENFP"],
    },
    "INFJ": {
        "desc": "이상주의적이고 통찰력이 뛰어나며, 깊은 공감 능력을 가진 조용한 리더형입니다. 가치와 의미를 중시합니다.",
        "celeb": ["방탄소년단 RM", "마크 트웨인", "마틴 루터 킹", "니콜 키드먼"],
        "good": ["ENFP", "ENTP"],
        "bad": ["ESTP", "ESFP"],
    },
    "INTJ": {
        "desc": "독립적이고 전략적이며, 미래지향적 사고를 가진 완벽주의자입니다. 논리적이고 체계적인 계획을 선호합니다.",
        "celeb": ["엘론 머스크", "마크 저커버그", "스티븐 호킹", "아인슈타인"],
        "good": ["ENFP", "ENTP"],
        "bad": ["ESFP", "ESTP"],
    },
    "ISTP": {
        "desc": "논리적이고 현실적이며, 문제 해결에 능한 실용주의자입니다. 즉흥적이고 유연하게 상황에 대처합니다.",
        "celeb": ["정해인", "클린트 이스트우드", "브루스 윌리스", "마이클 조던"],
        "good": ["ESFJ", "ENFJ"],
        "bad": ["ENFP", "ENTP"],
    },
    "ISFP": {
        "desc": "온화하고 겸손하며, 감성적이고 예술적인 성향이 강합니다. 자유롭고 조용한 환경을 선호합니다.",
        "celeb": ["뷔(방탄소년단)", "정우성", "마릴린 먼로", "브리트니 스피어스"],
        "good": ["ESFJ", "ENFJ"],
        "bad": ["ENTJ", "ENFJ"],
    },
    "INFP": {
        "desc": "이상주의적이고 창의적이며, 깊은 내면의 신념을 가진 성찰가입니다. 감정이 풍부하고 타인에게 공감합니다.",
        "celeb": ["정국(방탄소년단)", "조앤 K. 롤링", "윌리엄 셰익스피어", "조니 뎁"],
        "good": ["ENFJ", "ENTJ"],
        "bad": ["ESTJ", "ESFJ"],
    },
    "INTP": {
        "desc": "논리적이고 분석적이며, 독창적인 아이디어를 추구하는 사색가입니다. 이론과 원리를 탐구하는 것을 즐깁니다.",
        "celeb": ["양세형", "빌 게이츠", "아이작 뉴턴", "앨버트 아인슈타인"],
        "good": ["ENTJ", "ENFJ"],
        "bad": ["ESFJ", "ESTJ"],
    },
    "ESTP": {
        "desc": "적극적이고 현실적이며, 즉각적인 행동과 도전을 즐기는 활동가입니다. 위기 상황에서 침착하게 대처합니다.",
        "celeb": ["김종국", "마돈나", "어니스트 헤밍웨이", "도널드 트럼프"],
        "good": ["ISFJ", "ISTJ"],
        "bad": ["INFJ", "INFP"],
    },
    "ESFP": {
        "desc": "사교적이고 에너지 넘치며, 현재를 즐기는 낙천주의자입니다. 타인과 어울리며 긍정적인 분위기를 만듭니다.",
        "celeb": ["박명수", "마일리 사이러스", "엘튼 존", "카메론 디아즈"],
        "good": ["ISFJ", "ISTJ"],
        "bad": ["INFJ", "INTJ"],
    },
    "ENFP": {
        "desc": "열정적이고 창의적이며, 새로운 가능성을 추구하는 아이디어 뱅크입니다. 타인과의 소통을 즐깁니다.",
        "celeb": ["유재석", "로버트 다우니 주니어", "윌 스미스", "로빈 윌리엄스"],
        "good": ["INFJ", "INTJ"],
        "bad": ["ISTJ", "ISFJ"],
    },
    "ENTP": {
        "desc": "논쟁을 즐기고, 창의적이며, 새로운 아이디어를 탐구하는 혁신가입니다. 토론과 변화를 좋아합니다.",
        "celeb": ["김구라", "토마스 에디슨", "마크 트웨인", "레오나르도 다 빈치"],
        "good": ["INFJ", "INTJ"],
        "bad": ["ISFJ", "ISTJ"],
    },
    "ESTJ": {
        "desc": "체계적이고 현실적이며, 리더십이 뛰어난 관리자형입니다. 규칙과 질서를 중시하고, 책임감이 강합니다.",
        "celeb": ["박지성", "미셸 오바마", "조지 W. 부시", "엠마 왓슨"],
        "good": ["ISFP", "INFP"],
        "bad": ["INFP", "ISFP"],
    },
    "ESFJ": {
        "desc": "친절하고 사교적이며, 타인을 돕는 것을 즐기는 협력가입니다. 공동체와 조화를 중요하게 생각합니다.",
        "celeb": ["박보영", "테일러 스위프트", "휴 그랜트", "제니퍼 가너"],
        "good": ["ISFP", "INFP"],
        "bad": ["INTP", "ISTP"],
    },
    "ENFJ": {
        "desc": "이타적이고 카리스마 넘치며, 타인을 이끄는 리더형입니다. 타인의 감정에 민감하고, 협동을 중시합니다.",
        "celeb": ["방탄소년단 진", "버락 오바마", "오프라 윈프리", "벤 애플렉"],
        "good": ["INFP", "ISFP"],
        "bad": ["ISTP", "INTP"],
    },
    "ENTJ": {
        "desc": "결단력 있고 전략적인 리더형입니다. 목표 달성을 위해 체계적으로 계획하고 추진합니다.",
        "celeb": ["빌 클린턴", "스티브 잡스", "고든 램지", "마거릿 대처"],
        "good": ["INTP", "INFP"],
        "bad": ["ISFP", "INFP"],
    },
}


def _inject_css():
    st.markdown(
        """
        <style>
        :root{
            --bg0:#070a1b; --bg1:#0c1242; --bg2:#371569;
            --cyan:#75e8ff; --pink:#ff77e6;
            --glass:rgba(255,255,255,0.08); --glass2:rgba(255,255,255,0.06);
            --stroke:rgba(255,255,255,0.16);
            --text:rgba(245,248,255,0.92); --muted:rgba(245,248,255,0.70);
            --shadow:rgba(0,0,0,0.35);
        }
        @keyframes fadeIn{from{opacity:0}to{opacity:1}}
        @keyframes slideUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
        .anim-fadeIn{animation:fadeIn .55s ease-out both}
        .anim-slideUp{animation:slideUp .60s cubic-bezier(.2,.9,.2,1) both}

        .glass-card{
            background:linear-gradient(180deg,var(--glass),var(--glass2));
            border:1px solid var(--stroke);
            box-shadow:0 14px 40px var(--shadow);
            backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
            border-radius:22px;
        }
        .hero{padding:1.25rem 1.35rem 1.1rem}
        .hero-title{font-size:2.1rem;letter-spacing:-0.02em;font-weight:800;margin:0 0 .4rem}
        .hero-title span{background:linear-gradient(90deg,var(--cyan),var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent}
        .hero-sub{font-size:1.05rem;line-height:1.55;color:var(--muted);margin:0}

        .q-wrap{margin-top:.3rem;padding:1.15rem 1.25rem}
        .q-top{display:flex;align-items:center;justify-content:space-between;gap:.75rem;margin-bottom:.75rem}
        .q-count{font-weight:700;color:rgba(245,248,255,0.86);letter-spacing:.02em}
        .q-hint{font-size:.95rem;color:var(--muted)}
        .q-text{font-size:1.35rem;font-weight:800;letter-spacing:-0.015em;margin:.2rem 0 1rem}

        div[data-testid="stProgress"]>div{background:rgba(255,255,255,0.08)!important;border-radius:999px!important;height:12px!important;border:1px solid rgba(255,255,255,0.12)!important;overflow:hidden!important}
        div[data-testid="stProgress"] div[role="progressbar"]{background:linear-gradient(90deg,var(--cyan),var(--pink))!important;border-radius:999px!important}

        .choice-shell div[data-testid="stButton"]>button{
            width:100%!important;padding:.9rem .8rem!important;border-radius:16px!important;
            border:1px solid rgba(255,255,255,0.18)!important;
            color:rgba(245,248,255,0.95)!important;
            box-shadow:0 10px 28px rgba(0,0,0,0.22)!important;
            backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
            transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;
            font-weight:700!important;min-height:52px;
        }
        .choice-shell div[data-testid="stButton"]>button:hover{
            transform:translateY(-2px);box-shadow:0 16px 40px rgba(0,0,0,0.35)!important;
            border-color:rgba(117,232,255,0.35)!important;
        }

        .soft-btn div[data-testid="stButton"]>button{
            border-radius:14px!important;border:1px solid rgba(255,255,255,0.18)!important;
            background:rgba(255,255,255,0.06)!important;color:rgba(245,248,255,0.92)!important;
            transition:transform .16s ease,border-color .16s ease;
        }
        .soft-btn div[data-testid="stButton"]>button:hover{transform:translateY(-1px);border-color:rgba(255,119,230,0.35)!important}

        .modal-title{font-size:2.0rem;font-weight:900;letter-spacing:-0.02em;margin:0;line-height:1.15}
        .modal-title .grad{background:linear-gradient(90deg,var(--cyan),var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent}
        .modal-kicker{margin:.25rem 0 .7rem;color:rgba(245,248,255,0.74);font-size:1.02rem}
        .modal-desc{margin-top:.75rem;color:rgba(245,248,255,0.90);font-size:1.03rem;line-height:1.65}
        .modal-desc b{color:rgba(245,248,255,0.98)}

        .dim-bar{
            display:flex;height:36px;border-radius:18px;overflow:hidden;margin-bottom:.6rem;
            border:1px solid rgba(255,255,255,0.12);
        }
        .dim-left{display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.95rem;color:#fff}
        .dim-right{display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.95rem;color:#fff}
        .dim-label{display:flex;justify-content:space-between;font-weight:600;font-size:.92rem;color:rgba(245,248,255,0.85);margin-bottom:.2rem}
        .pill-row{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.9rem}
        .pill{padding:.38rem .62rem;border-radius:999px;border:1px solid rgba(255,255,255,0.14);background:rgba(255,255,255,0.05);font-size:.92rem;color:rgba(245,248,255,0.82)}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_state():
    defaults = {
        "mbti_q_order": None,
        "mbti_answers": None,
        "mbti_step": 0,
        "mbti_result": None,
        "mbti_pcts": None,
        "mbti_result_saved": False,
        "mbti_show_modal": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _select_questions():
    if st.session_state.mbti_q_order and len(st.session_state.mbti_q_order) == NUM_QUESTIONS:
        return
    by_type = {}
    for q, t in QUESTIONS_POOL:
        by_type.setdefault(t, []).append((q, t))
    selected = []
    per_type = NUM_QUESTIONS // 4 // 2
    for t1, t2 in [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]:
        selected += random.sample(by_type[t1], per_type)
        selected += random.sample(by_type[t2], per_type)
    random.shuffle(selected)
    st.session_state.mbti_q_order = selected
    st.session_state.mbti_answers = [None] * NUM_QUESTIONS


def _compute_result(questions, answers):
    scores = {}
    for idx, (_, code) in enumerate(questions):
        val = answers[idx]
        if val is None:
            continue
        scores[code] = scores.get(code, 0) + CHOICES[val][1]

    dims = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]
    mbti = ""
    pcts = {}
    for pos, neg in dims:
        ps = max(scores.get(pos, 0), 0)
        ns = max(scores.get(neg, 0), 0)
        total = ps + ns
        if total == 0:
            pos_pct = 50
        else:
            pos_pct = int(round(ps / total * 100))
        neg_pct = 100 - pos_pct
        pcts[pos] = pos_pct
        pcts[neg] = neg_pct
        mbti += pos if pos_pct >= neg_pct else neg
    return mbti, pcts


@st.dialog("MBTI 결과", width="large")
def _show_mbti_result_dialog():
    mbti = st.session_state.mbti_result
    pcts = st.session_state.mbti_pcts
    info = MBTI_INFO.get(mbti)

    st.markdown(
        f"""
        <div class="modal-kicker">당신의 MBTI</div>
        <h2 class="modal-title">🧠 <span class="grad">{mbti}</span></h2>
        """,
        unsafe_allow_html=True,
    )

    if info:
        st.markdown(f'<div class="modal-desc">{info["desc"]}</div>', unsafe_allow_html=True)

    dims = [("E", "I", "#75e8ff", "#6d5efc"), ("S", "N", "#34d399", "#f59e0b"), ("T", "F", "#3b82f6", "#ef4444"), ("J", "P", "#8b5cf6", "#ff77e6")]
    for pos, neg, col_l, col_r in dims:
        lp = pcts.get(pos, 50)
        rp = pcts.get(neg, 50)
        st.markdown(
            f"""
            <div class="dim-label"><span>{pos} {lp}%</span><span>{neg} {rp}%</span></div>
            <div class="dim-bar">
              <div class="dim-left" style="width:{max(lp,5)}%;background:{col_l}">{pos}</div>
              <div class="dim-right" style="width:{max(rp,5)}%;background:{col_r}">{neg}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if info:
        st.markdown(
            f"""
            <div style="margin-top:.8rem;padding:.75rem .9rem;border-radius:18px;border:1px solid rgba(255,255,255,0.14);background:linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03))">
              <div style="font-weight:700;color:var(--cyan);margin-bottom:.3rem">대표 유명인</div>
              <div class="modal-desc" style="margin:0">{', '.join(info['celeb'])}</div>
              <div style="font-weight:700;color:var(--cyan);margin:.5rem 0 .3rem">잘 맞는 MBTI</div>
              <div class="modal-desc" style="margin:0">{', '.join(info['good'])}</div>
              <div style="font-weight:700;color:var(--pink);margin:.5rem 0 .3rem">상성이 안 맞는 MBTI</div>
              <div class="modal-desc" style="margin:0">{', '.join(info['bad'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("닫기", key="mbti_close_dialog", use_container_width=True):
        st.session_state.mbti_show_modal = False
        st.rerun()


def run():
    mongo_uri = get_mongo_uri()
    if not mongo_uri:
        st.error("MongoDB 연결 정보(MONGODB_URI)가 설정되지 않았습니다.")
        st.info("로컬: `.env` 설정 / 배포: Streamlit Secrets 설정을 추가하세요.")
        return

    _inject_css()
    _init_state()
    _select_questions()

    questions = st.session_state.mbti_q_order

    st.markdown(
        """
        <div class="glass-card hero anim-fadeIn">
          <div class="hero-title">🧠 <span>MBTI 검사</span></div>
          <p class="hero-sub">48개 문항으로 당신의 MBTI를 정밀 분석합니다.<br>
          질문은 세션마다 랜덤 순서로 출제됩니다.</p>
          <div class="pill-row">
            <div class="pill">48문항</div>
            <div class="pill">랜덤 순서</div>
            <div class="pill">5단계 응답</div>
            <div class="pill">모달 결과</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🧪 검사", "📊 통계"])

    with tab1:
        idx = st.session_state.mbti_step
        answers = st.session_state.mbti_answers

        all_answered = answers is not None and None not in answers

        if not all_answered:
            q_text, q_code = questions[idx]

            st.progress(idx / NUM_QUESTIONS)

            st.markdown(
                f"""
                <div class="glass-card q-wrap anim-slideUp">
                  <div class="q-top">
                    <div class="q-count">Q {idx+1} / {NUM_QUESTIONS}</div>
                    <div class="q-hint">얼마나 동의하나요?</div>
                  </div>
                  <div class="q-text anim-fadeIn">{idx+1}. {q_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            cols = st.columns(5, gap="small")
            for i, (label, _val) in enumerate(CHOICES):
                bg = CHOICE_COLORS[i]
                with cols[i]:
                    st.markdown(
                        f'<div class="choice-shell" style="--bg:{bg}"><style>.choice-shell:nth-of-type({i+1}) div[data-testid="stButton"]>button{{background:{bg}!important}}</style>',
                        unsafe_allow_html=True,
                    )
                    if st.button(label, key=f"mbti_btn_{idx}_{i}", use_container_width=True):
                        st.session_state.mbti_answers[idx] = i
                        if idx < NUM_QUESTIONS - 1:
                            st.session_state.mbti_step = idx + 1
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            if idx > 0:
                st.markdown('<div class="soft-btn" style="margin-top:.8rem">', unsafe_allow_html=True)
                if st.button("이전", use_container_width=True, key="mbti_prev"):
                    st.session_state.mbti_step = max(0, idx - 1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            if st.session_state.mbti_result is None:
                mbti, pcts = _compute_result(questions, answers)
                st.session_state.mbti_result = mbti
                st.session_state.mbti_pcts = pcts
                st.session_state.mbti_show_modal = True

            if not st.session_state.mbti_result_saved and st.session_state.mbti_result:
                try:
                    collection = get_collection("automation_db", "inspection_records")
                    if collection is not None:
                        collection.insert_one({
                            "result_type": st.session_state.mbti_result,
                            "pcts": st.session_state.mbti_pcts,
                            "created_at": datetime.now(),
                            "city": "성남시",
                            "source": "MBTI",
                        })
                except Exception:
                    pass
                st.session_state.mbti_result_saved = True

            st.markdown(
                """
                <div class="glass-card q-wrap anim-slideUp" style="margin-top:1rem">
                  <div class="q-text" style="margin:0 0 .55rem">검사 완료</div>
                  <div class="q-hint">결과는 팝업으로 표시됩니다. 닫은 뒤 다시 검사할 수 있어요.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="soft-btn">', unsafe_allow_html=True)
                if st.button("결과 다시 보기", use_container_width=True, key="mbti_reshow"):
                    st.session_state.mbti_show_modal = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="soft-btn">', unsafe_allow_html=True)
                if st.button("다시 검사하기", use_container_width=True, key="mbti_restart"):
                    for k in ["mbti_q_order", "mbti_answers", "mbti_step", "mbti_result", "mbti_pcts", "mbti_result_saved", "mbti_show_modal"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # Show result dialog
        if st.session_state.get("mbti_show_modal") and st.session_state.get("mbti_result"):
            _show_mbti_result_dialog()

    with tab2:
        st.markdown(
            """
            <div class="glass-card q-wrap anim-slideUp" style="margin-top:.8rem">
              <div class="q-text" style="margin:0 0 .4rem">MBTI 유형 분포</div>
              <div class="q-hint">전체 검사 결과의 MBTI 유형별 분포입니다.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="soft-btn" style="margin-top:.7rem">', unsafe_allow_html=True)
        if st.button("통계 새로고침", type="primary", use_container_width=True, key="mbti_stat_refresh"):
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        try:
            collection = get_collection("automation_db", "inspection_records")
            if collection is None:
                st.info("DB 연결 실패")
            else:
                pipeline = [
                    {"$match": {"source": "MBTI"}},
                    {"$group": {"_id": "$result_type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
                raw = list(collection.aggregate(pipeline))
                all_types = list(MBTI_INFO.keys())
                counts = {t: 0 for t in all_types}
                for item in raw:
                    t = item.get("_id")
                    if t in counts:
                        counts[t] = int(item.get("count", 0))
                total = sum(counts.values())

                if total == 0:
                    st.info("아직 통계 데이터가 없습니다.")
                else:
                    labels = [t for t in all_types if counts[t] > 0]
                    values = [counts[t] for t in labels]
                    colors = ["#75e8ff", "#6d5efc", "#34d399", "#f59e0b", "#3b82f6", "#ef4444", "#8b5cf6", "#ff77e6",
                              "#06b6d4", "#a855f7", "#10b981", "#f97316", "#6366f1", "#ec4899", "#14b8a6", "#e11d48"]

                    fig = go.Figure(data=[go.Bar(
                        x=labels,
                        y=values,
                        marker=dict(color=colors[:len(labels)], line=dict(color="rgba(255,255,255,0.2)", width=1)),
                        text=[f"{v}명" for v in values],
                        textposition="auto",
                        textfont=dict(color="white", size=12),
                    )])
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=30, b=10),
                        font=dict(color="rgba(245,248,255,0.90)"),
                        xaxis=dict(showgrid=False, color="rgba(245,248,255,0.7)"),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", color="rgba(245,248,255,0.7)"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    pct_rows = []
                    for t in labels:
                        pct = round((counts[t] / total) * 100, 1)
                        pct_rows.append({"유형": t, "건수": counts[t], "비율(%)": pct})
                    st.dataframe(pct_rows, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"통계 조회 오류: {e}")


if __name__ == "__main__":
    run()
