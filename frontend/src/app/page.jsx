
'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleSignUpClick = () => {
    router.push('/auth');
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-gray-50 dark:bg-[#101922]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gray-50/80 dark:bg-[#101922]/80 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between whitespace-nowrap border-b border-gray-200 dark:border-gray-700 h-20">
            <div className="flex items-center gap-4 text-gray-800 dark:text-white">
              <div className="h-8 w-8 text-[#137fec]">
                <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <g clipPath="url(#clip0_6_330)">
                    <path clipRule="evenodd" d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z" fill="currentColor" fillRule="evenodd"></path>
                  </g>
                  <defs>
                    <clipPath id="clip0_6_330">
                      <rect fill="white" height="48" width="48"></rect>
                    </clipPath>
                  </defs>
                </svg>
              </div>
              <h2 className="text-xl font-bold leading-tight tracking-[-0.015em]">Scheddy AI</h2>
            </div>
            <div className="flex items-center gap-4">
              <button onClick={handleSignUpClick} className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#137fec] text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-[#137fec]/90 transition-colors">
                <span className="truncate">Sign Up</span>
              </button>
              <button className="md:hidden p-2 rounded-md text-gray-600 dark:text-gray-300">
                <span className="material-symbols-outlined">menu</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow pt-20">
        {/* Hero Section */}
        <section className="relative py-24 md:py-32">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-200 dark:from-[#101922] dark:to-gray-900 opacity-50"></div>
          <div className="container mx-auto px-4 relative z-10">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-black leading-tight tracking-[-0.033em] text-gray-900 dark:text-white">
                Your Schedule, Supercharged by AI.
              </h1>
              <p className="mt-4 text-lg md:text-xl font-normal leading-normal text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                Seamlessly manage your time with an intelligent calendar and a personal AI assistant.
              </p>
              <button onClick={handleSignUpClick} className="mt-8 flex mx-auto min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-6 bg-[#137fec] text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-[#137fec]/90 transition-colors">
                <span className="truncate">Get Started for Free</span>
              </button>
            </div>
          </div>
        </section>

        {/* Feature Section 1 */}
        <section className="py-20 bg-gray-50 dark:bg-gray-900/50" id="features">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center gap-12">
              <div className="md:w-1/2">
                <div className="flex flex-col gap-4">
                  <h2 className="text-3xl md:text-4xl font-bold leading-tight tracking-tight text-gray-900 dark:text-white max-w-md">
                    A Familiar Calendar, Reimagined.
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 text-base font-normal leading-normal max-w-md">
                    Our intuitive calendar provides daily, weekly, and monthly views, making it effortless to create and manage your events with powerful time-blocking features.
                  </p>
                </div>
              </div>
              <div className="md:w-1/2">
                <div className="w-full bg-center bg-no-repeat aspect-[4/3] bg-cover rounded-xl shadow-lg" style={{backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuD3U9hBfjoq_25i6YFislsuYbnyxNpmGzGHnh-qgezfsJ3szjEI39znyDKVfH2FDvoJ3mdMaox8INTUSjFfCz-nZyhIjOqFOdn2S5h3gSzwm98ObeAoxXscmAIyHfF6s7VN2fmn17xMJcZZDV6pHehKse62kaF3x5WHZ5EJUAt7ACIqmD-xohGU9eyVI_BMnVJlgN8MEvk_qv40dV7Afwq6BBnP9HBTXDxdqyyVQIyInJVvKNGVavPKYehbeAaQdQQoYY5IgDNrLw")'}}></div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Section 2 */}
        <section className="py-20 bg-gray-50 dark:bg-[#101922]">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row-reverse items-center gap-12">
              <div className="md:w-1/2">
                <div className="flex flex-col gap-4">
                  <h2 className="text-3xl md:text-4xl font-bold leading-tight tracking-tight text-gray-900 dark:text-white max-w-md">
                    Your Personal Scheduling Genius.
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 text-base font-normal leading-normal max-w-md">
                    Let our AI assistant handle the heavy lifting. Get smart reminders, find information instantly, and access your conversation history anytime.
                  </p>
                </div>
              </div>
              <div className="md:w-1/2">
                <div className="w-full bg-center bg-no-repeat aspect-[4/3] bg-cover rounded-xl shadow-lg" style={{backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDQ-td_4VwkLhpMrS1DUTeqy6Fiw7flVn4rsxYzCNLeOtjGNuwZ2Y5en_1uZrqBRUf0DP8UKBzZt5Q2FXiBsfTQbspgGBFFEUankQ6EMelmh5gQT7o_8zchUII33N1xnZZDlI9C7xWYsn1fLObqP3beXapCtGjucXZd0PeIe55NkQg25plOu9MrHQF5VR1eZDHxSWj_oeVPk74WlxcGsTUcqQPswpprzy3QTXE1WF1ljhpPRrxVm4UGGpSg28gdM_cKho1NFIsisQ")'}}></div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">Unlock Peak Productivity</h2>
              <p className="mt-4 text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">Scheddy AI goes beyond simple scheduling. It's your intelligent partner in mastering your time.</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white dark:bg-[#101922] rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-[#137fec]/10 text-[#137fec] mb-4">
                  <span className="material-symbols-outlined">auto_awesome</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Intelligent Scheduling</h3>
                <p className="text-gray-600 dark:text-gray-400">Our AI analyzes your patterns and suggests optimal times for tasks and meetings, saving you hours of planning.</p>
              </div>
              <div className="bg-white dark:bg-[#101922] rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-[#137fec]/10 text-[#137fec] mb-4">
                  <span className="material-symbols-outlined">bolt</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Effortless Automation</h3>
                <p className="text-gray-600 dark:text-gray-400">Automate reminders, follow-ups, and recurring events. Focus on what truly matters, not the busywork.</p>
              </div>
              <div className="bg-white dark:bg-[#101922] rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow">
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-[#137fec]/10 text-[#137fec] mb-4">
                  <span className="material-symbols-outlined">insights</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Actionable Insights</h3>
                <p className="text-gray-600 dark:text-gray-400">Get a clear overview of your time allocation. Identify productivity peaks and optimize your workflow for success.</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 bg-[#137fec]/10 dark:bg-[#137fec]/20">
          <div className="container mx-auto px-4">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Ready to take control of your schedule?</h2>
              <p className="mt-2 text-gray-600 dark:text-gray-300">Join Scheddy AI today and experience the future of time management.</p>
              <button onClick={handleSignUpClick} className="mt-6 flex mx-auto min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-6 bg-[#137fec] text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-[#137fec]/90 transition-colors">
                <span className="truncate">Sign Up Now</span>
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 dark:bg-[#101922] border-t border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 text-[#137fec]">
                <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <g clipPath="url(#clip0_6_330_footer)">
                    <path clipRule="evenodd" d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z" fill="currentColor" fillRule="evenodd"></path>
                  </g>
                  <defs>
                    <clipPath id="clip0_6_330_footer">
                      <rect fill="white" height="48" width="48"></rect>
                    </clipPath>
                  </defs>
                </svg>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">© 2024 Scheddy AI. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
