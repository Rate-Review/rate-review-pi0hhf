import React, { lazy, Suspense } from 'react'; //  ^18.0.0
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'; //  ^6.4.0
import PublicRoute from './PublicRoute'; // src/web/src/routes/PublicRoute.tsx
import ProtectedRoute from './ProtectedRoute'; // src/web/src/routes/ProtectedRoute.tsx
import AdminRoutes from './AdminRoutes'; // src/web/src/routes/AdminRoutes.tsx
import ClientRoutes from './ClientRoutes'; // src/web/src/routes/ClientRoutes.tsx
import LawFirmRoutes from './LawFirmRoutes'; // src/web/src/routes/LawFirmRoutes.tsx
import { ROUTES } from '../constants/routes'; // src/web/src/constants/routes.ts
import { useAuth } from '../hooks/useAuth'; // src/web/src/hooks/useAuth.ts

// LD1: Define lazy-loaded components for performance optimization
const LoginPage = lazy(() => import('../pages/auth/LoginPage')); // src/web/src/pages/auth/LoginPage.tsx
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage')); // src/web/src/pages/auth/RegisterPage.tsx
const ResetPasswordPage = lazy(() => import('../pages/auth/ResetPasswordPage')); // src/web/src/pages/auth/ResetPasswordPage.tsx
const MFASetupPage = lazy(() => import('../pages/auth/MFASetupPage')); // src/web/src/pages/auth/MFASetupPage.tsx
const MainLayout = lazy(() => import('../components/layout/MainLayout')); // src/web/src/components/layout/MainLayout.tsx
const AuthLayout = lazy(() => import('../components/layout/AuthLayout')); // src/web/src/components/layout/AuthLayout.tsx
const ErrorPage = lazy(() => import('../pages/ErrorPage')); // src/web/src/pages/ErrorPage.tsx
const NotFoundPage = lazy(() => import('../pages/NotFoundPage')); // src/web/src/pages/NotFoundPage.tsx

// LD1: Main routing component that defines the application's routing structure
const AppRoutes: React.FC = () => {
  // LD1: Use the useAuth hook to get authentication status
  const { isAuthenticated } = useAuth();

  // LD3: Return a BrowserRouter component containing all application routes
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          {/* LD4: Configure public routes with PublicRoute component */}
          <Route element={<PublicRoute />}>
            <Route path={ROUTES.LOGIN} element={<AuthLayout><LoginPage /></AuthLayout>} />
            <Route path={ROUTES.REGISTER} element={<AuthLayout><RegisterPage /></AuthLayout>} />
            <Route path={ROUTES.RESET_PASSWORD} element={<AuthLayout><ResetPasswordPage /></AuthLayout>} />
            <Route path={ROUTES.MFA_SETUP} element={<AuthLayout><MFASetupPage /></AuthLayout>} />
          </Route>

          {/* LD5: Configure protected routes with ProtectedRoute component */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              {/* LD6: Include role-based route sections using AdminRoutes, ClientRoutes, and LawFirmRoutes components */}
              <Route path="/admin/*" element={<AdminRoutes />} />
              <Route path="/client/*" element={<ClientRoutes />} />
              <Route path="/law-firm/*" element={<LawFirmRoutes />} />
            </Route>
          </Route>

          {/* LD7: Set up error handling routes for 404 (NotFoundPage) and general errors (ErrorPage) */}
          <Route path={ROUTES.ERROR} element={<MainLayout><ErrorPage /></MainLayout>} />
          <Route path={ROUTES.NOT_FOUND} element={<MainLayout><NotFoundPage /></MainLayout>} />

          {/* LD8: Add default redirects for root paths to appropriate destinations */}
          <Route path="/" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};

// IE3: Export the AppRoutes component for use in the application
export default AppRoutes;