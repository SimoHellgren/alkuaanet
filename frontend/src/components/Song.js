import React from 'react'
import { useFormField } from '../hooks'

const Song = ({song: {id, name, tones}, updateSong}) => {
  const newName = useFormField('text', name)
  const newTones = useFormField('text', tones)

  const handleUpdate = (event) => {
    event.preventDefault()

    const updatedSong = {
      id: id,
      name: newName.value,
      tones: newTones.value
    }

    updateSong(id, updatedSong)

  }

  return [
  <div>[{id}] {name} ({tones}) </div>,
  <div>
    <form onSubmit={handleUpdate}>
      <div>edit name: <input {...newName}/></div>
      <div>edit tones: <input {...newTones}/></div>
      <button type='submit'>Save</button>
    </form>
  </div>
]
      
  }

  export default Song