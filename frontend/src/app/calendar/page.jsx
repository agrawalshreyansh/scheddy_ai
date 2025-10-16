// app/page.jsx
'use client';
import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import MainContent from './components/CalendarView';
import AssistantPanel from './components/AIChat';
import { CalendarProvider } from './context/CalendarContext';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const storedUser = localStorage.getItem('user');
    console.log('Stored user:', storedUser);
    if (!storedUser) {
      router.push('/auth');
      return;
    }

    try {
      const userData = JSON.parse(storedUser);
      // Check if user has uuid/id
      if (!userData.user_id && !userData.email) {
        router.push('/auth');
      }
    } catch (error) {
      console.error('Error parsing user data from localStorage:', error);
      router.push('/auth');
    }
  }, [router]);

  return (
    <CalendarProvider>
      <div className="font-display bg-[#f6f7f8] dark:bg-[#101922] h-screen overflow-hidden">
        <div className="flex h-full w-full">
          <Sidebar />
          <div className="flex flex-1 flex-col h-full overflow-hidden">
            <Header />
            <main className="flex flex-1 overflow-hidden">
              <MainContent />
              <AssistantPanel />
            </main>
          </div>
        </div>
      </div>
    </CalendarProvider>
  );
}