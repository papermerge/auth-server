import { Button } from "react-bootstrap";


export default function SocialLogin() {
  return <div className="d-flex flex-column align-items-center">
    <Button className="m-2 btn-success">
      <i className="bi bi-google"></i><span className="m-2">Login with Google</span>
    </Button>
    <Button className="m-2">
      <i className="bi bi-github"></i><span className="m-2">Login with GitHub</span>
    </Button>
  </div>
}