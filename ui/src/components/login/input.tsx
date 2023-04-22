import { useState } from 'react';
import type { InputProps } from './types';


export default function Input({onchange, ...props}: InputProps) {
  const [value, setValue] = useState('');

  const changeHandle = (event: React.SyntheticEvent) => {
    let target = event.target as HTMLInputElement;
    setValue(target.value);
    onchange(target.value);
  }

  return (
    <>
      <input
        className="form-control"
        value={value}
        onChange={changeHandle}
        type={props.type}
        name={props.name}
        placeholder={props.placeholder}
      />
    </>
  );
}
