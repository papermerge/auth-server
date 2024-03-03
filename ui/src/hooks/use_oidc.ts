
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


export const useOIDC = () => {
  const [{ loading, error }] = useState<StateType>({ loading: false, error: null });
  let oidcAuth;
  let config: RuntimeConfig | undefined = get_runtime_config();

  oidcAuth = useCallback(() => {
    const state = generateState();
    saveState(state);

    window.location.href = auth_provider_url(
      config?.oidc?.authorize_url || '',
      config?.oidc?.client_id || '',
      config?.oidc?.redirect_url || '',
      config?.oidc?.scope || '',
      state
    );
  }, [
    config?.oidc?.authorize_url,
    config?.oidc?.client_id,
    config?.oidc?.redirect_url,
    config?.oidc?.scope
  ]);


  return { loading, error, oidcAuth};
}
