
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
      scope = '',
    } = props;
  const popupRef = useRef<Window | null>();
  const intervalRef = useRef<string | number | NodeJS.Timeout | undefined>();
  const [{ loading, error }, setUI] = useState<StateType>({ loading: false, error: null });

  const getAuth = useCallback(() => {
      const state = generateState();
      saveState(state);

      console.log("open popup");
      // 3. Open popup
      popupRef.current = openPopup(
        auth_provider_url(authorizeUrl, clientId, redirectUri, scope, state)
      );

      // 4. Register message listener
      async function handleMessageListener(message: MessageEvent<TMessageData>) {
        try {
          if (!('error' in message.data)) {
            let payload = message?.data?.payload;
            console.log(`PAYLOAD code received: ${payload?.code}`);

            const response = await fetch(
              auth_server_url(
                clientId,
                payload?.code,
                redirectUri,
                state
              ),
              {
                method:'POST',
              }
            );
            payload = await response.json();
          }
        } catch (genericError: any) {
          console.error(genericError);
        } finally {
          cleanup(intervalRef, popupRef, handleMessageListener);
        }
      }

      console.log("Adding handleMessageListenser");
      window.addEventListener('message', handleMessageListener);

      return () => {
        window.removeEventListener('message', handleMessageListener);
      };

  }, []);

  return { loading, error, getAuth};
}