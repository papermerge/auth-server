import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { LoginPage } from './pages/Login.page';

const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
]);

export function Router() {
  return <RouterProvider router={router} />;
}
