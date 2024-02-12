
import { useCallback, useState } from 'react';
import { RuntimeConfig } from '../types';
import {
  generateState,
  saveState,
  auth_provider_url,
} from "../utils"

import { get_runtime_config  } from "../runtime_config";

type StateType = {
  loading: boolean,
  error: string | null
}


export const useGoogleAuth = () => {
  const [{ loading, error }] = useState<StateType>({ loading: false, error: null });
  let googleAuth;
  let config: RuntimeConfig | undefined = get_runtime_config();

  googleAuth = useCallback(() => {
    const state = generateState();
    saveState(state);

    window.location.href = auth_provider_url(
      config?.oauth2?.google?.authorize_url || '',
      config?.oauth2?.google?.client_id || '',
      config?.oauth2?.google?.redirect_uri || '',
      config?.oauth2?.google?.scope || '',
      state
    );
  }, [
    config?.oauth2?.google?.authorize_url,
    config?.oauth2?.google?.client_id,
    config?.oauth2?.google?.redirect_uri,
    config?.oauth2?.google?.scope
  ]);


  return { loading, error, googleAuth};
}


export const useGithubAuth = () => {
  const [{ loading, error }] = useState<StateType>({ loading: false, error: null });
  let githubAuth;
  let config: RuntimeConfig | undefined = get_runtime_config();

  githubAuth = useCallback(() => {
    const state = generateState();
    saveState(state);

    window.location.href = auth_provider_url(
      config?.oauth2?.github?.authorize_url || '',
      config?.oauth2?.github?.client_id || '',
      config?.oauth2?.github?.redirect_uri || '',
      config?.oauth2?.github?.scope || '',
      state
    );
  }, [
    config?.oauth2?.github?.authorize_url,
    config?.oauth2?.github?.client_id,
    config?.oauth2?.github?.redirect_uri,
    config?.oauth2?.github?.scope
  ]);

  return { loading, error, githubAuth};
}
