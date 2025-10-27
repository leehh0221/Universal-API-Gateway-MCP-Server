import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ApiListPage from './pages/ApiListPage';
import ApiDetailPage from './pages/ApiDetailPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <Link to="/" className="flex items-center px-2 py-2 text-gray-900 hover:text-gray-600">
                    <h1 className="text-xl font-bold">Universal API Gateway</h1>
                  </Link>
                  <div className="ml-6 flex space-x-4 items-center">
                    <Link to="/" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                      Dashboard
                    </Link>
                    <Link to="/apis" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                      APIs
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </nav>

          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/apis" element={<ApiListPage />} />
              <Route path="/apis/:serviceName" element={<ApiDetailPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
