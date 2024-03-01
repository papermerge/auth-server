import { useEffect } from 'react';
import { queryToObject } from '../../utils';
import { auth_server_url } from "../../utils"


export const OIDCCallback = () => {

  useEffect(() => {
      const payload = {
        ...queryToObject(window.location.search.split('?')[1]),
        ...queryToObject(window.location.hash.split('#')[1]),
      };
      const url = auth_server_url(
        window.__PAPERMERGE_RUNTIME_CONFIG__.oidc.client_id,
        payload?.code,
        window.__PAPERMERGE_RUNTIME_CONFIG__.oidc.redirect_uri,
        payload?.state,
        'google'
      );

      fetch(url, { method:'POST' })
      .then(response => response.json())
      .then(
        data => {
          console.log(data);
          console.log(`Redirecting to the origin ${window.location.origin}/app`);
          window.location.href = `${window.location.origin}/app`;
        }
      ).catch(error => {
        console.log(`There was an error ==='${error}'===`);
      });

    }, []
  );

  return (
    <div className="m-2">
      Loading...
    </div>
  );
};
