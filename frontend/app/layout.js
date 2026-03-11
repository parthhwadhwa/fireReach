import "./globals.css";

export const metadata = {
  title: "FireReach – Autonomous Outreach Engine",
  description:
    "Research a company's growth signals and generate personalized outreach in seconds.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
