/**
 * API 관련 React Query 훅
 */
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../lib/api-client';
import type { ProxyRequest } from '../types/api';

/**
 * API 목록 조회 훅
 */
export function useApis() {
  return useQuery({
    queryKey: ['apis'],
    queryFn: apiClient.getApis,
  });
}

/**
 * API 상세 조회 훅
 */
export function useApi(serviceName: string) {
  return useQuery({
    queryKey: ['api', serviceName],
    queryFn: () => apiClient.getApi(serviceName),
    enabled: !!serviceName,
  });
}

/**
 * 엔드포인트 목록 조회 훅
 */
export function useEndpoints(serviceName: string) {
  return useQuery({
    queryKey: ['endpoints', serviceName],
    queryFn: () => apiClient.getEndpoints(serviceName),
    enabled: !!serviceName,
  });
}

/**
 * API 테스트 훅
 */
export function useApiTest() {
  return useMutation({
    mutationFn: (request: ProxyRequest) => apiClient.testEndpoint(request),
  });
}

/**
 * 헬스체크 훅
 */
export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: apiClient.getHealth,
  });
}
