
import { useCallback, useState, useRef } from 'react';
import { TAuthTokenPayload, TOauth2Props, TMessageData } from '../types';
import { OAUTH_RESPONSE, DEFAULT_EXCHANGE_CODE_FOR_TOKEN_METHOD } from '../constants';
import {
  cleanup,
  auth_server_url,
  generateState,
  saveState,
  auth_provider_url,
  openPopup
} from "../utils"

type StateType = {
  loading: boolean,
  error: string | null
}


export const useOAuth2 = <T = TAuthTokenPayload>(props: TOauth2Props<T>) => {
  const {
      authorizeUrl,
      clientId,
      redirectUri,
      scope = ''
    } = props;

  const [{ loading, error }, setUI] = useState<StateType>({ loading: false, error: null });

  const getAuth = useCallback(() => {
      const state = generateState();
      saveState(state);

      window.location.href = auth_provider_url(
        authorizeUrl,
        clientId,
        redirectUri,
        scope,
        state
      );

  }, []);

  return { loading, error, getAuth};
}