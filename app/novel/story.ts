export type CharId =
  | 'protagonist' | 'deputy' | 'junior_one' | 'junior_two'
  | 'chief' | 'manager' | 'mayor' | 'district' | 'caller' | 'buddy'
  | 'caller_ice' | 'caller_spring';

export type Position = 'left' | 'center' | 'right' | 'left_low' | 'center_low' | 'right_low' | 'caller';

export interface CharDisplay { id: CharId; pos: Position; }

export type Beat =
  | { kind: 'narration'; text: string }
  | { kind: 'dialogue'; who: CharId; text: string }
  | { kind: 'bg'; name: string }
  | { kind: 'show'; chars: CharDisplay[] }
  | { kind: 'hide'; ids: CharId[] }
  | { kind: 'hideAll' }
  | { kind: 'effects'; mentality?: number; team_bond?: number }
  | { kind: 'item'; name: string; itemId: string }
  | { kind: 'photo'; src: string }
  | { kind: 'choice'; options: { text: string; effects?: { mentality?: number; team_bond?: number }; jump: string }[] }
  | { kind: 'ending'; text: string };

export interface Scene { beats: Beat[]; next?: string; }

export const CHAR_INFO: Record<CharId, { name: string; color: string }> = {
  protagonist: { name: '주인공',  color: '#d9f0ff' },
  deputy:      { name: '차석',    color: '#ffe0b3' },
  junior_one:  { name: '삼석',    color: '#ffd7a8' },
  junior_two:  { name: '사석',    color: '#ffe8c7' },
  chief:       { name: '팀장',    color: '#ffd0d0' },
  manager:     { name: '과장',    color: '#f6c1ff' },
  mayor:       { name: '시장',    color: '#e6e6e6' },
  district:    { name: '구청장',  color: '#e6ffd8' },
  caller:        { name: '민원인',  color: '#ffcccc' },
  caller_ice:    { name: '민원인',  color: '#ffcccc' },
  caller_spring: { name: '민원인',  color: '#ffcccc' },
  buddy:         { name: '동기',    color: '#d0ffd8' },
};


export const BG_URL = (name: string) => `/novel/bg/${name}.png`;


export const CHAR_URL = (id: CharId) => `/novel/chars/${id}_default.png`;

// ── 엔딩 분기 헬퍼 ────────────────────────────────────────────────────
// processToInteractive에서는 변수를 직접 읽을 수 없으므로,
// transfer_end 마지막에 choice 없이 jump만 있는 특수 선택지를 삽입해
// page.tsx의 choose()가 변수 조건을 판단한다.
// 대신 여기서는 4개 엔딩 씬을 별도로 정의하고,
// transfer_end에서 page.tsx가 변수로 분기 씬을 결정한다.
// (구현 편의상 transfer_end 마지막에 kind:'ending_branch' 대신
//  page.tsx에서 processToInteractive 호출 전에 씬을 결정하는 방식으로 처리)

export const STORY: Record<string, Scene> = {
  start: {
    beats: [
      { kind: 'narration', text: '1년의 수험기간 끝에 공무원에 합격했다.' },
      { kind: 'narration', text: '안전한 철밥통의 미래가 나를 기다린다.' },
      { kind: 'narration', text: '적어도 그때의 나는, 그렇게 믿고 있었다.' },
      { kind: 'narration', text: '당신의 직렬은?' },
      { kind: 'choice', options: [{ text: '토목직', jump: 'choose_civil' }] },
    ],
  },

  choose_civil: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'effects', mentality: 1 },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'center' }] },
      { kind: 'narration', text: '토목직.' },
      { kind: 'narration', text: '서류에 적힌 두 글자가 왠지 단단해 보였다.' },
      { kind: 'narration', text: '도로, 하천, 공사, 현장.' },
      { kind: 'narration', text: '어쩐지 세상을 실제로 움직이는 일 같았다.' },
      { kind: 'hide', ids: ['protagonist'] },
    ],
    next: 'appointment_day',
  },

  appointment_day: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'city_hall' },
      { kind: 'narration', text: '9월이었다.' },
      { kind: 'narration', text: '은행나무 잎이 막 노래지기 시작하는 계절에, 발령장을 받으러 시청 대강당에 줄지어 섰다.' },
      { kind: 'narration', text: '선선한 가을 바람이 정장 안으로 스며들었고, 어디선가 금목서 향이 희미하게 났다.' },
      { kind: 'dialogue', who: 'mayor', text: '임용을 축하합니다. 시민을 위해 책임감을 갖고 일해주시기 바랍니다.' },
      { kind: 'narration', text: '시장님의 손에서 임용장을 받는 순간, 드디어 인생이 시작되는 것 같았다.' },
      { kind: 'show', chars: [{ id: 'buddy', pos: 'left' }, { id: 'protagonist', pos: 'right' }] },
      { kind: 'dialogue', who: 'buddy', text: '야, 우리 진짜 공무원 됐다.' },
      { kind: 'dialogue', who: 'protagonist', text: '그러게. 이제 고생 끝이지.' },
      { kind: 'narration', text: '그 말은 오래 가지 못했다.' },
      { kind: 'hideAll' },
      { kind: 'bg', name: 'district_office_exterior' },
      { kind: 'narration', text: '오후에는 곧바로 중원구청으로 이동했다.' },
      { kind: 'dialogue', who: 'district', text: '반갑습니다. 각 부서에서 잘 적응하시길 바랍니다.' },
      { kind: 'narration', text: '인사를 마치고 나는 건설과로 배치되었다.' },
    ],
    next: 'first_desk',
  },

  first_desk: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_construction' },
      { kind: 'narration', text: '사무실 문이 열리자 프린터 소리와 전화벨, 서류 넘기는 소리가 한꺼번에 들이쳤다.' },
      { kind: 'show', chars: [{ id: 'chief', pos: 'right' }] },
      { kind: 'dialogue', who: 'chief', text: '오늘부터 우리 팀에서 일할 신규야. 다들 얼굴만 익혀둬.' },
      { kind: 'narration', text: '과장, 팀장, 차석, 삼석, 사석.' },
      { kind: 'narration', text: '그리고 맨 끝에 나.' },
      { kind: 'hide', ids: ['chief'] },
      { kind: 'show', chars: [{ id: 'manager', pos: 'left' }] },
      { kind: 'dialogue', who: 'manager', text: '밥 많이 먹어라. 계속 배고플테니까.' },
      { kind: 'hide', ids: ['manager'] },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'left' }] },
      { kind: 'dialogue', who: 'deputy', text: '이쪽 와서 앉아요. 오늘부터 여기 자리 써요.' },
      { kind: 'hide', ids: ['deputy'] },
      { kind: 'show', chars: [{ id: 'junior_one', pos: 'left' }] },
      { kind: 'dialogue', who: 'junior_one', text: '모르면 메모부터 해요. 나중에 진짜 기억 안 납니다.' },
      { kind: 'hide', ids: ['junior_one'] },
      { kind: 'show', chars: [{ id: 'junior_two', pos: 'right' }] },
      { kind: 'dialogue', who: 'junior_two', text: '전화 오면 일단 떨지 말고, 누가 언제 뭘 원하는지만 적어요.' },
      { kind: 'hide', ids: ['junior_two'] },
      { kind: 'narration', text: '여기저기 인사를 드리고 안내받은 자리에 앉았다.' },
      { kind: 'narration', text: '책상에는 먼지가 수북했고, 모니터 옆엔 이름 모를 열쇠 하나가 굴러다니고 있었다.' },
      { kind: 'item', name: '이름 모를 열쇠', itemId: 'mystery_key' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'right' }] },
      { kind: 'dialogue', who: 'protagonist', text: '이게 뭐지...' },
      { kind: 'narration', text: '그 찰나, 전화가 울렸다.' },
    ],
    next: 'first_call',
  },

  first_call: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'show', chars: [{ id: 'caller', pos: 'caller' }] },
      { kind: 'dialogue', who: 'caller', text: '여보세요? 도로 파헤쳐놓고 왜 아직도 정리를 안 해요?' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'left' }] },
      { kind: 'dialogue', who: 'protagonist', text: '아, 제가 오늘 처음 와서...' },
      { kind: 'dialogue', who: 'caller', text: '처음 오면 아무것도 안 해도 돼요? 담당이면 책임을 져야지!' },
      { kind: 'narration', text: '욕은 아니었지만, 욕보다 더 선명하게 아팠다.' },
      { kind: 'effects', mentality: -1 },
      { kind: 'hide', ids: ['caller'] },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'right' }] },
      { kind: 'dialogue', who: 'deputy', text: '일단 메모해요. 위치, 연락처, 뭐가 문제인지.' },
      { kind: 'dialogue', who: 'deputy', text: '그리고 이 파일이랑 이 종이 두 장. 전임자가 남긴 인수인계예요.' },
      { kind: 'narration', text: '파일은 뒤죽박죽 정리된 공사 서류철이었고, 종이 두 장에는 공사명과 업체명, 민원 다발 지점만 적혀 있었다.' },
      { kind: 'dialogue', who: 'deputy', text: '지금부터 이 구간 공사 담당은 당신이에요. 책임감 있어야 해요.' },
      { kind: 'dialogue', who: 'protagonist', text: '네...' },
      { kind: 'narration', text: '근데 진짜 하나도 무슨 소린지 모르겠다.' },
      { kind: 'choice', options: [
        { text: '일단 아는 척하며 메모부터 정리한다', effects: { mentality: 1 }, jump: 'early_days' },
        { text: '솔직하게 잘 모르겠다고 다시 묻는다', effects: { team_bond: 2 }, jump: 'early_days' },
        { text: '인수인계 파일을 혼자 밤새 분석해보기로 한다', effects: { mentality: 2 }, jump: 'early_days' },
      ]},
    ],
  },

  early_days: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'narration', text: '그날 이후로는 매일이 속도전이었다.' },
      { kind: 'narration', text: '결재선, 설계변경, 준공계, 기성검사.' },
      { kind: 'narration', text: '단어는 계속 들리는데 문장은 끝까지 이해되지 않았다.' },
      { kind: 'show', chars: [{ id: 'chief', pos: 'right' }, { id: 'manager', pos: 'left' }] },
      { kind: 'dialogue', who: 'chief', text: '오전에 현장 나갔다 와서 보고 올리고, 업체에도 전화 넣어.' },
      { kind: 'dialogue', who: 'manager', text: '민원 들어오면 혼자 끌어안지 말고 꼭 보고해.' },
      { kind: 'hide', ids: ['chief', 'manager'] },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'left' }] },
      { kind: 'dialogue', who: 'deputy', text: '모르면 물어봐요. 대신 같은 걸 세 번은 묻지 말고.' },
      { kind: 'hide', ids: ['deputy'] },
      { kind: 'show', chars: [{ id: 'junior_one', pos: 'left' }, { id: 'junior_two', pos: 'right' }] },
      { kind: 'dialogue', who: 'junior_one', text: '처음 3개월은 원래 다 멍합니다.' },
      { kind: 'dialogue', who: 'junior_two', text: '저도 아직 멍해요.' },
      { kind: 'narration', text: '하루 종일 정신없이 움직이다 보면 퇴근 무렵엔 내가 뭘 한 건지 설명도 못 하겠는데, 이상하게 다음 날 아침엔 또 출근하고 있었다.' },
    ],
    next: 'winter_arc',
  },

  winter_arc: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'winter_road' },
      { kind: 'narration', text: '계절이 바뀌고 겨울이 왔다.' },
      { kind: 'narration', text: '건설과의 공기는 더 차가워졌고, 설해대책 기간이 시작되었다.' },
      { kind: 'show', chars: [{ id: 'chief', pos: 'left' }] },
      { kind: 'dialogue', who: 'chief', text: '오늘 밤 눈 예보 있어. 비상대기 걸릴 수 있으니까 핸드폰 소리 키워둬.' },
      { kind: 'narration', text: '새벽에 울리는 단체 연락, 제설재 확인, 민원 대비 연락망.' },
      { kind: 'narration', text: '처음에는 내가 왜 새벽 다섯 시에 도로 결빙 사진을 보고 있는지 이해할 수 없었다.' },
      { kind: 'narration', text: '눈이 오는 밤이면 팀 전체가 지도를 펼쳐놓고 제설 구간을 나눴다.' },
      { kind: 'narration', text: '새벽 세 시에 현장에 나가 염화칼슘을 뿌리고, 동이 틀 무렵에 다시 사무실로 돌아와 보고서를 썼다.' },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'right' }] },
      { kind: 'dialogue', who: 'deputy', text: '주사님, 차 살 생각 있어요?' },
      { kind: 'dialogue', who: 'protagonist', text: '아니요... 왜요?' },
      { kind: 'dialogue', who: 'deputy', text: '아, 우리는 당분간 57시간 넘게 초과를 찍게 될 거에요. 차 사기 딱 좋은 시점이지.' },
      { kind: 'narration', text: '웃자고 한 말인 건 알았다. 그런데 웃음이 나오지 않았다.' },
      { kind: 'hide', ids: ['deputy'] },
      { kind: 'choice', options: [
        { text: '투덜거리면서도 현장 흐름을 몸으로 익힌다', effects: { mentality: 2, team_bond: -1 }, jump: 'winter_relief' },
        { text: '긴장한 채로 매뉴얼을 반복해서 읽으며 버틴다', effects: { mentality: -1, team_bond: 2 }, jump: 'winter_relief' },
        { text: '새벽 출동마다 선배들 곁에 붙어 질문을 쏟아낸다', effects: { mentality: 1, team_bond: 1 }, jump: 'winter_relief' },
      ]},
    ],
  },

  winter_relief: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'narration', text: '그래도 겨울에는 한 가지 위안이 있었다.' },
      { kind: 'narration', text: '3월까지는 추워서 사람들이 덜 싸돌아다닌다.' },
      { kind: 'narration', text: '도로 점용이니 포장 파손이니 주정차 동선이니, 그런 민원이 확실히 줄었다.' },
      { kind: 'narration', text: '사무실 난방 바람을 맞으며 조용한 오전을 보내는 날이면, 아주 잠깐 행복하다는 생각도 들었다.' },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'right' }] },
      { kind: 'dialogue', who: 'deputy', text: '이때 숨 좀 돌려놔요. 4월 오면 다시 시작이니까.' },
      { kind: 'narration', text: '그 말은 예언이었다.' },
      { kind: 'narration', text: '하지만 그 전에, 한 가지 일이 더 있었다.' },
    ],
    next: 'ice_claim',
  },

  ice_claim: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'winter_road' },
      { kind: 'narration', text: '큰 눈이 내린 다음 날 오전이었다.' },
      { kind: 'narration', text: '팀 전체가 새벽부터 나가 제설 작업을 마친 뒤였다. 나도 세 시간 자고 복귀해서 모니터를 붙들고 있었다.' },
      { kind: 'show', chars: [{ id: 'caller_ice', pos: 'caller' }] },
      { kind: 'dialogue', who: 'caller_ice', text: '거기 건설과죠? 아까 보도블록에서 미끄러져서 발목을 삐었는데요.' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'left' }] },
      { kind: 'dialogue', who: 'protagonist', text: '아, 많이 다치셨어요? 지금 병원에 계신가요?' },
      { kind: 'dialogue', who: 'caller_ice', text: '병원 갔다 왔죠. 치료비가 나왔는데, 구청이 눈 관리를 제대로 안 한 거잖아요. 배상해줘야 하는 거 아닌가요?' },
      { kind: 'narration', text: '가슴이 내려앉았다. 배상. 그 단어가 머릿속에서 빙빙 돌았다.' },
      { kind: 'effects', mentality: -1 },
      { kind: 'hide', ids: ['caller_ice'] },
      { kind: 'show', chars: [{ id: 'chief', pos: 'right' }] },
      { kind: 'dialogue', who: 'chief', text: '잠깐. 일단 전화 잠시 대기시켜봐.' },
      { kind: 'dialogue', who: 'chief', text: '일단 미끄러진 위치부터 확인해. 집 앞이냐, 점포 앞이냐. 거기는 소유자나 점유자가 직접 치울 의무가 있어. 우리 구역이 아닐 수 있어.' },
      { kind: 'dialogue', who: 'chief', text: '우리 구역이라 해도, 새벽에 제설 다 했잖아. 강설 자체는 자연재해야. 판례도 마찬가지야. 제설 조치를 다 이행했으면 위기예측 부실로 봐도 지자체 관리하자로 인정 안 해.' },
      { kind: 'dialogue', who: 'chief', text: '영조물 배상 요건이 안 돼. 보험 처리도 마찬가지야. 제설 일지랑 현장 사진 다 있지?' },
      { kind: 'narration', text: '영조물 배상 책임은 국가배상법 제5조에 따른 제도다. 하지만 핵심은 지자체의 설치·관리에 \'하자\'가 있어야 한다는 것.' },
      { kind: 'narration', text: '강설은 자연재해다. 아무리 많은 눈이 와도, 지자체가 제설 조치를 다 했다면 관리하자로 보기 어렵다는 게 판례의 흐름이다.' },
      { kind: 'narration', text: '더구나 집 앞이나 점포 앞 보도는 해당 소유자·점유자가 관리 의무를 진다. 거기서 미끄러진 거라면 지자체 소관조차 아니다.' },
      { kind: 'narration', text: '머릿속이 정리됐다. 이건 배상 요건에 해당하지 않는다. 근데 이걸 어떻게 설명해야 하나.' },
      { kind: 'show', chars: [{ id: 'caller_ice', pos: 'caller' }] },
      { kind: 'dialogue', who: 'caller_ice', text: '뭐라고요? 사람이 다쳤는데 책임이 없다고요?' },
      { kind: 'dialogue', who: 'caller_ice', text: '눈이 오면 미리미리 치워야지, 아침에 사람 다친 다음에 치우면 뭐가 달라요?' },
      { kind: 'dialogue', who: 'caller_ice', text: '이게 나라에서 일하는 사람들이 할 소리예요?' },
      { kind: 'narration', text: '전화기 너머로 분노가 쏟아져 들어왔다.' },
      { kind: 'narration', text: '틀린 말이 아니었다. 그리고 맞는 말도 아니었다.' },
      { kind: 'narration', text: '어떻게 할까.' },
      { kind: 'choice', options: [
        { text: '영조물 배상 책임에 대해 설명한다 (관리하자 없음)', effects: { mentality: -1, team_bond: -1 }, jump: 'choice_explain' },
        { text: '국가배상법에 따른 절차를 안내한다', effects: { mentality: 1, team_bond: 1 }, jump: 'choice_empathy' },
        { text: '배상 대상이 아니라고 단호하게 말한다', effects: { mentality: 2 }, jump: 'choice_escalate' },
      ]},
    ],
  },

  choice_explain: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'center' }, { id: 'caller_ice', pos: 'caller' }] },
      { kind: 'dialogue', who: 'protagonist', text: '영조물 배상 책임은 지자체의 설치·관리에 하자가 있을 때 성립합니다. 강설 자체는 자연재해이고, 저희가 새벽 세 시부터 제설 작업을 완료했습니다. 판례상 이 경우 관리하자로 보기 어렵습니다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '눈이 오면 미리미리 치워놔야 하는 거 아니에요? 아침에 사람 다치고 나서 치우면 무슨 소용이에요.' },
      { kind: 'dialogue', who: 'protagonist', text: '저희가 사고 이전에 이미 제설 작업을 완료했습니다. 사고 시각 이전에 현장에 나갔고 기록도 남아 있습니다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '그게 무슨 말인지 모르겠고요. 사람이 다쳤으면 치료비는 줘야 하는 거 아닌가요?' },
      { kind: 'dialogue', who: 'protagonist', text: '그리고 미끄러지신 장소가 집 앞이나 점포 앞이라면, 그 구간은 소유자가 직접 제설 의무를 지십니다. 저희 관리 구역이 아닐 수도 있어요.' },
      { kind: 'dialogue', who: 'caller_ice', text: '그게 그거 아닌가요? 다 구청이 관리해야 하는 거 아니에요?' },
      { kind: 'narration', text: '세 번을 다르게 설명했다. 그래도 통하지 않았다.' },
      { kind: 'narration', text: '이 답답함을 어떻게 표현해야 할지 몰랐다. 틀린 말을 하는 게 아닌데, 상대방한테 전달이 안 된다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '됐어요. 어디다 신고해야 하는지 알아볼게요.' },
      { kind: 'narration', text: '전화가 끊겼다.' },
      { kind: 'narration', text: '며칠 뒤 국민신문고로 민원이 내려왔고, 결론은 같았다. 배상 요건 미해당.' },
      { kind: 'narration', text: '맞는 말을 했는데도 뭔가 잘못한 것 같은 기분이었다. 설명이 통하지 않는다는 게 이렇게 지치는 일인 줄 몰랐다.' },
      { kind: 'hide', ids: ['caller_ice', 'protagonist'] },
    ],
    next: 'spring_arc',
  },

  choice_empathy: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'center' }, { id: 'caller_ice', pos: 'caller' }] },
      { kind: 'dialogue', who: 'protagonist', text: '많이 놀라셨겠어요. 발목이 많이 다치셨나요?' },
      { kind: 'dialogue', who: 'protagonist', text: '다만 강설은 자연재해로 분류되고, 저희가 사고 이전부터 제설 작업을 완료한 기록이 있어서요. 국가배상법상 이 경우는 지자체의 배상 요건이 충족되지 않습니다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '그러니까 소송을 하라고요? 나 보고 직접 싸우라고요?' },
      { kind: 'dialogue', who: 'protagonist', text: '행정심판이나 민사소송으로 불복하실 수는 있는데, 솔직히 말씀드리면 지자체 과실을 입증하기 어려운 상황이에요. 미리 알고 계셔야 할 것 같아서요.' },
      { kind: 'dialogue', who: 'caller_ice', text: '...' },
      { kind: 'narration', text: '잠시 침묵이 흘렀다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '법대로 하면 나는 그냥 손해 보고 끝나는 거네요.' },
      { kind: 'narration', text: '부정하기 어려운 말이었다. 공감을 표현해도, 결론이 달라지지 않는다는 사실이 가장 힘든 부분이었다.' },
      { kind: 'narration', text: '절차를 안내했지만, 결국 아무것도 해줄 수 없다는 말과 같았다. 그걸 알면서도 해야 하는 설명이었다.' },
      { kind: 'hide', ids: ['caller_ice', 'protagonist'] },
    ],
    next: 'spring_arc',
  },

  choice_escalate: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'center' }, { id: 'caller_ice', pos: 'caller' }] },
      { kind: 'dialogue', who: 'protagonist', text: '죄송합니다. 이 경우는 배상 대상이 아닙니다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '설명도 없이 그냥 안 된다고요?' },
      { kind: 'dialogue', who: 'protagonist', text: '강설은 자연재해입니다. 저희가 사고 이전에 제설 작업을 완료했고, 판례상 이 경우 지자체 관리하자로 인정되지 않습니다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '그게 무슨 말이에요? 사람이 다쳤으면 책임을 져야 하는 거 아닌가요?' },
      { kind: 'dialogue', who: 'protagonist', text: '불복하시려면 국민신문고나 행정심판을 이용하시면 됩니다.' },
      { kind: 'dialogue', who: 'caller_ice', text: '어디다 항의해야 하는지 알려줘요. 이렇게 끝낼 순 없으니까.' },
      { kind: 'narration', text: '국민신문고 주소를 알려주고 전화를 끊었다.' },
      { kind: 'narration', text: '단호하게 답했다. 틀린 건 없었다.' },
      { kind: 'narration', text: '전화를 끊고 나서도 그 목소리가 머릿속에 남았다. 내가 너무 차가웠나. 아니면 이게 맞는 건가.' },
      { kind: 'hide', ids: ['caller_ice', 'protagonist'] },
    ],
    next: 'spring_arc',
  },

  spring_arc: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'spring_street' },
      { kind: 'narration', text: '4월이 되자 민원이 돌아왔다.' },
      { kind: 'narration', text: '금광동 금빛 그랑메종 아파트 재개발 공사가 본격화되면서, 건설과 전화가 부쩍 늘었다.' },
      { kind: 'show', chars: [{ id: 'caller_spring', pos: 'caller' }] },
      { kind: 'dialogue', who: 'caller_spring', text: '거기 건설과죠? 저 금광동 금빛 그랑메종 입주민인데요, 공사 시작하고 나서 차들이 우리 아파트 앞 도로를 무단 주차 구간으로 쓰고 있어요.' },
      { kind: 'dialogue', who: 'caller_spring', text: '시선유도봉 좀 설치해주세요. 그거 설치하면 차들이 못 세울 거 아닌가요.' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'left' }] },
      { kind: 'dialogue', who: 'protagonist', text: '시선유도봉이라고 하시면... 혹시 차량 진입을 막는 볼라드나 주차금지봉 말씀하시는 건가요?' },
      { kind: 'dialogue', who: 'caller_spring', text: '아니 그게 그거 아닌가요? 아무튼 그 봉 같은 거요. 도로에 박아서 차 못 세우게 하는.' },
      { kind: 'narration', text: '시선유도봉은 야간에 운전자 시선을 유도하는 반사성 도로안전시설이다.' },
      { kind: 'narration', text: '주차금지봉이나 볼라드와는 전혀 다른 물건이고, 도로안전시설 설치·관리 규정상 설치 위치와 목적이 엄격히 정해져 있다.' },
      { kind: 'narration', text: '즉, 민원인이 원하는 용도로는 시선유도봉을 설치할 수 없었다.' },
      { kind: 'dialogue', who: 'caller_spring', text: '어쨌든 뭔가 설치해줘서 차를 못 세우게 해달라는 거예요. 그게 그렇게 어려운 일인가요?' },
      { kind: 'dialogue', who: 'caller_spring', text: '옆 단지는 됐다고 하던데, 우리는 왜 안 돼요?' },
      { kind: 'narration', text: '\'옆 단지는 됐다\'는 말 — 십중팔구 아파트 사유지 안에 관리소 측이 자체적으로 세운 것이다. 지자체가 도로 위에 박아준 게 아니다.' },
      { kind: 'narration', text: '도로안전시설 설치·관리에 관한 규칙상 시선유도봉은 안전지대, 차선 변경 구간 등 시선 유도가 실제로 필요한 구간에만 설치할 수 있다. 주차를 막겠다고 도로 위에 임의로 박는 건 위법이다.' },
      { kind: 'narration', text: '내가 해줄 수 있는 게 없다. 법이 그렇게 돼있다. 근데 이걸 어떻게 받아들이게 할 수 있을까.' },
      { kind: 'choice', options: [
        { text: '규정을 내세워 끝까지 안 된다고 버틴다', effects: { mentality: 1, team_bond: 1 }, jump: 'spring_defend' },
        { text: '왜 안 되는지 차분히 설명하고, 가능한 다른 방법을 함께 찾아본다', effects: { mentality: -1, team_bond: 2 }, jump: 'spring_defend' },
        { text: '민원이 너무 악질이다. 법 취지는 맞지 않지만 어떻게든 대안을 찾아 마무리해버린다', effects: { team_bond: 1 }, jump: 'spring_yield' },
      ]},
    ],
  },

  spring_defend: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'center' }, { id: 'caller_spring', pos: 'caller' }] },
      { kind: 'dialogue', who: 'protagonist', text: '시선유도봉은 도로안전시설 설치·관리에 관한 규칙에 따라 안전지대, 차선 변경 구간 등 실제로 시선 유도가 필요한 구간에만 설치할 수 있습니다. 주차를 막는 용도로는 설치가 불가합니다.' },
      { kind: 'dialogue', who: 'caller_spring', text: '그러면 뭘 설치해줄 수 있어요?' },
      { kind: 'dialogue', who: 'protagonist', text: '도로 구간에 임의로 주차금지 시설물을 설치하는 건 도로법 위반이 될 수 있습니다. 불법 주차 차량은 불법주차 신고나 단속 강화 요청으로 대응하시는 게 맞습니다.' },
      { kind: 'dialogue', who: 'caller_spring', text: '그게 다예요? 담당자가 의지가 없는 거 아닌가요? 옆 단지는 됐다는데.' },
      { kind: 'narration', text: '이를 악물었다. 의지가 없는 게 아니었다. 법이 그렇게 돼 있는 거다. 여기서 눈치 봐서 해줬다간 내가 위법을 저지르는 거다.' },
      { kind: 'dialogue', who: 'protagonist', text: '옆 단지는 아파트 사유지 안에 관리소 측에서 자체 설치한 겁니다. 저희가 도로에 설치해드린 게 아닙니다. 허용 범위 밖의 시설 설치는 저희가 할 수 없습니다.' },
      { kind: 'dialogue', who: 'caller_spring', text: '이렇게 무책임할 수가 있어요? 국민 세금으로 일하면서.' },
      { kind: 'narration', text: '전화를 끊고 나서도 손이 떨렸다.' },
      { kind: 'narration', text: '맞는 말을 했다. 법적으로도, 행정적으로도 흠 잡을 게 없었다. 그런데 왜 이렇게 지치는 건지 몰랐다.' },
      { kind: 'hide', ids: ['caller_spring', 'protagonist'] },
    ],
    next: 'spring_resolution',
  },

  spring_yield: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'show', chars: [{ id: 'protagonist', pos: 'center' }, { id: 'caller_spring', pos: 'caller' }] },
      { kind: 'dialogue', who: 'protagonist', text: '...잠시 확인해볼게요.' },
      { kind: 'narration', text: '통화를 보류했다.' },
      { kind: 'hide', ids: ['caller_spring'] },
      { kind: 'show', chars: [{ id: 'manager', pos: 'right' }] },
      { kind: 'dialogue', who: 'protagonist', text: '팀장님, 이 민원 어떻게 마무리할 방법이 없을까요. 규정상 시선유도봉은 안 되는데...' },
      { kind: 'dialogue', who: 'manager', text: '...해당 구간 현황 뽑아봐. 도로 선형이나 교통 안전 목적으로 설치 가능한 명분이 있나 보고.' },
      { kind: 'hide', ids: ['manager'] },
      { kind: 'narration', text: '법적으로 내 주장이 맞는다는 건 알았다. 시선유도봉을 거기 설치하면 안 된다. 그것도 알았다.' },
      { kind: 'narration', text: '하지만 이 민원인은 절대 받아들이지 않을 것 같았다. 계속 싸우는 것도 비용이다.' },
      { kind: 'narration', text: '며칠 후, 억지로 명분을 찾아냈다. 교통 안전이라는 이름을 붙이면 설치가 불가능하지는 않은 구간이었다.' },
      { kind: 'show', chars: [{ id: 'caller_spring', pos: 'caller' }] },
      { kind: 'dialogue', who: 'caller_spring', text: '어, 됐어요? 왜 처음부터 이렇게 안 해줬어요?' },
      { kind: 'narration', text: '대답하지 않았다.' },
      { kind: 'narration', text: '이게 맞는 건지 아직도 모르겠다. 법 취지대로라면 이렇게 하면 안 됐다. 그런데 민원은 닫혔다.' },
      { kind: 'hide', ids: ['caller_spring', 'protagonist'] },
    ],
    next: 'spring_resolution',
  },

  spring_resolution: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'narration', text: '봄 민원이 지나갔다.' },
      { kind: 'narration', text: '어떤 식으로 마무리가 됐든, 민원이 닫히고 나면 이상하게도 공허한 감각이 남았다.' },
      { kind: 'narration', text: '민원은 문제 하나만 담고 오는 게 아니라, 사람의 조급함과 억울함과 기대까지 같이 실려 온다는 걸 알게 됐다.' },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'left' }, { id: 'manager', pos: 'right' }] },
      { kind: 'dialogue', who: 'deputy', text: '버티는 것도 실력이에요.' },
      { kind: 'dialogue', who: 'manager', text: '그래도 너, 처음보단 표정이 덜 놀라네.' },
      { kind: 'narration', text: '그 말이 칭찬인지 위로인지는 모르겠지만, 이상하게 오래 남았다.' },
    ],
    next: 'transfer_end',
  },

  transfer_end: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_evening' },
      { kind: 'narration', text: '그렇게 정신없이 계절이 한 바퀴 돌았다.' },
      { kind: 'narration', text: '모든 게 익숙해질 즈음, 인사이동 명단이 내려왔다.' },
      { kind: 'show', chars: [{ id: 'buddy', pos: 'left' }] },
      { kind: 'dialogue', who: 'buddy', text: '야, 나 다른 동으로 간다.' },
      { kind: 'hide', ids: ['buddy'] },
      { kind: 'show', chars: [{ id: 'deputy', pos: 'left' }, { id: 'protagonist', pos: 'right' }] },
      { kind: 'dialogue', who: 'deputy', text: '저도 이번에 이동이에요. 다음 담당자 오면 파일 위치부터 알려줘야겠네.' },
      { kind: 'show', chars: [{ id: 'junior_one', pos: 'center' }] },
      { kind: 'dialogue', who: 'junior_one', text: '차석님 가시면 팀 분위기 진짜 달라지겠는데요.' },
      { kind: 'hide', ids: ['junior_one'] },
      { kind: 'show', chars: [{ id: 'junior_two', pos: 'center' }] },
      { kind: 'dialogue', who: 'junior_two', text: '이제 나는 누구 뒤에 숨어야 하지...' },
      { kind: 'hide', ids: ['junior_two'] },
      { kind: 'dialogue', who: 'protagonist', text: '이제 좀 알 것 같았는데, 또 바뀌네요.' },
      { kind: 'dialogue', who: 'deputy', text: '원래 그런 거예요. 남는 사람도 있고, 가는 사람도 있고.' },
      { kind: 'narration', text: '정든 사람들과 인사를 나누는 순간, 입직 첫날보다 더 이상한 기분이 들었다.' },
      { kind: 'narration', text: '도망치고 싶던 곳인데, 막상 떠난다니 아쉬웠다.' },
    ],
    // 엔딩은 page.tsx에서 변수를 보고 분기
    next: 'ending_branch',
  },

  // ── 변수 분기용 더미 씬 (page.tsx가 변수 체크 후 실제 엔딩 씬으로 redirect) ──
  ending_branch: {
    beats: [],
    // page.tsx의 processToInteractive가 이 씬에서 변수 조건으로 분기
  },

  // ── 엔딩 1: 성장 (mentality≥2 & team_bond≥3) ─────────────────────
  ending_growth: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_evening' },
      { kind: 'narration', text: '1년 전의 나는 철밥통을 상상했다.' },
      { kind: 'narration', text: '지금의 나는, 민원인의 목소리가 욕이어도 일단 끝까지 듣는다.' },
      { kind: 'narration', text: '새벽 세 시에 제설재를 뿌리며, 이게 내 일이라고 생각하게 되었다.' },
      { kind: 'narration', text: '힘들었지만, 단단해졌다.' },
      { kind: 'narration', text: '그리고 내일도 아마, 전화벨 소리와 함께 공무원 인생은 계속될 것이다.' },
      { kind: 'ending', text: '성장 엔딩 — 1년 차 토목직, 단단해지다' },
    ],
  },

  // ── 엔딩 1-B: 성장 + 열쇠 사용 ───────────────────────────────────
  ending_growth_key: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_evening' },
      { kind: 'narration', text: '바빠서 한 번도 열어보지 못했던 캐비닛을 열었다.' },
      { kind: 'narration', text: '오래된 잠금장치가 툭, 하고 열렸다.' },
      { kind: 'photo', src: '/novel/items/life4cut.jpg' },
      { kind: 'narration', text: '첫 회식 때 찍었던 인생네컷이었다.' },
      { kind: 'narration', text: '그때의 우리는 다들 어색하게 웃고 있었다.' },
      { kind: 'narration', text: '힘들지만 낭만있었다.' },
      { kind: 'narration', text: '그리고 내일도 아마, 전화벨 소리와 함께 공무원 인생은 계속될 것이다.' },
      { kind: 'ending', text: '성장 엔딩 — 힘들지만 낭만있었다' },
    ],
  },

  // ── 엔딩 2: 동료 의지 (mentality<0 & team_bond≥3) ─────────────────
  ending_team: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_evening' },
      { kind: 'narration', text: '솔직히 말하면 많이 지쳤다.' },
      { kind: 'narration', text: '민원을 받을 때마다 심장이 쪼그라드는 느낌은 1년이 지나도 사라지지 않았다.' },
      { kind: 'narration', text: '그래도 버틸 수 있었던 건, 옆자리 사람들 때문이었다.' },
      { kind: 'narration', text: '먼저 물어봐 주는 차석, 실없이 웃게 해주는 삼석과 사석.' },
      { kind: 'narration', text: '혼자였으면 진작 쓰러졌을 것이다.' },
      { kind: 'narration', text: '내일도 지치겠지만, 그래도 출근할 수 있을 것 같다.' },
      { kind: 'ending', text: '동료 의지 엔딩 — 혼자는 아니었다' },
    ],
  },

  // ── 엔딩 3: 독야청청 (mentality≥2 & team_bond<2) ──────────────────
  ending_solo: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_evening' },
      { kind: 'narration', text: '1년 동안 약해지지 않으려고 버텼다.' },
      { kind: 'narration', text: '민원이 와도, 상사가 채근해도, 업체가 핑계를 대도 — 흔들리지 않는 법을 배웠다.' },
      { kind: 'narration', text: '대신 어느 순간부터, 팀 회식 자리가 불편해졌다.' },
      { kind: 'narration', text: '같이 웃는 법을 잊어버린 것 같기도 했다.' },
      { kind: 'narration', text: '강해진 건지, 차가워진 건지.' },
      { kind: 'narration', text: '그 차이를 아직 잘 모르겠다.' },
      { kind: 'ending', text: '독야청청 엔딩 — 강해졌지만, 혼자다' },
    ],
  },

  // ── 엔딩 4: 번아웃 (기타) ─────────────────────────────────────────
  ending_burnout: {
    beats: [
      { kind: 'hideAll' },
      { kind: 'bg', name: 'office_evening' },
      { kind: 'narration', text: '1년이 지났는데, 출근길이 여전히 무겁다.' },
      { kind: 'narration', text: '철밥통이라는 말이 이제는 농담으로도 들리지 않는다.' },
      { kind: 'narration', text: '민원 전화가 울리면 아직도 심장이 먼저 반응하고, 퇴근하고 나서도 업무 생각이 끊기지 않는다.' },
      { kind: 'narration', text: '취업 공고를 검색해본 게 한두 번이 아니었다.' },
      { kind: 'narration', text: '아직 결심은 못 했다.' },
      { kind: 'narration', text: '그냥, 내일은 조금 달랐으면 좋겠다.' },
      { kind: 'ending', text: '번아웃 엔딩 — 아직 결심은 못 했다' },
    ],
  },
};
