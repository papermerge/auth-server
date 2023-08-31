import { useState } from 'react';

import Button from "./button";
import Input from "./input";
import Error from './error';
import { ClickEvent } from './types';


const authenticate = async (username: string, password: string) => {
  const params = new URLSearchParams();

  params.append('username', username);
  params.append('password', password);
  params.append('grant_type', 'password');

  let response = await fetch(
    '/api/token',
    {
      method: "POST",
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params
    }
  );

  if (response.status === 200) {
    for(let [key, value] of response.headers.entries()) {
      console.log(key, value);
    }
    // read redirect from URL params or from header
    // and redirect to new URL
    // e.g.
    window.location.href = "/app";
    return true;
  }

  return false;
}


function credentials_provided(username: string, password: string): boolean {
  /**
   * Returens true only if both username and password are provided
   * as non empty strings
   */
  if (!username) {
    return false;
  }
  if (!password) {
    return false;
  }

  let clean_username = username.trim();
  let clean_password = password.trim();

  if (clean_username === '') {
    return false;
  }

  if (clean_password === '') {
    return false;
  }

  return true;
}


export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState(
    (new URLSearchParams(document.location.search)).get('msg') || ''
  );
  const [inProgress, setInProgress] = useState(false);
  const [isEnabled, setIsEnabled] = useState(false);

  const handleSubmit = (event: ClickEvent) => {
    event.preventDefault()
    setErrorMessage('');
    setInProgress(true);

    let body = JSON.stringify({username, password});

    fetch(
      '/api/token',
      {
        method:'POST',
        body: body,
        headers: {
          "Content-Type": "application/json",
        }
      },
    )
    .then(response => {
        if (response.status != 200) {
          setErrorMessage(response.statusText);
          response.json().then(result => console.log(result));
          setInProgress(false);
        } else {
          window.location.href = `${window.location.origin}/app`;
        }
      }
    ).catch(error => {
      console.log(`There was an error ==='${error}'===`);
    });
  }

  const handleChangeUsername = (value: string) => {
    setUsername(value);

    setErrorMessage('');

    // disable sign in button if credentials are not provided
    setIsEnabled(
      credentials_provided(value, password)
    );
  }

  const handleChangePassword = (value: string) => {
    setPassword(value);

    setErrorMessage('');

    // disable sign in button if credentials are not provided
    setIsEnabled(
      credentials_provided(username, value)
    );
  }

  return (
    <form>
      <div className="mb-3 form-floating">
        <Input
          onchange={handleChangeUsername}
          name="username"
          type="text"
          placeholder="Username or email" />
        <label className="form-label">
          Username
        </label>
      </div>

      <div className="mb-3 form-floating">
        <Input
          onchange={handleChangePassword}
          name="password"
          type="password"
          placeholder="" />
        <label className="form-label">
          Password
        </label>
      </div>

      <Button
        onClick={handleSubmit}
        in_progress={inProgress}
        is_enabled={isEnabled} />

      <Error message={errorMessage} />
    </form>
  );
}