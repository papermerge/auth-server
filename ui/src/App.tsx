import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import { OIDCCallback } from './components/oidc_login/oidc_callback';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

import Logo from "./components/login/logo";
import Login from "./components/login/login";
import OIDCLogin from "./components/oidc_login/oidc_login";
import Separator from './components/separator';

import { is_oidc_enabled } from './runtime_config';


const SimpleLoginLayout = () => {
  return (
    <main className="login-layout">
      <div>
        <Logo />
        <div className="d-flex card flex-row">
          <div className="px-2 py-3">
            <div className="card-body">
              <p className="card-title text-secondary">
                Sign in with your credentials
              </p>
              <Login />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

const OIDCLoginLayout = () => {
  return (
    <main className="login-layout">
      <div>
        <Logo />
        <div className="d-flex card flex-row">
          <div className="px-2 py-3">
            <div className="card-body h-100 d-flex align-items-center">
              <OIDCLogin />
            </div>
          </div>
          <Separator />
          <div className="px-2 py-3">
            <div className="card-body">
              <p className="card-title text-secondary">
                Sign in with your credentials
              </p>
              <Login />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}


const LoginLayout = () => {
  if (is_oidc_enabled()) {
    return <OIDCLoginLayout />;
  }

  return <SimpleLoginLayout />;
}

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<OIDCCallback />} path="/oidc/callback" />
      <Route element={<LoginLayout />} path="/" />
      <Route element={<Navigate to="/" />} path="*" />
    </Routes>
  </BrowserRouter>
);

export default App;
