
import { useCallback, useState, useRef } from 'react';
import { TAuthTokenPayload, TOauth2Props, TMessageData } from '../types';
import { OAUTH_RESPONSE, DEFAULT_EXCHANGE_CODE_FOR_TOKEN_METHOD } from '../constants';
import {
  cleanup,
  formatExchangeCodeForTokenServerURL,
  generateState,
  saveState,
  formatAuthorizeUrl,
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
      responseType,
      scope = '',
      onError,
      onSuccess,
    } = props;
  const popupRef = useRef<Window | null>();
  const intervalRef = useRef<string | number | NodeJS.Timeout | undefined>();
  const [{ loading, error }, setUI] = useState<StateType>({ loading: false, error: null });

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


		// 4. Register message listener
		async function handleMessageListener(message: MessageEvent<TMessageData>) {
			const type = message?.data?.type;

			if (type !== OAUTH_RESPONSE) {
				return;
			}

			try {

				if ('error' in message.data) {
					const errorMessage = message.data?.error || 'Unknown Error occured.';

          setUI({loading: false, error: errorMessage});

					if (onError) {
            await onError(errorMessage);
          }

				} else {
					let payload = message?.data?.payload;

          if (responseType === 'code') {
            const response = await fetch(
							formatExchangeCodeForTokenServerURL(
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
					setUI({loading: false, error: null});
					//setData(payload);

					if (onSuccess) {
						await onSuccess(payload);
					}
				}
			} catch (genericError: any) {
				console.error(genericError);
				setUI({loading: false, error: genericError.toString()});
			} finally {
				// Clear stuff ...
				cleanup(intervalRef, popupRef, handleMessageListener);
			}
		}
		window.addEventListener('message', handleMessageListener);

		// 4. Begin interval to check if popup was closed forcefully by the user
		intervalRef.current = setInterval(() => {
			const popupClosed = !popupRef.current?.window || popupRef.current?.window?.closed;
			if (popupClosed) {
				// Popup was closed before completing auth...
				setUI((ui) => ({
					...ui,
					loading: false,
				}));
				console.warn('Warning: Popup was closed before completing authentication.');
				cleanup(intervalRef, popupRef, handleMessageListener);
			}
		}, 250);

		// 5. Remove listener(s) on unmount
		return () => {
			window.removeEventListener('message', handleMessageListener);
			if (intervalRef.current) clearInterval(intervalRef.current);
		};

  }, []);

  return { loading, error, getAuth};
}