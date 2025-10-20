'use client';
import React, { useState, useRef, useEffect } from 'react';
import { History, MessageCircle, Send, Loader2 } from 'lucide-react';
import { sendChatMessage } from '@/lib/api';
import { formatDateTime } from '@/lib/dateUtils';
import { useCalendar } from '../context/CalendarContext';

const AssistantPanel = () => {
  const { refreshEvents } = useCalendar();
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hello! How can I assist you with your schedule today?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Use the API service
      const data = await sendChatMessage(currentInput, conversationId);

      // Store conversation_id from first response
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
        console.log('Conversation started with ID:', data.conversation_id);
      }

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.message,
        timestamp: new Date(),
        action: data.action,
        event: data.event,
        events: data.events,
        rescheduled_events: data.rescheduled_events,
      };

      setMessages(prev => [...prev, aiMessage]);

      // Refresh calendar events if event was created, updated, or deleted
      if (['create_event', 'update_event', 'delete_event'].includes(data.action)) {
        refreshEvents();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        id: 1,
        type: 'ai',
        content: "Hello! How can I assist you with your schedule today?",
        timestamp: new Date(),
      },
    ]);
    setConversationId(null); // Reset conversation_id to null for new conversation
    console.log('Conversation cleared - starting new conversation');
  };

  return (
    <aside className="w-80 flex-shrink-0 flex-col border-l border-[#101922]/10 dark:border-[#f6f7f8]/10 lg:flex">
      <div className="flex h-full flex-col p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">AI Assistant</h3>
            {conversationId && (
              <span 
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-full"
                title={`Conversation ID: ${conversationId}`}
              >
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                Active
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={clearConversation}
              className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20 transition-colors"
              title="Clear conversation and start new"
            >
              <History size={16} />
            </button>
            <button className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20 transition-colors">
              <MessageCircle size={16} />
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-grow flex-col overflow-hidden">
          <div className="flex-1 space-y-4 overflow-y-auto rounded-lg bg-[#101922]/5 dark:bg-[#f6f7f8]/5 p-4 min-h-0">
            {messages.map((message, index) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.type === 'user' ? 'justify-end' : ''
                } animate-fadeIn`}
                style={{
                  animation: `fadeIn 0.3s ease-in ${index * 0.1}s both`
                }}
              >
                {message.type === 'ai' && (
                  <div className="h-8 w-8 rounded-full bg-[#137fec] flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">
                    AI
                  </div>
                )}
                
                <div
                  className={`rounded-lg p-3 text-sm max-w-[75%] ${
                    message.type === 'ai'
                      ? 'bg-white dark:bg-[#101922] text-gray-700 dark:text-gray-300'
                      : 'bg-[#137fec] text-white'
                  } ${message.isError ? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400' : ''}`}
                >
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                  
                  {/* Show single event details */}
                  {message.event && (
                    <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs opacity-75">
                      <p>📅 Event: {message.event.task_title}</p>
                    </div>
                  )}
                  
                  {/* Show multiple events */}
                  {message.events && message.events.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs opacity-75">
                      <p className="font-semibold mb-1">📅 Events ({message.events.length}):</p>
                      {message.events.slice(0, 3).map((evt, idx) => (
                        <p key={idx} className="ml-2">• {evt.task_title || evt.title}</p>
                      ))}
                      {message.events.length > 3 && (
                        <p className="ml-2 italic">... and {message.events.length - 3} more</p>
                      )}
                    </div>
                  )}
                  
                  {/* Show rescheduled events */}
                  {message.rescheduled_events && message.rescheduled_events.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs opacity-75">
                      <p className="font-semibold mb-1">🔄 Rescheduled ({message.rescheduled_events.length}):</p>
                      {message.rescheduled_events.map((evt, idx) => (
                        <p key={idx} className="ml-2">• {evt.task_title || evt.title}</p>
                      ))}
                    </div>
                  )}
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
            {isLoading && (
              <div className="flex items-start gap-3 animate-pulse">
                <div className="h-8 w-8 rounded-full bg-[#137fec] flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">
                  AI
                </div>
                <div className="rounded-lg p-3 text-sm bg-white dark:bg-[#101922] text-gray-700 dark:text-gray-300">
                  <div className="flex items-center gap-2">
                    <Loader2 size={16} className="animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="mt-4 relative">
            <textarea
              placeholder="Ask me anything..."
              className="w-full resize-none rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-[#101922] p-3 pr-12 text-sm text-gray-800 dark:text-gray-200 focus:border-[#137fec] focus:ring-1 focus:ring-[#137fec] outline-none transition-all"
              rows="3"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button 
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className={`absolute right-2 bottom-2 rounded-lg p-2 text-white transition-all ${
                isLoading || !inputValue.trim() 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-[#137fec] hover:bg-[#137fec]/90 hover:scale-105'
              }`}
            >
              {isLoading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default AssistantPanel;