import { useEffect } from 'react';
import { queryToObject } from '../../utils';
import { auth_server_url } from "../../utils"


export const Callback = () => {

  useEffect(() => {
      const payload = {
        ...queryToObject(window.location.search.split('?')[1]),
        ...queryToObject(window.location.hash.split('#')[1]),
      };
      const url = auth_server_url(
        window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.google.client_id,
        payload?.code,
        window.__PAPERMERGE_RUNTIME_CONFIG__.oauth2.google.redirect_uri,
        payload?.state
      )
      console.log(`POSTING NOW to ${url}`);
      console.log(`CODE=${payload?.code}`);

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
