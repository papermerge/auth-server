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
			exchangeCodeForTokenServerURL: string;
			exchangeCodeForTokenMethod?: 'POST' | 'GET';
			onSuccess?: (payload: T) => void;
			// TODO Adjust payload type
	  }
	| {
			responseType: 'token';
			onSuccess?: (payload: T) => void;
	  };


export type TOauth2Props<T = TAuthTokenPayload> = {
	authorizeUrl: string;
	clientId: string;
	redirectUri: string;
	scope?: string;
	extraQueryParameters?: Record<string, any>;
	onError?: (error: string) => void;
} & TResponseTypeBasedProps<T>;
