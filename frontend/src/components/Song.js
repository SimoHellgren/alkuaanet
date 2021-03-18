import React, { useState } from 'react'

const Song = ({song: {id, name, tones}, updateSong}) => {
  const [newName, setNewName] = useState(name)
  const [newTones, setNewTones] = useState(tones)

  const handleUpdate = (event) => {
    event.preventDefault()

    const updatedSong = {
      id: id,
      name: newName,
      tones: newTones
    }

    updateSong(id, updatedSong)

  }

  return [
  <div>[{id}] {name} ({tones}) </div>,
  <div>
    <form onSubmit={handleUpdate}>
      <div>edit name: <input name='newname' value={newName} onChange={({target}) => setNewName(target.value)}/></div>
      <div>edit tones: <input name='newtones' value={newTones} onChange={({target}) => setNewTones(target.value)}/></div>
      <button type='submit'>Save</button>
    </form>
  </div>
]
      
  }

  export default Song