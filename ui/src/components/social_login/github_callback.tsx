import { useEffect } from 'react';
import { queryToObject } from '../../utils';
import { auth_server_url } from "../../utils"


export const GitHubCallback = () => {

  useEffect(() => {
      const payload = {
        ...queryToObject(window.location.search.split('?')[1]),
        ...queryToObject(window.location.hash.split('#')[1]),
      };
      const url = auth_server_url(
        window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.github.client_id,
        payload?.code,
        window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.redirect_uri,
        payload?.state,
        'github'
      );

      fetch(url, { method:'POST' })
      .then(response => response.json())
      .then(
        data => {
          console.log(data);
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
