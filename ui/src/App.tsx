import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

import Logo from "./components/login/logo";
import Login from "./components/login/login";
import SocialLogin from "./components/social_login/social_login";
import Separator from './components/separator';


export default function LoginLayout() {
  return (
    <main className="login-layout">
      <div>
        <Logo />
        <div className="d-flex card flex-row">
          <div className="px-2 py-3">
            <div className="card-body h-100 d-flex align-items-center">
              <SocialLogin />
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
