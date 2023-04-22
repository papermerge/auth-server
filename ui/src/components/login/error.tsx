
type Args = {
  message: string;
}

function Error({message}: Args) {
  return (
    <>
      <div className='text-danger m-2'>
        {message}
      </div>
    </>
  )
}

export default Error;