/**
 * API 클라이언트
 */
import axios from 'axios';
import type {
  APIListResponse,
  APIDetailResponse,
  APIEndpoint,
  ProxyRequest,
  ProxyResponse,
  HealthResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  /**
   * 헬스체크
   */
  async getHealth(): Promise<HealthResponse> {
    const { data } = await client.get<HealthResponse>('/health');
    return data;
  },

  /**
   * 등록된 모든 API 목록 조회
   */
  async getApis(): Promise<APIListResponse> {
    const { data} = await client.get<APIListResponse>('/apis');
    return data;
  },

  /**
   * 특정 API 상세 정보 조회
   */
  async getApi(serviceName: string): Promise<APIDetailResponse> {
    const { data } = await client.get<APIDetailResponse>(`/apis/${serviceName}`);
    return data;
  },

  /**
   * 특정 API의 엔드포인트 목록 조회
   */
  async getEndpoints(serviceName: string): Promise<APIEndpoint[]> {
    const { data } = await client.get<APIEndpoint[]>(`/apis/${serviceName}/endpoints`);
    return data;
  },

  /**
   * API 엔드포인트 테스트 호출
   */
  async testEndpoint(request: ProxyRequest): Promise<ProxyResponse> {
    const { data } = await client.post<ProxyResponse>('/proxy/test', request);
    return data;
  },
};
