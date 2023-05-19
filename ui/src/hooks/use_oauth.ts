
import { useCallback, useState, useRef } from 'react';
import { TAuthTokenPayload, TOauth2Props } from '../types';
import { OAUTH_RESPONSE } from '../constants';
import { generateState, saveState, formatAuthorizeUrl, openPopup} from "../utils"


export const useOAuth2 = <T = TAuthTokenPayload>(props: TOauth2Props<T>) => {
  const {
      authorizeUrl,
      clientId,
      redirectUri,
      responseType,
      scope = '',
    } = props;
  const popupRef = useRef<Window | null>();
  const [{ loading, error }, setUI] = useState({ loading: false, error: null });

  const getAuth = useCallback(() => {
      // 1. Init
      setUI({
        loading: true,
        error: null,
      });

      // 2. Generate and save state
      const state = generateState();
      saveState(state);

      // 3. Open popup
      popupRef.current = openPopup(
        formatAuthorizeUrl(authorizeUrl, clientId, redirectUri, scope, state, responseType)
      );

  }, []);

  return { loading, error, getAuth};
}