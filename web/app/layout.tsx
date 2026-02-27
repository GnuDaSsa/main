import "./globals.css";
import { ReactNode } from "react";

export const metadata = {
  title: "Between Us",
  description: "데이트 코스 추천 MVP"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
