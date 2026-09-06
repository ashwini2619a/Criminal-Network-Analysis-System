import { useState, useCallback } from 'react';
import { ChatMessage } from '../types';
import * as api from '../lib/api';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    const newMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content,
      timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false })
    };
    const updatedMessages = [...messages, newMsg];
    setMessages(updatedMessages);
    setLoading(true);

    try {
      const resp = await api.sendQuery(content);
      const botMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'assistant',
        content: resp.answer || resp.reply || 'Query processed.',
        timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false }),
        query_type: resp.query_type,
        highlighted_nodes: resp.highlighted_nodes
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          content: 'System Error: Failed to communicate with core.',
          timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false })
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, [messages]);

  const clearHistory = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, loading, sendMessage, clearHistory };
}
