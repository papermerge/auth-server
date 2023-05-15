import React from "react";
import Spinner from 'react-bootstrap/Spinner';
import { ClickEvent } from "./types";


type Args = {
  in_progress: boolean;
  is_enabled: boolean;
  onClick: (event: ClickEvent) => void;
}


function Button({in_progress, is_enabled, onClick, ...props}: Args) {
  let button_text;

  if (in_progress) {
    button_text = <Spinner as="span" variant="light" size="sm" />;
  } else {
    button_text = <span className="sr-only">Sign In</span>;
  }
  return (
    <>
      <button {...props}
        type="submit"
        disabled={!is_enabled}
        onClick={onClick}
        className="btn btn-lg btn-primary"
        style={{'width': '100%'}}>
          {button_text}
      </button>
    </>
  );
}

export default Button;