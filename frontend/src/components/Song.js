import React from 'react'

const Song = ({song: {id, name, tones}}) => {
    return (
      <div>[{id}] {name} ({tones}) </div>
    )
  }

  export default Song