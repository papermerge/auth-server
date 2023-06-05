import type { RuntimeConfig } from "./types";


export function get_runtime_config(): RuntimeConfig | undefined {
  if (!window.hasOwnProperty('__PAPERMERGE_RUNTIME_CONFIG__')) {
    return undefined;
  }

  return window.__PAPERMERGE_RUNTIME_CONFIG__;
}


export function is_oauth2_enabled(): boolean {
  let config: RuntimeConfig | undefined = get_runtime_config();

  if (!config) {
    return false;
  }

  if (config.hasOwnProperty('oauth2')) {
    return true;
  }

  return false;
}


export function is_google_auth_enabled(): boolean {

  let config: RuntimeConfig | undefined = get_runtime_config();

  if (!is_oauth2_enabled()) {
    return false;
  }

  if (config && config.oauth2.hasOwnProperty('google')) {
    return true;
  }

  return false;
}


export function is_github_auth_enabled(): boolean {

  let config: RuntimeConfig | undefined = get_runtime_config();

  if (!is_oauth2_enabled()) {
    return false;
  }

  if (config && config.oauth2.hasOwnProperty('github')) {
    return true;
  }

  return false;
}