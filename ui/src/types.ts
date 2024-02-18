
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


export type ProviderType = 'google' | 'github';
export type LoginProvider = 'db' | 'ldap'

export type TOauth2Props<T = TAuthTokenPayload> = {
  provider: ProviderType;
  authorizeUrl: string;
  clientId: string;
  redirectUri: string;
  scope?: string;
  extraQueryParameters?: Record<string, any>;
  onError?: (error: string) => void;
} & TResponseTypeBasedProps<T>;


export type RuntimeConfig = {
  oauth2: {
    google: OAuth2ProviderType,
    github: OAuth2ProviderType
  }
  /*
  There are two types of buttons to sign in:
  1. social - or OIDC/OAuth2
  2. default login button
  When signing in via Social/OIDC/OAuth2 provider attributes is set the OIDC provider
  When signing in via default login button - backend can authenticate via
  DB or via LDAP. `login_provider` attribute is there to distinguish between
  DB or LDAP authentication.
  */
  login_provider: LoginProvider
}

declare global {

  type OAuth2ProviderType = {
    redirect_uri: string,
    authorize_url: string,
    client_id: string,
    scope: string
  }

  interface Window {
    __PAPERMERGE_RUNTIME_CONFIG__: RuntimeConfig;
  }
}
