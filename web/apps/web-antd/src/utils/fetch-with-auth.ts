import { useAccessStore } from '@vben/stores';

import { formatToken } from '#/utils/auth';

export const API_BASE = '/api/admin/';

export function fetchWithAuth(input: RequestInfo, init: RequestInit = {}) {
  const accessStore = useAccessStore();
  const token = accessStore.accessToken;
  const headers = new Headers(init.headers || {});
  headers.append('Content-Type', 'application/json');
  headers.append('Authorization', formatToken(token) as string);
  return fetch(API_BASE + input, { ...init, headers });
}
