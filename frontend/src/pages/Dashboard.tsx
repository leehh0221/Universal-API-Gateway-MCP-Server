/**
 * Dashboard 페이지
 * 시스템 상태 및 API 개요 표시
 */
import { useHealth, useApis } from '../hooks/useApis';

export default function Dashboard() {
  const { data: health, isLoading: healthLoading, error: healthError } = useHealth();
  const { data: apis, isLoading: apisLoading, error: apisError } = useApis();

  if (healthLoading || apisLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (healthError || apisError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold">Error loading data</h3>
        <p className="text-red-600 mt-2">
          {healthError ? String(healthError) : String(apisError)}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="mt-1 text-sm text-gray-600">
          Universal API Gateway 시스템 현황
        </p>
      </div>

      {/* System Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Status</div>
            <div className="mt-1 flex items-center">
              <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`}></span>
              <span className="text-lg font-semibold text-gray-900">
                {health?.status || 'Unknown'}
              </span>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Version</div>
            <div className="mt-1 text-lg font-semibold text-gray-900">
              {health?.version || 'N/A'}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Loaded APIs</div>
            <div className="mt-1 text-lg font-semibold text-gray-900">
              {health?.loaded_apis || 0}
            </div>
          </div>
        </div>
      </div>

      {/* API Overview */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Available APIs</h3>
        <div className="space-y-3">
          {apis?.apis.map((api) => (
            <div key={api.service_name} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold text-gray-900">{api.display_name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{api.description}</p>
                  <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                    <span>{api.endpoints.length} endpoints</span>
                    <span>•</span>
                    <span>{api.base_url}</span>
                  </div>
                </div>
                <a
                  href={`/apis/${api.service_name}`}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  View Details →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
