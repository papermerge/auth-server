import styles from "./logo.module.scss";

export default function Logo() {
  return (
    <div className={styles.logo}>
      <img width="112px" height="108px" src="/images/logo.svg" />
    </div>
  );
}