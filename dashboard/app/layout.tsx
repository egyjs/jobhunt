import './globals.css';
import type { Metadata } from 'next';
import React from 'react';

export const metadata: Metadata = {
  title: 'JobApply Dashboard',
  description: 'Monitor job matches and trigger AI-powered applications.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="app-body">
        <main className="app-container">{children}</main>
      </body>
    </html>
  );
}
