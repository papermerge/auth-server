import 'bootstrap/dist/css/bootstrap.min.css';

import Logo from "./components/login/logo";
import Login from "./components/login/login";


export default function LoginLayout() {
  return (
    <main className="login-layout">
      <div>
        <Logo />

        <div className="card px-2 py-3">
          <div className="card-body">
            <p className="card-title text-secondary">
              Please sign in to start your session
            </p>
            <Login />
          </div>
        </div>
      </div>
    </main>
  );
}
