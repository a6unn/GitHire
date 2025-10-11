import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Navigation } from './components/Navigation';
import { ToastContainer } from './components/Toast';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { ProjectDetailPage } from './pages/ProjectDetailPage';
import { ShortlistPage } from './pages/ShortlistPage';
import { ShortlistedCandidatesPage } from './pages/ShortlistedCandidatesPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotFoundPage } from './pages/NotFoundPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ToastProvider>
            <AuthProvider>
              <div className="min-h-screen bg-gray-50">
                <Navigation />
                <ToastContainer />
                <main className="transition-opacity duration-300 ease-in-out">
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                    <Route path="/reset-password" element={<ResetPasswordPage />} />
                    <Route
                      path="/dashboard"
                      element={
                        <ProtectedRoute>
                          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <DashboardPage />
                          </div>
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/projects"
                      element={
                        <ProtectedRoute>
                          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <ProjectsPage />
                          </div>
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/projects/:projectId"
                      element={
                        <ProtectedRoute>
                          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <ProjectDetailPage />
                          </div>
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/projects/:projectId/shortlist"
                      element={
                        <ProtectedRoute>
                          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <ShortlistPage />
                          </div>
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/projects/:projectId/shortlisted"
                      element={
                        <ProtectedRoute>
                          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <ShortlistedCandidatesPage />
                          </div>
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/profile"
                      element={
                        <ProtectedRoute>
                          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <ProfilePage />
                          </div>
                        </ProtectedRoute>
                      }
                    />
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                </main>
              </div>
            </AuthProvider>
          </ToastProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
