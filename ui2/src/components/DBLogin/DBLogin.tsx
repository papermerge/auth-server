import { Container, PasswordInput, TextInput } from '@mantine/core';

export default function Login() {
  return (
    <Container>
      <TextInput m={"lg"} label="Username" placeholder="username" />
      <PasswordInput m={"lg"} label="Password" placeholder="password" />
    </Container>
  );
}