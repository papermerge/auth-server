import { useEffect, useState } from 'react';

import { Button, PasswordInput, Text, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';
import { redirect } from "react-router-dom";

import { get_runtime_config } from '@/RuntimeConfig';
import { RuntimeConfig } from '@/types';

function get_token_endpoint(): string {
  const base_url = import.meta.env.VITE_TOKEN_BASE_URL

  return `${base_url}/api/token`
}

function get_redirect_endpoint(): string {
  const base_url = import.meta.env.VITE_REDIRECT_BASE_URL

  return `${base_url}/app`
}


export default function Login() {
  const [error, setError] = useState<string>()
  const form = useForm({
    mode: 'uncontrolled',
    initialValues: { username: '', password: '' },
  });
  const [submittedValues, setSubmittedValues] = useState<typeof form.values | null>(null);

  useEffect(() => {
    if (submittedValues?.password && submittedValues.username) {
       // only if both username and password are provided and not empty
      let config: RuntimeConfig | undefined = get_runtime_config();
      let provider = 'db';
      const username = submittedValues?.username
      const password = submittedValues?.password

      if (config) {
        provider = config.login_provider;
      }

      let body = JSON.stringify({username, password, provider});
      fetch(
        get_token_endpoint(),
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
            setError(response.statusText);
            response.json().then(result => console.log(result));
          } else {
            redirect(get_redirect_endpoint())
          }
        }
      ).catch(error => {
        console.log(`There was an error ==='${error}'===`);
      });
    }
  }, [submittedValues?.username, submittedValues?.password])

  return (
    <form onSubmit={form.onSubmit(setSubmittedValues)}>
        <TextInput
          {...form.getInputProps('username')}
          key={form.key('username')}
          label="Username"
          placeholder="username"
          required />
        <PasswordInput
          {...form.getInputProps('password')}
          key={form.key('password')}
          label="Password"
          placeholder="Your password"
          required mt="md" />
        <Button fullWidth mt="xl" type="submit">
          Sign in
        </Button>
        <Text my={"md"} c="red">
          {error}
        </Text>
    </form>
  );
}