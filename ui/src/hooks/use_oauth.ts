
import { useCallback, useState, useRef } from 'react';
import { TAuthTokenPayload, TOauth2Props } from '../types';


const OAUTH_STATE_KEY = 'react-use-oauth2-state-key';
export const POPUP_HEIGHT = 700;
export const POPUP_WIDTH = 600;
export const OAUTH_RESPONSE = 'react-use-oauth2-response';
export const DEFAULT_EXCHANGE_CODE_FOR_TOKEN_METHOD = 'POST';


const generateState = () => {
	const validChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	let array: Uint8Array = new Uint8Array(40);
  let array2: Uint8Array;

  window.crypto.getRandomValues(array);

  array2 = array.map(
    (value: number, index: number, array: Uint8Array) => {
        return validChars.codePointAt(value % validChars.length) || 0;
    }
  );
	const randomState = String.fromCharCode.apply(null, Array.from(array2));

  return randomState;
};

const saveState = (state: string) => {
	sessionStorage.setItem(OAUTH_STATE_KEY, state);
};

const removeState = () => {
	sessionStorage.removeItem(OAUTH_STATE_KEY);
};

export const objectToQuery = (object: Record<string, string>) => {
	return new URLSearchParams(object).toString();
};

export const queryToObject = (query: string) => {
	const parameters = new URLSearchParams(query);
	return Object.fromEntries(parameters.entries());
};


export const formatAuthorizeUrl = (
	authorizeUrl: string,
	clientId: string,
	redirectUri: string,
	scope: string,
	state: string,
	responseType: TOauth2Props['responseType'],
	extraQueryParameters: TOauth2Props['extraQueryParameters'] = {}
) => {
	const query = objectToQuery({
		response_type: responseType,
		client_id: clientId,
		redirect_uri: redirectUri,
		scope,
		state,
		...extraQueryParameters,
	});

	return `${authorizeUrl}?${query}`;
};

export const openPopup = (url: string) => {
	// To fix issues with window.screen in multi-monitor setups, the easier option is to
	// center the pop-up over the parent window.
	const top = window.outerHeight / 2 + window.screenY - POPUP_HEIGHT / 2;
	const left = window.outerWidth / 2 + window.screenX - POPUP_WIDTH / 2;
	return window.open(
		url,
		'OAuth2 Popup',
		`height=${POPUP_HEIGHT},width=${POPUP_WIDTH},top=${top},left=${left}`
	);
};

export const closePopup = (popupRef: React.MutableRefObject<Window | null | undefined>) => {
	popupRef.current?.close();
};

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