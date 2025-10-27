/**
 * API 목록 페이지
 */
import { useApis } from '../hooks/useApis';
import { Link } from 'react-router-dom';

export default function ApiListPage() {
  const { data, isLoading, error } = useApis();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading APIs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold">Error loading APIs</h3>
        <p className="text-red-600 mt-2">{String(error)}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Available APIs</h2>
        <p className="mt-1 text-sm text-gray-600">
          Total {data?.total || 0} APIs available
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {data?.apis.map((api) => (
          <div
            key={api.service_name}
            className="bg-white shadow rounded-lg hover:shadow-lg transition-shadow"
          >
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {api.display_name}
                    </h3>
                    {api.auth_required && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        Auth Required
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-gray-600">{api.description}</p>

                  <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      {api.endpoints.length} endpoints
                    </div>
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                      </svg>
                      {api.base_url}
                    </div>
                  </div>

                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Endpoints:</h4>
                    <div className="space-y-1">
                      {api.endpoints.map((endpoint) => (
                        <div
                          key={endpoint.id}
                          className="flex items-center space-x-2 text-sm"
                        >
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-mono font-semibold ${
                            endpoint.http_method === 'GET' ? 'bg-green-100 text-green-800' :
                            endpoint.http_method === 'POST' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {endpoint.http_method}
                          </span>
                          <span className="text-gray-700">{endpoint.display_name}</span>
                          <span className="text-gray-400">-</span>
                          <span className="text-gray-500">{endpoint.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <Link
                  to={`/apis/${api.service_name}`}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  View Details & Test
                  <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
