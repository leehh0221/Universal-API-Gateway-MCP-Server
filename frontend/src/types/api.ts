/**
 * Backend API 타입 정의
 */

export interface ParameterDefinition {
  type: string;
  description: string;
  required: boolean;
  default?: any;
  min?: number;
  max?: number;
  enum?: any[];
}

export interface ResponseMapping {
  path?: string;
  format: string;
}

export interface RateLimit {
  max_calls: number;
  per_seconds: number;
}

export interface APIEndpoint {
  id: string;
  name: string;
  display_name: string;
  description: string;
  http_method: string;
  path: string;
  parameters: Record<string, ParameterDefinition>;
  response_mapping?: ResponseMapping;
  timeout_seconds: number;
  rate_limit?: RateLimit;
}

export interface APIDefinition {
  service_name: string;
  display_name: string;
  base_url: string;
  description: string;
  auth_required: boolean;
  endpoints: APIEndpoint[];
}

export interface APIListResponse {
  total: number;
  apis: APIDefinition[];
}

export interface APIDetailResponse {
  api: APIDefinition;
}

export interface ProxyRequest {
  service_name: string;
  endpoint_id: string;
  arguments: Record<string, any>;
}

export interface ProxyResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  loaded_apis: number;
}
