import { Container } from '@mantine/core';
import DBLogin from '../components/DBLogin/DBLogin';
import classes from "./Login.module.css";

export function LoginPage() {
  return (
    <Container className={classes.login}>
      <DBLogin />
    </Container>
  );
}
