import { Button } from "react-bootstrap";
import { useGoogleAuth, useGithubAuth } from "../../hooks/use_oauth";
import { is_google_auth_enabled, is_github_auth_enabled  } from "../../runtime_config";


export default function SocialLogin() {
  const { googleAuth } = useGoogleAuth();
  const { githubAuth } = useGithubAuth();

  let google_signin_btn: JSX.Element = <div />;
  let github_signin_btn: JSX.Element = <div />;

  if (is_google_auth_enabled()) {
    google_signin_btn = <Button className="m-2 btn-success" onClick={() => googleAuth()}>
      <i className="bi bi-google"></i><span className="m-2">Login with Google</span>
    </Button>
  }

  if (is_github_auth_enabled()) {
    github_signin_btn = <Button className="m-2" onClick={() => githubAuth()}>
      <i className="bi bi-github"></i><span className="m-2">Login with GitHub</span>
    </Button>
  }

  return <div className="d-flex flex-column align-items-center">
    {google_signin_btn}
    {github_signin_btn}
  </div>
}
