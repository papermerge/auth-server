import { OAUTH_RESPONSE } from "./constants";

export type TAuthTokenPayload = {
  token_type: string;
  expires_in: number;
  access_token: string;
  scope: string;
  refresh_token: string;
};

export type TResponseTypeBasedProps<T> =
  | {
      responseType: 'code';
      onSuccess?: (payload: T) => void;
      // TODO Adjust payload type
    }
  | {
      responseType: 'token';
      onSuccess?: (payload: T) => void;
    };


export type TOauth2Props<T = TAuthTokenPayload> = {
  provider: 'google' | 'github';
  authorizeUrl: string;
  clientId: string;
  redirectUri: string;
  scope?: string;
  extraQueryParameters?: Record<string, any>;
  onError?: (error: string) => void;
} & TResponseTypeBasedProps<T>;

export type TMessageData =
  | {
      type: typeof OAUTH_RESPONSE;
      error: string;
    }
  | {
      type: typeof OAUTH_RESPONSE;
      payload: any;
    };


declare global {

  type OAuth2ProviderType = {
    redirect_uri: string,
    callback: string,
    authorize_url: string,
    client_id: string,
    exchange_code_for_token_url: string,
    scope: string
  }

  interface Window {
    __PAPERMERGE_RUNTIME_CONFIG__: {
      oauth2: {
        google: OAuth2ProviderType,
        github: OAuth2ProviderType
      }
    }
  }
}
