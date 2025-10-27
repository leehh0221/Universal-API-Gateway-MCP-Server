/**
 * API 상세 페이지
 * API 엔드포인트 목록 및 테스트 기능 제공
 */
import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApi, useApiTest } from '../hooks/useApis';
import type { APIEndpoint, ProxyRequest } from '../types/api';

export default function ApiDetailPage() {
  const { serviceName } = useParams<{ serviceName: string }>();
  const { data, isLoading, error } = useApi(serviceName || '');
  const testMutation = useApiTest();

  const [selectedEndpoint, setSelectedEndpoint] = useState<APIEndpoint | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [testResult, setTestResult] = useState<any>(null);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading API details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold">Error loading API</h3>
        <p className="text-red-600 mt-2">{String(error)}</p>
      </div>
    );
  }

  const api = data?.api;

  if (!api) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">API not found</p>
      </div>
    );
  }

  const handleEndpointSelect = (endpoint: APIEndpoint) => {
    setSelectedEndpoint(endpoint);
    setTestResult(null);

    // Initialize form data with default values
    const initialData: Record<string, any> = {};
    Object.entries(endpoint.parameters).forEach(([key, param]) => {
      if (param.default !== undefined) {
        initialData[key] = param.default;
      } else if (param.type === 'boolean') {
        initialData[key] = false;
      } else {
        initialData[key] = '';
      }
    });
    setFormData(initialData);
  };

  const handleInputChange = (paramName: string, value: any, type: string) => {
    let processedValue = value;

    if (type === 'number') {
      processedValue = value === '' ? '' : parseFloat(value);
    } else if (type === 'integer') {
      processedValue = value === '' ? '' : parseInt(value, 10);
    } else if (type === 'boolean') {
      processedValue = value === 'true' || value === true;
    }

    setFormData(prev => ({ ...prev, [paramName]: processedValue }));
  };

  const handleTest = async () => {
    if (!selectedEndpoint || !serviceName) return;

    // Filter out empty values and only include required or filled parameters
    const args: Record<string, any> = {};
    Object.entries(formData).forEach(([key, value]) => {
      const param = selectedEndpoint.parameters[key];
      if (value !== '' && value !== null && value !== undefined) {
        args[key] = value;
      } else if (param?.required) {
        args[key] = value;
      }
    });

    const request: ProxyRequest = {
      service_name: serviceName,
      endpoint_id: selectedEndpoint.id,
      arguments: args,
    };

    try {
      const result = await testMutation.mutateAsync(request);
      setTestResult(result);
    } catch (err) {
      setTestResult({ success: false, error: String(err) });
    }
  };

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2 text-sm">
          <li>
            <Link to="/apis" className="text-blue-600 hover:text-blue-800">
              APIs
            </Link>
          </li>
          <li className="text-gray-400">/</li>
          <li className="text-gray-700">{api.display_name}</li>
        </ol>
      </nav>

      {/* API Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900">{api.display_name}</h2>
        <p className="mt-2 text-gray-600">{api.description}</p>
        <div className="mt-4 flex items-center space-x-6 text-sm">
          <div className="flex items-center text-gray-500">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
            {api.base_url}
          </div>
          {api.auth_required && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Auth Required
            </span>
          )}
        </div>
      </div>

      {/* Endpoints Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Endpoint List */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Endpoints</h3>
          <div className="space-y-2">
            {api.endpoints.map((endpoint) => (
              <button
                key={endpoint.id}
                onClick={() => handleEndpointSelect(endpoint)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-colors ${
                  selectedEndpoint?.id === endpoint.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-mono font-semibold ${
                        endpoint.http_method === 'GET' ? 'bg-green-100 text-green-800' :
                        endpoint.http_method === 'POST' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {endpoint.http_method}
                      </span>
                      <span className="font-semibold text-gray-900">{endpoint.display_name}</span>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">{endpoint.description}</p>
                    <p className="mt-1 text-xs font-mono text-gray-500">{endpoint.path}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Test Panel */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Endpoint</h3>

          {!selectedEndpoint ? (
            <div className="text-center py-12 text-gray-500">
              Select an endpoint to test
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Parameters</h4>
                {Object.keys(selectedEndpoint.parameters).length === 0 ? (
                  <p className="text-sm text-gray-500">No parameters required</p>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(selectedEndpoint.parameters).map(([paramName, param]) => (
                      <div key={paramName}>
                        <label className="block text-sm font-medium text-gray-700">
                          {paramName}
                          {param.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        <p className="text-xs text-gray-500 mt-0.5">{param.description}</p>

                        {param.enum ? (
                          <select
                            value={formData[paramName] || ''}
                            onChange={(e) => handleInputChange(paramName, e.target.value, param.type)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          >
                            <option value="">Select...</option>
                            {param.enum.map((val) => (
                              <option key={String(val)} value={String(val)}>
                                {String(val)}
                              </option>
                            ))}
                          </select>
                        ) : param.type === 'boolean' ? (
                          <select
                            value={String(formData[paramName])}
                            onChange={(e) => handleInputChange(paramName, e.target.value, param.type)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          >
                            <option value="false">false</option>
                            <option value="true">true</option>
                          </select>
                        ) : (
                          <input
                            type={param.type === 'number' || param.type === 'integer' ? 'number' : 'text'}
                            value={formData[paramName] || ''}
                            onChange={(e) => handleInputChange(paramName, e.target.value, param.type)}
                            placeholder={param.default !== undefined ? `Default: ${param.default}` : ''}
                            min={param.min}
                            max={param.max}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={handleTest}
                disabled={testMutation.isPending}
                className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
              >
                {testMutation.isPending ? 'Testing...' : 'Test API'}
              </button>

              {testResult && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-900 mb-2">Response</h4>
                  <div className={`p-4 rounded-lg ${
                    testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}>
                    {testResult.success ? (
                      <div>
                        <div className="flex items-center mb-2">
                          <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span className="text-green-800 font-semibold">Success</span>
                        </div>
                        <pre className="mt-2 text-xs bg-white p-3 rounded overflow-auto max-h-96">
                          {JSON.stringify(testResult.data, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-center mb-2">
                          <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          <span className="text-red-800 font-semibold">Error</span>
                        </div>
                        <p className="text-sm text-red-700">{testResult.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
