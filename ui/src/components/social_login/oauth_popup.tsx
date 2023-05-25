import { useState } from 'react';
import { OAUTH_RESPONSE } from '../../constants';
import { checkState, isWindowOpener, openerPostMessage, queryToObject } from '../../utils';


export const OAuthPopup = () => {
  const [ count, setCount ] = useState(0);

  const payload = {
    ...queryToObject(window.location.search.split('?')[1]),
    ...queryToObject(window.location.hash.split('#')[1]),
  };
  const state = payload?.state;
  const error = payload?.error;
  const opener = window?.opener;

  const stateOk = state && checkState(state);

  console.log('OAuthPopup')
  console.log(`OAuthPopup count=${count}`);

  if (!error && stateOk && count === 0) {
    console.log('OAuthPopup: posting a message stateOK');
    openerPostMessage(opener, {
      type: OAUTH_RESPONSE,
      payload,
    });
    setCount(1)
  } else {
    const errorMessage = error
      ? decodeURI(error)
      :
      !stateOk
      ? 'OAuth error: State mismatch.'
      : 'OAuth error: An error has occured.';
    console.log('OAuthPopup: posting a message Error');
    openerPostMessage(opener, {
      type: OAUTH_RESPONSE,
      error: errorMessage,
    });
  }


  return (
    <div className="m-2" data-id="popup-loading">
      Loading...
    </div>
  );
};
