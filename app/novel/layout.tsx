import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '공직생활 — 비주얼 노벨',
  description: '성남시청 AI 동아리가 만든 공직 생활 시뮬레이션 비주얼 노벨. 신규 공무원의 첫 해를 선택지로 풀어가는 이야기.',
  openGraph: {
    title: '공직생활 — 비주얼 노벨',
    description: '신규 공무원의 첫 해를 선택지로 풀어가는 이야기',
    images: [{ url: '/novel/start_bg.jpg', width: 1280, height: 720 }],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '공직생활 — 비주얼 노벨',
    description: '신규 공무원의 첫 해를 선택지로 풀어가는 이야기',
    images: ['/novel/start_bg.jpg'],
  },
};

export default function NovelLayout({ children }: { children: React.ReactNode }) {
  return children;
}
