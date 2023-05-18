import { Button } from "react-bootstrap";
import { useOAuth2 } from "../../hooks/use_oauth";


export default function SocialLogin() {
  const { loading, error, getAuth} = useOAuth2({
		authorizeUrl: 'http://localhost:3001/mock-authorize',
		clientId: 'SOME_CLIENT_ID',
		redirectUri: `${document.location.origin}/callback`,
		scope: 'SOME_SCOPE',
		responseType: 'code',
		exchangeCodeForTokenServerURL: 'http://localhost:3001/mock-token',
		exchangeCodeForTokenMethod: 'POST',
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
