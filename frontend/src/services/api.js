/**
 * services/api.js
 * ----------------
 * Central Axios client for all backend API calls.
 * 
 * WHY CENTRALIZE?
 *   If the backend URL changes, we only update VITE_API_BASE_URL.
 *   All components import from this file — no duplicated URLs.
 */

import axios from 'axios';

// The Vite dev proxy routes /api/* → http://localhost:8000/*
// In production, set VITE_API_BASE_URL to the real backend URL.
let rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
if (rawBaseUrl && !rawBaseUrl.startsWith('http://') && !rawBaseUrl.startsWith('https://')) {
  rawBaseUrl = `https://${rawBaseUrl}`;
}
const API_BASE_URL = rawBaseUrl;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds — LLM calls can be slow
});

// ── API functions ──────────────────────────────────────────────────────────

/**
 * Send a chat message to the assistant.
 * @param {string} employeeId - e.g. "EMP001"
 * @param {string} message - the user's question
 * @param {string|null} conversationId - null for new conversation
 * @returns {Promise<{conversation_id, answer, sources, tools_used}>}
 */
export async function sendChatMessage(employeeId, message, conversationId = null) {
  const response = await apiClient.post('/chat', {
    employee_id: employeeId,
    message,
    conversation_id: conversationId,
  });
  return response.data;
}

/**
 * Reset (clear) a conversation history on the backend.
 * @param {string} conversationId
 */
export async function resetConversation(conversationId) {
  const response = await apiClient.delete(`/conversations/${conversationId}`);
  return response.data;
}

/**
 * Fetch employee details (for verifying employee ID on load).
 * @param {string} employeeId
 */
export async function getEmployee(employeeId) {
  const response = await apiClient.get(`/employees/${employeeId}`);
  return response.data;
}

/**
 * Health check.
 */
export async function checkHealth() {
  const response = await apiClient.get('/health');
  return response.data;
}

export default apiClient;
