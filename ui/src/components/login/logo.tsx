import Image from "next/image";

export default function Logo() {
  return (
    <div className="logo">
      <Image alt="Papermerge logo" width="112" height="108" src="/images/logo.svg" />
    </div>
  );
}