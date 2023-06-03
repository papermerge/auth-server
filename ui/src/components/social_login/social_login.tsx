import { Button } from "react-bootstrap";
import { useOAuth2 } from "../../hooks/use_oauth";


export default function SocialLogin() {
  const { loading, error, getAuth} = useOAuth2({
    provider: 'google',
    authorizeUrl: window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.google.authorize_url,
    clientId: window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.google.client_id,
    scope: window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.google.scope,
    redirectUri: window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.redirect_uri,
    responseType: 'code',
    onSuccess: () => console.log('Success'),
    onError: () => console.log('Error'),
  });

  return <div className="d-flex flex-column align-items-center">
    <Button className="m-2 btn-success" onClick={() => getAuth()}>
      <i className="bi bi-google"></i><span className="m-2">Login with Google</span>
    </Button>
    <Button className="m-2">
      <i className="bi bi-github"></i><span className="m-2">Login with GitHub</span>
    </Button>
  </div>
}
