'use client';
import { useState, useCallback, useEffect, useRef } from 'react';
import { STORY, CHAR_INFO, BG_URL, CHAR_URL } from './story';
import type { CharId, CharDisplay, Position } from './story';

type Vars = { mentality: number; team_bond: number };

interface GameState {
  scene: string;
  beatIdx: number;
  vars: Vars;
  chars: CharDisplay[];
  bg: string | null;
  ended: boolean;
  endingText: string;
  items: string[];
}

const ITEM_NAMES: Record<string, string> = {
  mystery_key: '이름 모를 열쇠',
};

function applyEffects(vars: Vars, e: { mentality?: number; team_bond?: number }): Vars {
  return { mentality: vars.mentality + (e.mentality || 0), team_bond: vars.team_bond + (e.team_bond || 0) };
}

function updateChars(current: CharDisplay[], incoming: CharDisplay[]): CharDisplay[] {
  const next = [...current];
  for (const c of incoming) {
    const idx = next.findIndex(x => x.id === c.id);
    if (idx >= 0) next[idx] = c; else next.push(c);
  }
  return next;
}

function processToInteractive(scene: string, beatIdx: number, vars: Vars, chars: CharDisplay[], bg: string | null, items: string[]): GameState {
  let s = scene, i = beatIdx, v = vars, c = chars, b = bg, it = items;
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const sd = STORY[s];
    if (!sd) return { scene: s, beatIdx: i, vars: v, chars: c, bg: b, ended: true, endingText: '', items: it };
    if (i >= sd.beats.length) {
      if (sd.next) {
        // 엔딩 분기: ending_branch 씬에서 변수로 엔딩 결정
        if (sd.next === 'ending_branch') {
          const m = v.mentality, t = v.team_bond;
          if (m >= 2 && t >= 2)      { s = 'ending_growth';   }
          else if (m <= 0 && t >= 2) { s = 'ending_team';     }
          else if (m >= 2 && t <= 0) { s = 'ending_solo';     }
          else                       { s = 'ending_burnout';  }
          i = 0; continue;
        }
        s = sd.next; i = 0; continue;
      }
      return { scene: s, beatIdx: i, vars: v, chars: c, bg: b, ended: true, endingText: '', items: it };
    }
    const beat = sd.beats[i];
    if (beat.kind === 'bg')      { b = beat.name; i++; continue; }
    if (beat.kind === 'show')    { c = updateChars(c, beat.chars); i++; continue; }
    if (beat.kind === 'hide')    { c = c.filter(ch => !beat.ids.includes(ch.id)); i++; continue; }
    if (beat.kind === 'hideAll') { c = []; i++; continue; }
    if (beat.kind === 'effects') { v = applyEffects(v, beat); i++; continue; }
    if (beat.kind === 'item')    { if (!it.includes(beat.itemId)) it = [...it, beat.itemId]; i++; continue; }
    if (beat.kind === 'ending')  { return { scene: s, beatIdx: i, vars: v, chars: c, bg: b, ended: true, endingText: beat.text, items: it }; }
    // narration, dialogue, choice, photo — stop and return
    return { scene: s, beatIdx: i, vars: v, chars: c, bg: b, ended: false, endingText: '', items: it };
  }
}

const INIT = processToInteractive('start', 0, { mentality: 0, team_bond: 0 }, [], null, []);

function getCharStyle(pos: Position, id?: string): React.CSSProperties {
  const isSmallCaller = id === 'caller_ice' || id === 'caller_spring';
  const common: React.CSSProperties = {
    position: 'absolute', bottom: '21%', height: pos === 'caller' ? (isSmallCaller ? '65%' : '130%') : '68%',
    width: 'auto', objectFit: 'contain', filter: 'drop-shadow(0 6px 18px rgba(0,0,0,0.7))',
    pointerEvents: 'none', userSelect: 'none',
  };
  if (pos === 'left'       || pos === 'left_low')   return { ...common, left: '3%', bottom: pos === 'left_low' ? '16%' : '21%' };
  if (pos === 'center'     || pos === 'center_low') return { ...common, left: '50%', transform: 'translateX(-50%)', bottom: pos === 'center_low' ? '16%' : '21%' };
  if (pos === 'right'      || pos === 'right_low')  return { ...common, right: '3%', bottom: pos === 'right_low' ? '16%' : '21%' };
  if (pos === 'caller') {
    if (id === 'caller_ice')    return { ...common, top: '4%',  right: '1%', bottom: 'auto' };
    if (id === 'caller_spring') return { ...common, top: '18%', right: '1%', bottom: 'auto' };
    return { ...common, top: '-47%', right: '-15%', bottom: 'auto' };
  }
  return common;
}

// BGM zone detection: returns 1, 2, or 3
const BGM3_SCENES = new Set([
  'first_call', 'early_days', 'winter_arc', 'winter_relief',
  'ice_claim', 'choice_explain', 'choice_empathy', 'choice_escalate',
  'spring_arc', 'spring_defend', 'spring_yield', 'spring_resolution',
]);
const BGM2_SCENES = new Set([
  'transfer_end', 'ending_branch',
  'ending_growth', 'ending_growth_key', 'ending_team', 'ending_solo', 'ending_burnout',
]);
function getBgmTrack(scene: string, ended: boolean): 1 | 2 | 3 {
  if (ended || BGM2_SCENES.has(scene)) return 2;
  if (BGM3_SCENES.has(scene)) return 3;
  return 1;
}

export default function NovelPage() {
  const [state, setState] = useState<GameState>(INIT);
  const [textKey, setTextKey] = useState(0);
  const [bgmOn, setBgmOn] = useState(true);
  const [gameStarted, setGameStarted] = useState(false);
  const [isMobileGame, setIsMobileGame] = useState(false);
  const [isPortrait, setIsPortrait] = useState(false);
  const [itemNotif, setItemNotif] = useState<string | null>(null);
  const [btnHover, setBtnHover] = useState(false);
  const [mouse, setMouse] = useState({ x: 0.5, y: 0.5 });
  const [statDelta, setStatDelta] = useState<{ m?: number; t?: number; key: number } | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const bgm1Ref = useRef<HTMLAudioElement | null>(null);
  const bgm2Ref = useRef<HTMLAudioElement | null>(null);
  const bgm3Ref = useRef<HTMLAudioElement | null>(null);
  const startedRef = useRef(false);
  const currentTrackRef = useRef(0);
  const prevItemsRef = useRef<string[]>([]);

  // Preload all game images while user is on start screen
  useEffect(() => {
    const bgNames = new Set<string>();
    const charIdSet = new Set<string>();
    Object.values(STORY).forEach(scene => {
      scene.beats.forEach((b: any) => {
        if (b.kind === 'bg') bgNames.add(b.name);
        if (b.kind === 'show') b.chars.forEach((c: any) => charIdSet.add(c.id));
        if (b.kind === 'photo') { const img = new Image(); img.src = b.src; }
      });
    });
    bgNames.forEach(name => { const img = new Image(); img.src = BG_URL(name); });
    charIdSet.forEach(id => { const img = new Image(); img.src = CHAR_URL(id as CharId); });
    const start = new Image(); start.src = '/novel/start_bg.jpg';
  }, []);

  // Init audio elements once
  useEffect(() => {
    const a1 = new Audio('/novel/bgm.mp3');
    a1.loop = true; a1.volume = 0.35;
    bgm1Ref.current = a1;
    const a2 = new Audio('/novel/bgm2.mp3');
    a2.loop = true; a2.volume = 0.35;
    bgm2Ref.current = a2;
    const a3 = new Audio('/novel/bgm3.mp3');
    a3.loop = true; a3.volume = 0.35;
    bgm3Ref.current = a3;
    return () => { a1.pause(); a2.pause(); a3.pause(); };
  }, []);

  // Orientation detection
  useEffect(() => {
    const check = () => setIsPortrait(window.innerHeight > window.innerWidth);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  // Item toast detection
  useEffect(() => {
    const prev = prevItemsRef.current;
    const curr = state.items;
    const newItems = curr.filter(id => !prev.includes(id));
    if (newItems.length > 0) {
      const name = ITEM_NAMES[newItems[0]] || newItems[0];
      setItemNotif(name);
      const t = setTimeout(() => setItemNotif(null), 3800);
      prevItemsRef.current = curr;
      return () => clearTimeout(t);
    }
    prevItemsRef.current = curr;
  }, [state.items]);

  // Switch BGM based on scene — always restart from beginning on track change
  useEffect(() => {
    if (!startedRef.current) return;
    const refs = [bgm1Ref.current, bgm2Ref.current, bgm3Ref.current];
    const track = getBgmTrack(state.scene, state.ended);
    const changed = track !== currentTrackRef.current;
    currentTrackRef.current = track;
    refs.forEach((a, i) => {
      if (!a) return;
      if (i + 1 === track) {
        if (changed) { a.currentTime = 0; }
        if (bgmOn && a.paused) a.play().catch(() => {});
        else if (!bgmOn && !a.paused) a.pause();
      } else {
        if (!a.paused) a.pause();
        if (changed) a.currentTime = 0;
      }
    });
  }, [state.scene, state.ended, bgmOn]);

  // BGM toggle
  const toggleBgm = useCallback(() => {
    setBgmOn(v => {
      const next = !v;
      const refs = [bgm1Ref.current, bgm2Ref.current, bgm3Ref.current];
      const track = currentTrackRef.current;
      refs.forEach((a, i) => {
        if (!a) return;
        if (i + 1 === track) {
          if (next) a.play().catch(() => {});
          else a.pause();
        }
      });
      return next;
    });
  }, []);

  const playClick = useCallback(() => {
    try {
      if (!audioCtxRef.current) audioCtxRef.current = new AudioContext();
      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = 'sine';
      osc.frequency.setValueAtTime(900, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(500, ctx.currentTime + 0.06);
      gain.gain.setValueAtTime(0.22, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.09);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.09);
    } catch { /* ignore */ }
  }, []);

  const startGame = useCallback(async () => {
    // 모바일에서만 전체화면 + 가로 고정
    const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth < 768;
    if (isMobile) {
      try {
        const el = document.documentElement;
        if (el.requestFullscreen) await el.requestFullscreen();
        else if ((el as any).webkitRequestFullscreen) (el as any).webkitRequestFullscreen();
      } catch { /* ignore */ }
      try {
        if (screen.orientation && (screen.orientation as any).lock) {
          await (screen.orientation as any).lock('landscape');
        }
      } catch { /* ignore */ }
    }

    setIsMobileGame(isMobile);
    setGameStarted(true);
    startedRef.current = true;
    currentTrackRef.current = 1;
    const a1 = bgm1Ref.current;
    if (a1) { a1.currentTime = 0; a1.play().catch(() => {}); }
  }, []);

  const advance = useCallback(() => {
    setState(prev => {
      if (prev.ended) return prev;
      const beat = STORY[prev.scene]?.beats[prev.beatIdx];
      if (!beat || beat.kind === 'choice') return prev;
      return processToInteractive(prev.scene, prev.beatIdx + 1, prev.vars, prev.chars, prev.bg, prev.items);
    });
    setTextKey(k => k + 1);
  }, []);

  const choose = useCallback((idx: number) => {
    playClick();
    setState(prev => {
      const beat = STORY[prev.scene]?.beats[prev.beatIdx];
      if (!beat || beat.kind !== 'choice') return prev;
      const opt = beat.options[idx];
      if (opt.effects && (opt.effects.mentality || opt.effects.team_bond)) {
        setStatDelta({ m: opt.effects.mentality, t: opt.effects.team_bond, key: Date.now() });
        setTimeout(() => setStatDelta(null), 1600);
      }
      const newVars = opt.effects ? applyEffects(prev.vars, opt.effects) : prev.vars;
      return processToInteractive(opt.jump, 0, newVars, prev.chars, prev.bg, prev.items);
    });
    setTextKey(k => k + 1);
  }, [playClick]);

  const useKey = useCallback(() => {
    setState(prev => processToInteractive('ending_growth_key', 0, prev.vars, [], prev.bg, prev.items));
    setTextKey(k => k + 1);
  }, []);

  const tryTrueEnding = useCallback(() => {
    setState(prev => processToInteractive('spring_arc', 0, { mentality: 2, team_bond: 2 }, [], null, prev.items));
    setTextKey(k => k + 1);
  }, []);

  const restart = useCallback(() => {
    // Exit fullscreen & unlock orientation
    try {
      if (document.fullscreenElement) document.exitFullscreen();
      else if ((document as any).webkitFullscreenElement) (document as any).webkitExitFullscreen();
    } catch { /* ignore */ }
    try {
      if (screen.orientation && (screen.orientation as any).unlock) (screen.orientation as any).unlock();
    } catch { /* ignore */ }

    setState(INIT);
    setTextKey(k => k + 1);
    setGameStarted(false);
    startedRef.current = false;
    currentTrackRef.current = 0;
    [bgm1Ref, bgm2Ref, bgm3Ref].forEach(r => { if (r.current) { r.current.pause(); r.current.currentTime = 0; } });
  }, []);

  const currentBeat = STORY[state.scene]?.beats[state.beatIdx];
  const m = state.vars.mentality;
  const t = state.vars.team_bond;
  const hasKey = state.items.includes('mystery_key');
  const isGrowthEnding = state.scene === 'ending_growth' || state.scene === 'ending_growth_key';
  const showKeyPopup = state.ended && state.scene === 'ending_growth' && hasKey;
  const showTrueEndingHint = state.ended && !isGrowthEnding;

  /* ── START SCREEN ── */
  if (!gameStarted) {
    const dx = (mouse.x - 0.5);
    const dy = (mouse.y - 0.5);
    return (
      <div style={{ width: '100%', maxWidth: 900, margin: '0 auto 2rem' }}>
        <style>{`
          @keyframes titleFloat  { 0%,100% { transform: translateY(0px);  } 50% { transform: translateY(-7px);  } }
          @keyframes subFloat    { 0%,100% { transform: translateY(0px);  } 50% { transform: translateY(-4px);  } }
          @keyframes bgBreathe   { 0%,100% { transform: scale(1.06) translate(0px,0px); } 50% { transform: scale(1.09) translate(0px,-3px); } }
          @keyframes btnSketch   { 0%,100% { box-shadow: 3px 3px 0 #111; } 50% { box-shadow: 4px 4px 0 #111; } }
          @keyframes fadeUp      { from { opacity:0; transform: translateY(18px); } to { opacity:1; transform: translateY(0); } }
        `}</style>
        <div
          style={{ position: 'relative', width: '100%', aspectRatio: '16/9', overflow: 'hidden', borderRadius: 4, background: '#e8e4dc', cursor: 'default' }}
          onMouseMove={e => {
            const r = e.currentTarget.getBoundingClientRect();
            setMouse({ x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height });
          }}
          onMouseLeave={() => setMouse({ x: 0.5, y: 0.5 })}
        >
          {/* 배경 이미지 — parallax */}
          <div style={{
            position: 'absolute', inset: '-6%',
            backgroundImage: `url('/novel/start_bg.jpg')`,
            backgroundSize: 'cover', backgroundPosition: 'center',
            transform: `translate(${dx * -18}px, ${dy * -12}px) scale(1.06)`,
            transition: 'transform 0.25s ease-out',
          }} />
          {/* 밝기 오버레이 */}
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(235,230,220,0.18)' }} />

          {/* 시작하기 버튼만 */}
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: '10%' }}>
            <button
              onClick={startGame}
              onMouseEnter={() => setBtnHover(true)}
              onMouseLeave={() => setBtnHover(false)}
              style={{
                padding: 'clamp(0.55rem,1.4vw,0.85rem) clamp(1.8rem,5vw,3.2rem)',
                background: btnHover ? '#111' : 'rgba(255,255,255,0.88)',
                border: '2.5px solid #111',
                color: btnHover ? '#fff' : '#111',
                fontSize: 'clamp(0.85rem,2vw,1.05rem)',
                fontWeight: 700, cursor: 'pointer',
                letterSpacing: '0.18em',
                boxShadow: btnHover ? '5px 5px 0 #333' : '3px 3px 0 #333',
                transform: btnHover ? 'translate(-2px,-2px) scale(1.03)' : 'translate(0,0) scale(1)',
                transition: 'all 0.13s ease',
                animation: 'fadeUp 0.7s 0.3s ease both',
              }}
            >시작하기</button>
          </div>

          <div style={{ position: 'absolute', bottom: 10, right: 14, fontFamily: 'monospace', fontSize: '0.58rem', color: 'rgba(0,0,0,0.3)', letterSpacing: '0.08em' }}>© 2026 DLC — AI Club</div>
        </div>
      </div>
    );
  }

  /* ── GAME WRAPPER (모바일: fullscreen fixed / 데스크톱: 일반 페이지 레이아웃) ── */
  return (
    <div style={isMobileGame
      ? { position: 'fixed', inset: 0, zIndex: 9999, background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }
      : { width: '100%', maxWidth: 900, margin: '0 auto 2rem' }
    }>
      <style>{`
        @keyframes vnFadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.2; } }
        @keyframes rotateBounce { 0%,100% { transform: rotate(-15deg); } 50% { transform: rotate(15deg); } }
        @keyframes itemPop { 0% { opacity:0; transform: translate(-50%,-50%) scale(0.85); } 15% { opacity:1; transform: translate(-50%,-50%) scale(1.04); } 25% { transform: translate(-50%,-50%) scale(1); } 80% { opacity:1; } 100% { opacity:0; transform: translate(-50%,-50%) scale(0.95); } }
        @keyframes statFloat { 0% { opacity:1; transform: translateY(0) scale(1); } 30% { opacity:1; transform: translateY(-10px) scale(1.1); } 100% { opacity:0; transform: translateY(-38px) scale(0.9); } }
      `}</style>

      {/* Portrait rotation prompt — 모바일 전용 */}
      {isMobileGame && isPortrait && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 20, background: 'rgba(2,4,18,0.97)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, color: '#c8deff', textAlign: 'center', padding: 32 }}>
          <div style={{ fontSize: '2.8rem', animation: 'rotateBounce 1.6s ease-in-out infinite', display: 'inline-block' }}>📱</div>
          <div style={{ fontSize: '1.05rem', fontWeight: 700 }}>기기를 가로로 돌려주세요</div>
          <div style={{ fontSize: '0.78rem', color: '#4a6aaa', lineHeight: 1.6 }}>가로 모드에서 최적으로 플레이됩니다</div>
          <button onClick={restart} style={{ marginTop: 8, padding: '0.5rem 1.4rem', background: 'none', border: '1px solid rgba(255,255,255,0.15)', color: '#555', borderRadius: 6, cursor: 'pointer', fontSize: 12 }}>
            나가기
          </button>
        </div>
      )}

      {/* ── ENDING SCREEN ── */}
      {state.ended ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 14, textAlign: 'center', color: '#f3f7ff', padding: 40, background: isMobileGame ? 'transparent' : '#050a1a', borderRadius: isMobileGame ? 0 : 4, minHeight: isMobileGame ? 'auto' : 360 }}>
          <div style={{ fontSize: '0.9rem', color: '#7a90c8', letterSpacing: 3 }}>— ENDING —</div>
          <div style={{ fontSize: 'clamp(1.1rem, 3vw, 1.6rem)', fontWeight: 800, marginTop: 4 }}>{state.endingText}</div>
          <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
            <div style={{ padding: '0.5rem 1.1rem', background: 'rgba(80,120,255,0.12)', border: '1px solid rgba(80,120,255,0.25)', borderRadius: 8, fontSize: 13, color: '#8aacff' }}>
              <div style={{ fontSize: '0.65rem', color: '#4a5a8a', marginBottom: 2, letterSpacing: 1 }}>멘탈</div>
              <div style={{ fontWeight: 700 }}>{m >= 0 ? '+' : ''}{m}</div>
            </div>
            <div style={{ padding: '0.5rem 1.1rem', background: 'rgba(80,200,180,0.1)', border: '1px solid rgba(80,200,180,0.2)', borderRadius: 8, fontSize: 13, color: '#6adfc8' }}>
              <div style={{ fontSize: '0.65rem', color: '#3a6a5a', marginBottom: 2, letterSpacing: 1 }}>팀유대</div>
              <div style={{ fontWeight: 700 }}>{t >= 0 ? '+' : ''}{t}</div>
            </div>
          </div>

          {/* Key use popup — only for ending_growth with the key */}
          {showKeyPopup && (
            <div style={{ marginTop: 8, padding: '14px 20px', background: 'rgba(10,20,60,0.92)', border: '1px solid rgba(180,160,80,0.5)', borderRadius: 10, maxWidth: 320 }}>
              <div style={{ fontSize: '0.7rem', color: '#c8a83a', letterSpacing: '0.15em', marginBottom: 6 }}>🗝 아이템</div>
              <div style={{ fontSize: '0.9rem', color: '#f0e8c0', marginBottom: 10 }}>이름 모를 열쇠를 사용하시겠습니까?</div>
              <button
                onClick={useKey}
                style={{ padding: '0.5rem 1.4rem', background: 'rgba(180,150,40,0.25)', border: '1px solid rgba(200,170,60,0.6)', color: '#f0d870', borderRadius: 7, cursor: 'pointer', fontSize: '0.85rem', fontWeight: 700 }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(180,150,40,0.45)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(180,150,40,0.25)')}
              >
                사용
              </button>
            </div>
          )}

          {/* 진엔딩 힌트 — 성장 엔딩이 아닐 때 */}
          {showTrueEndingHint && (
            <div style={{ marginTop: 4, padding: '16px 22px', background: 'rgba(6,10,30,0.9)', border: '1px solid rgba(100,80,200,0.4)', borderRadius: 10, maxWidth: 340, textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#7a6aaa', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: 6 }}>🔒 숨겨진 엔딩</div>
              <div style={{ fontSize: '0.92rem', color: '#c8b8ff', marginBottom: 12, lineHeight: 1.6 }}>진엔딩이 존재한다</div>
              <button
                onClick={tryTrueEnding}
                style={{ padding: '0.5rem 1.3rem', background: 'rgba(80,50,180,0.3)', border: '1px solid rgba(120,90,255,0.55)', color: '#b8a0ff', borderRadius: 7, cursor: 'pointer', fontSize: '0.82rem', fontWeight: 700, letterSpacing: '0.05em' }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(80,50,180,0.55)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(80,50,180,0.3)')}
              >
                마지막 분기로 돌아가기 (멘탈 +2 · 팀유대 +2)
              </button>
            </div>
          )}

          <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
            <button onClick={restart} style={{ padding: '0.65rem 2rem', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.25)', color: '#dbe8ff', borderRadius: 8, cursor: 'pointer', fontSize: 14 }}>
              처음부터
            </button>
            <button onClick={toggleBgm} style={{ padding: '0.65rem 1rem', background: bgmOn ? 'rgba(60,90,200,0.3)' : 'rgba(40,40,50,0.5)', border: `1px solid ${bgmOn ? 'rgba(106,143,255,0.5)' : 'rgba(80,80,100,0.4)'}`, color: bgmOn ? '#8aacff' : '#555', borderRadius: 8, cursor: 'pointer', fontSize: 12 }}>
              {bgmOn ? '♪ BGM ON' : '♪ BGM OFF'}
            </button>
          </div>
        </div>
      ) : (
        /* ── GAME SCREEN ── */
        <div
          style={{ position: 'relative', width: isMobileGame ? 'min(100vw, calc(100vh * 16 / 9))' : '100%', aspectRatio: '16/9', overflow: 'hidden', background: '#000', borderRadius: isMobileGame ? 0 : 4, cursor: (currentBeat?.kind === 'choice' || currentBeat?.kind === 'photo') ? 'default' : 'pointer', userSelect: 'none' }}
          onClick={(currentBeat?.kind !== 'choice' && currentBeat?.kind !== 'photo') ? advance : undefined}
          onMouseDown={e => e.preventDefault()}
        >
          {/* Background */}
          {state.bg
            ? <img src={BG_URL(state.bg)} alt="" decoding="async" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
            : <div style={{ position: 'absolute', inset: 0, background: '#000' }} />
          }
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.18)' }} />

          {/* Characters */}
          {state.chars.map(ch => (
            <img key={ch.id} src={CHAR_URL(ch.id as CharId)} alt={CHAR_INFO[ch.id as CharId]?.name} decoding="async" style={getCharStyle(ch.pos, ch.id)} />
          ))}

          {/* Item acquisition popup */}
          {itemNotif && (
            <div style={{ position: 'absolute', top: '42%', left: '50%', zIndex: 15, pointerEvents: 'none', animation: 'itemPop 3.8s ease forwards' }}>
              <div style={{ background: 'linear-gradient(160deg,rgba(18,14,6,0.97),rgba(28,22,4,0.97))', border: '1px solid rgba(210,175,60,0.75)', borderRadius: 12, padding: '18px 28px', textAlign: 'center', boxShadow: '0 0 32px rgba(180,150,30,0.3), 0 8px 24px rgba(0,0,0,0.7)', minWidth: 200 }}>
                <div style={{ fontSize: '1.4rem', marginBottom: 6 }}>🗝</div>
                <div style={{ fontSize: '0.68rem', color: '#a07830', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: 4 }}>아이템 획득</div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: '#f0d870', letterSpacing: '0.05em' }}>[{itemNotif}]</div>
              </div>
            </div>
          )}

          {/* TOP-LEFT: Stats box */}
          <div style={{ position: 'absolute', top: 10, left: 10, display: 'flex', gap: 6, pointerEvents: 'none' }}>
            <div style={{ position: 'relative' }}>
              <div style={{ padding: '5px 10px', background: 'rgba(4,8,28,0.82)', border: '1px solid rgba(80,120,255,0.35)', borderRadius: 6 }}>
                <div style={{ fontSize: '0.67rem', color: '#4a5a8a', letterSpacing: '0.1em', marginBottom: 1 }}>멘탈</div>
                <div style={{ fontSize: '0.94rem', fontWeight: 700, color: m >= 0 ? '#8aacff' : '#ff7a7a', lineHeight: 1 }}>{m >= 0 ? '+' : ''}{m}</div>
              </div>
              {statDelta?.m !== undefined && statDelta.m !== 0 && (
                <div key={`m-${statDelta.key}`} style={{ position: 'absolute', top: -4, left: '50%', transform: 'translateX(-50%)', fontSize: '0.9rem', fontWeight: 800, color: statDelta.m > 0 ? '#75e8ff' : '#ff7a7a', animation: 'statFloat 1.5s ease forwards', whiteSpace: 'nowrap', textShadow: '0 0 8px rgba(0,0,0,0.9)' }}>
                  {statDelta.m > 0 ? `+${statDelta.m}` : `${statDelta.m}`}
                </div>
              )}
            </div>
            <div style={{ position: 'relative' }}>
              <div style={{ padding: '5px 10px', background: 'rgba(4,8,28,0.82)', border: '1px solid rgba(80,200,160,0.3)', borderRadius: 6 }}>
                <div style={{ fontSize: '0.67rem', color: '#3a6a5a', letterSpacing: '0.1em', marginBottom: 1 }}>팀유대</div>
                <div style={{ fontSize: '0.94rem', fontWeight: 700, color: '#6adfc8', lineHeight: 1 }}>{t >= 0 ? '+' : ''}{t}</div>
              </div>
              {statDelta?.t !== undefined && statDelta.t !== 0 && (
                <div key={`t-${statDelta.key}`} style={{ position: 'absolute', top: -4, left: '50%', transform: 'translateX(-50%)', fontSize: '0.9rem', fontWeight: 800, color: statDelta.t > 0 ? '#6adfc8' : '#ff7a7a', animation: 'statFloat 1.5s ease forwards', whiteSpace: 'nowrap', textShadow: '0 0 8px rgba(0,0,0,0.9)' }}>
                  {statDelta.t > 0 ? `+${statDelta.t}` : `${statDelta.t}`}
                </div>
              )}
            </div>
          </div>

          {/* TOP-RIGHT: BGM button */}
          <button
            onClick={e => { e.stopPropagation(); toggleBgm(); }}
            style={{ position: 'absolute', top: 10, right: 10, padding: '5px 10px', background: bgmOn ? 'rgba(30,55,140,0.75)' : 'rgba(20,20,30,0.75)', border: `1px solid ${bgmOn ? 'rgba(106,143,255,0.5)' : 'rgba(80,80,100,0.4)'}`, borderRadius: 6, color: bgmOn ? '#8aacff' : '#555', cursor: 'pointer', fontSize: '0.84rem', fontWeight: 600, lineHeight: 1.4 }}
          >
            {bgmOn ? '♪ ON' : '♪ OFF'}
          </button>

          {/* Photo overlay */}
          {currentBeat?.kind === 'photo' && (
            <div
              style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.75)', cursor: 'pointer' }}
              onClick={advance}
            >
              <div style={{ position: 'relative', maxWidth: '70%', maxHeight: '80%' }}>
                <img src={currentBeat.src} alt="인생네컷" style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain', borderRadius: 6, boxShadow: '0 8px 40px rgba(0,0,0,0.8)' }} />
                <div style={{ position: 'absolute', bottom: -28, left: 0, right: 0, textAlign: 'center', fontFamily: 'monospace', fontSize: '0.68rem', color: '#666', letterSpacing: '0.1em' }}>클릭하여 계속</div>
              </div>
            </div>
          )}

          {/* Dialogue box */}
          {currentBeat?.kind !== 'choice' && currentBeat?.kind !== 'photo' && (
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(4,8,28,0.91)', borderTop: '1px solid rgba(80,130,255,0.2)', padding: '14px 22px 16px', minHeight: '21%' }}>
              {currentBeat?.kind === 'dialogue' && (
                <div style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 5, color: CHAR_INFO[currentBeat.who]?.color || '#fff', letterSpacing: 1.5 }}>
                  {CHAR_INFO[currentBeat.who]?.name}
                </div>
              )}
              <div key={textKey} style={{ fontSize: '1.07rem', color: '#eaf1ff', lineHeight: 1.9, animation: 'vnFadeIn 0.2s ease', userSelect: 'none' }}>
                {(currentBeat?.kind === 'narration' || currentBeat?.kind === 'dialogue') ? currentBeat.text : null}
              </div>
              <div style={{ position: 'absolute', bottom: 8, right: 14, width: 7, height: 7, borderBottom: '2px solid #6a8fff', borderRight: '2px solid #6a8fff', transform: 'rotate(45deg)', animation: 'blink 1.2s infinite' }} />
            </div>
          )}

          {/* Choices overlay */}
          {currentBeat?.kind === 'choice' && (
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.52)' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, width: '68%', maxWidth: 520 }}>
                {currentBeat.options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => choose(i)}
                    style={{ padding: '0.75rem 1.1rem', background: 'rgba(15,28,75,0.92)', border: '1px solid rgba(90,140,255,0.4)', color: '#d8e8ff', borderRadius: 8, cursor: 'pointer', fontSize: '1rem', lineHeight: 1.6, textAlign: 'center', letterSpacing: '-0.04em', whiteSpace: 'nowrap' }}
                    onMouseEnter={e => (e.currentTarget.style.background = 'rgba(35,60,150,0.92)')}
                    onMouseLeave={e => (e.currentTarget.style.background = 'rgba(15,28,75,0.92)')}
                  >
                    {opt.text}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
