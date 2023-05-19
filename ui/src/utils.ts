import { OAUTH_STATE_KEY, POPUP_HEIGHT, POPUP_WIDTH } from "./constants";
import { TAuthTokenPayload, TOauth2Props, TMessageData } from './types';


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


export const generateState = () => {
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

export const saveState = (state: string) => {
	sessionStorage.setItem(OAUTH_STATE_KEY, state);
};

export const removeState = () => {
	sessionStorage.removeItem(OAUTH_STATE_KEY);
};

export const objectToQuery = (object: Record<string, string>) => {
	return new URLSearchParams(object).toString();
};

export const queryToObject = (query: string) => {
	const parameters = new URLSearchParams(query);
	return Object.fromEntries(parameters.entries());
};

export const checkState = (receivedState: string) => {
	const state = sessionStorage.getItem(OAUTH_STATE_KEY);
	return state === receivedState;
};


export const isWindowOpener = (opener: Window | null): opener is Window =>
	opener !== null && opener !== undefined;

export const openerPostMessage = (opener: Window, message: TMessageData) =>
	opener.postMessage(message);

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