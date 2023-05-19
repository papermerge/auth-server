import { useEffect } from 'react';
import { OAUTH_RESPONSE } from '../../constants';
import { checkState, isWindowOpener, openerPostMessage, queryToObject } from '../../utils';


export const OAuthPopup = () => {
  useEffect(() => {
    const payload = {
      ...queryToObject(window.location.search.split('?')[1]),
      ...queryToObject(window.location.hash.split('#')[1]),
    };
    const state = payload?.state;
    const error = payload?.error;
    const opener = window?.opener;

    if (isWindowOpener(opener)) {
      const stateOk = state && checkState(state);

      if (!error && stateOk) {
        openerPostMessage(opener, {
          type: OAUTH_RESPONSE,
          payload,
        });
      } else {
        const errorMessage = error
          ? decodeURI(error)
          :
          !stateOk
          ? 'OAuth error: State mismatch.'
          : 'OAuth error: An error has occured.';
        openerPostMessage(opener, {
          type: OAUTH_RESPONSE,
          error: errorMessage,
        });
      }
    } else {
      throw new Error('No window opener');
    }
  }, []);

  return (
    <div className="m-2" data-id="popup-loading">
      Loading...
    </div>
  );
};
