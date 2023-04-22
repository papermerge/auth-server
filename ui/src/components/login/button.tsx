import React from "react";
import { ClickEvent } from "./types";

import Spinner from "../spinner";

type Args = {
  in_progress: boolean;
  is_enabled: boolean;
  onClick: (event: ClickEvent) => void;
}


function Button({in_progress, is_enabled, onClick, ...props}: Args) {
  return (
    <>
      <button {...props}
        type="button"
        disabled={!is_enabled}
        onClick={onClick}
        className="btn btn-lg btn-primary"
        style={{'width': '100%'}}>
            {in_progress && <Spinner />}
            <span className="sr-only">Sign In</span>
      </button>
    </>
  );
}

export default Button;