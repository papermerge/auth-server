import { Button } from "react-bootstrap";
import { useOIDC } from "../../hooks/use_oidc";
import { is_oidc_enabled } from "../../runtime_config";


export default function OIDCLogin() {
  const { oidcAuth } = useOIDC();

  let oidc_signin_btn: JSX.Element = <div />;

  if (is_oidc_enabled()) {
    oidc_signin_btn = <Button className="m-2 btn-success" onClick={() => oidcAuth()}>
      <span className="m-2">Login with OIDC</span>
    </Button>
  }

  return <div className="d-flex flex-column align-items-center">
    {oidc_signin_btn}
  </div>
}
