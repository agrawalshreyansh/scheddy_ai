// components/Header.jsx
'use client';
import React from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useCalendar } from '../context/CalendarContext';

const Header = () => {
  const router = useRouter();
  const { goToPrevious, goToNext, goToToday, getDateRangeString, view, setView } = useCalendar();

  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-gray-200 dark:border-gray-700 px-6 py-3">
      <div className="flex items-center gap-6">
        <button 
          onClick={goToToday}
          className="hidden md:flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800">
          <span>Today</span>
        </button>
        
        <div className="flex items-center gap-1">
          <button 
            onClick={goToPrevious}
            className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20">
            <ChevronLeft size={20} />
          </button>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white min-w-[200px] text-center">{getDateRangeString()}</h3>
          <button 
            onClick={goToNext}
            className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 p-1">
          {['Day', 'Week', 'Month'].map((viewOption) => (
            <button
              key={viewOption}
              onClick={() => setView(viewOption)}
              className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
                view === viewOption
                  ? 'text-white bg-[#137fec]'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20'
              }`}
            >
              {viewOption}
            </button>
          ))}
        </div>
        
        <button
          onClick={() => router.push('/profile')}
          className="h-10 w-10 rounded-full bg-cover bg-center hover:ring-2 hover:ring-[#137fec] transition-all cursor-pointer"
          style={{
            backgroundImage: `url("https://lh3.googleusercontent.com/aida-public/AB6AXuCykV1G_iYJ0U32BQwePm5OQ9rZ20HXpO_ADHX6rORAbh_cdPBydpEW8RfxFLksKVOFcrGi1FmfLazVcG_4-iaB10ovT8UHYgYgh07Q5msVXaNAj6xJv1KT473BlLC1Z7RubtIaeKO8zjBUDERbvDaGBElMG2qlSGUEh5eHxbAw2CX-84A1WPU05HCfVwpUHBn0unTXPUOx6CnS7NPjsAfREuENqu7JvnrRq-38IyIPv2lPESD7N46qnE8XgCfsjRbit_7n67OF8w")`
          }}
          aria-label="Go to profile"
        />
      </div>
    </header>
  );
};

export default Header;