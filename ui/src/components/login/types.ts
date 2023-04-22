export type InputProps = {
  onchange: (value: string) => void;
  type: "text" | "password";
  name: string;
  placeholder: string;
}


export type ClickEvent = React.MouseEvent<HTMLButtonElement, MouseEvent>;