import './globals.css';

export const metadata = {
  title: 'College AI Assistant',
  description: 'Your intelligent study companion',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}