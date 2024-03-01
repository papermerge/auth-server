import { TOauth2Props } from './types';


export const closePopup = (popupRef: React.MutableRefObject<Window | null | undefined>) => {
  popupRef.current?.close();
};

const OAUTH_STATE_KEY = "oauth_state_key";


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

export const auth_provider_url = (
  authorizeUrl: string,
  clientId: string,
  redirectUrl: string,
  scope: string,
  state: string,
  extraQueryParameters: TOauth2Props['extraQueryParameters'] = {}
) => {
  const query = objectToQuery({
    response_type: 'code',
    client_id: clientId,
    redirect_url: redirectUrl,
    scope,
    state,
    ...extraQueryParameters,
  });

  return `${authorizeUrl}?${query}`;
};


export const cleanup = (
  intervalRef: React.MutableRefObject<string | number | NodeJS.Timeout | undefined>,
  popupRef: React.MutableRefObject<Window | null | undefined>,
  handleMessageListener: any
) => {
  clearInterval(intervalRef.current);
  if (popupRef.current && typeof popupRef.current.close === 'function') {
    // closePopup(popupRef);
  };
  removeState();
  window.removeEventListener('message', handleMessageListener);
};

export const auth_server_url = (
  clientId: string,
  code: string,
  redirectUrl: string,
  state: string
) => {

  const url = '/api/token';
  const anySearchParameters = queryToObject('');

  console.log(`client_id=${clientId}`);
  console.log(`code=${code}`);
  console.log(`redirect_url=${redirectUrl}`);

  return `${url}?${objectToQuery({
    ...anySearchParameters,
    client_id: clientId,
    provider: 'oidc',
    grant_type: 'authorization_code',
    code,
    redirect_url: redirectUrl,
    state,
  })}`;

};
