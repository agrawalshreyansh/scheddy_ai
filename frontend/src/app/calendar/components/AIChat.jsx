// components/AssistantPanel.jsx
'use client';
import React from 'react';
import { History, MessageCircle, Send } from 'lucide-react';

const AssistantPanel = () => {
  const messages = [
    {
      id: 1,
      type: 'ai',
      content: "Hello! How can I assist you with your schedule today?",
    },
    {
      id: 2,
      type: 'user',
      content: "Can you schedule a meeting with the design team for tomorrow afternoon?",
    },
    {
      id: 3,
      type: 'ai',
      content: "Of course. I've scheduled a 'Design Review' for October 22nd at 11:00 AM. Does that work?",
    },
  ];

  return (
    <aside className="w-80 flex-shrink-0 flex-col border-l border-[#101922]/10 dark:border-[#f6f7f8]/10 lg:flex">
      <div className="flex h-full flex-col p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">AI Assistant</h3>
          <div className="flex items-center gap-2">
            <button className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20 transition-colors">
              <History size={16} />
            </button>
            <button className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20 transition-colors">
              <MessageCircle size={16} />
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-grow flex-col">
          <div className="flex-grow space-y-4 overflow-y-auto rounded-lg bg-[#101922]/5 dark:bg-[#f6f7f8]/5 p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.type === 'user' ? 'justify-end' : ''
                }`}
              >
                {message.type === 'ai' && (
                  <div className="h-8 w-8 rounded-full bg-[#137fec] flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">
                    AI
                  </div>
                )}
                
                <div
                  className={`rounded-lg p-3 text-sm ${
                    message.type === 'ai'
                      ? 'bg-white dark:bg-[#101922] text-gray-700 dark:text-gray-300'
                      : 'bg-[#137fec] text-white'
                  }`}
                >
                  <p>{message.content}</p>
                </div>
                
                {message.type === 'user' && (
                  <div
                    className="h-8 w-8 rounded-full bg-cover bg-center flex-shrink-0"
                    style={{
                      backgroundImage: `url("https://lh3.googleusercontent.com/aida-public/AB6AXuCykV1G_iYJ0U32BQwePm5OQ9rZ20HXpO_ADHX6rORAbh_cdPBydpEW8RfxFLksKVOFcrGi1FmfLazVcG_4-iaB10ovT8UHYgYgh07Q5msVXaNAj6xJv1KT473BlLC1Z7RubtIaeKO8zjBUDERbvDaGBElMG2qlSGUEh5eHxbAw2CX-84A1WPU05HCfVwpUHBn0unTXPUOx6CnS7NPjsAfREuENqu7JvnrRq-38IyIPv2lPESD7N46qnE8XgCfsjRbit_7n67OF8w")`
                    }}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 relative">
            <textarea
              placeholder="Ask me anything..."
              className="w-full resize-none rounded-lg border-gray-300 dark:border-gray-700 bg-transparent p-3 pr-12 text-sm text-gray-800 dark:text-gray-200 focus:border-[#137fec] focus:ring-[#137fec]"
              rows="3"
            />
            <button className="absolute right-2 bottom-2 rounded-lg bg-[#137fec] p-2 text-white transition-colors hover:bg-[#137fec]/90">
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default AssistantPanel;