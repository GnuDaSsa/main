import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '공직생활 — 비주얼 노벨',
  description: '성남시청 AI 동아리가 만든 공직 생활 시뮬레이션 비주얼 노벨',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
