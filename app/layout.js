import "./globals.css";

export const metadata = {
  title: "InstaTrace Web – Reels, Videos & Images",
  description: "Instagram Private & Collab Media Extractor (POC) – Web UI"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-50">
        {children}
      </body>
    </html>
  );
}
