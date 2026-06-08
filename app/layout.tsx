import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "성남시 영조물 배상공제 안내",
  description: "도로·보도 사고 접수 보조 MVP"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
