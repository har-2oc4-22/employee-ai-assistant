/**
 * hooks/useChat.js
 * -----------------
 * Custom React hook that manages all chat state and logic.
 *
 * WHY A CUSTOM HOOK?
 *   It keeps App.jsx clean (UI only).
 *   All API calls, loading state, error state, and history live here.
 *   Easy to unit test independently of the UI.
 *
 * STATE:
 *   messages       — array of {role, content, sources, tools_used, id}
 *   isLoading      — true while waiting for backend response
 *   error          — error message string or null
 *   conversationId — current conversation ID (null = new conversation)
 *   employeeId     — the currently selected employee
 */

import { useState, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendChatMessage, resetConversation } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [employeeId, setEmployeeId] = useState('EMP001');

  // Ref to scroll chat to bottom after new message
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Send a message to the assistant.
   * Adds the user's message immediately (optimistic UI),
   * then waits for the backend response.
   */
  const sendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || isLoading) return;
    setError(null);

    // Add user message to chat immediately
    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: messageText,
      sources: [],
      tools_used: [],
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(employeeId, messageText, conversationId);

      // Save conversation ID from response
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant message
      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        tools_used: response.tools_used || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Scroll to bottom after a brief delay for DOM update
      setTimeout(scrollToBottom, 100);

    } catch (err) {
      const errorMsg = err.response?.data?.detail
        || err.message
        || 'An error occurred. Please try again.';
      setError(errorMsg);

      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: uuidv4(),
          role: 'error',
          content: errorMsg,
          sources: [],
          tools_used: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [employeeId, conversationId, isLoading]);

  /**
   * Reset the conversation: clear local messages and backend history.
   */
  const resetChat = useCallback(async () => {
    if (conversationId) {
      try {
        await resetConversation(conversationId);
      } catch (e) {
        // Silently ignore — local reset still happens
        console.warn('Could not reset conversation on backend:', e.message);
      }
    }
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, [conversationId]);

  /**
   * Change the active employee — also resets the conversation.
   */
  const changeEmployee = useCallback(async (newEmployeeId) => {
    setEmployeeId(newEmployeeId);
    await resetChat();
  }, [resetChat]);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    employeeId,
    messagesEndRef,
    sendMessage,
    resetChat,
    changeEmployee,
  };
}
