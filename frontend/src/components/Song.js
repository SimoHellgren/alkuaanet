import React, { useState } from 'react'

const Song = ({song: {id, name, tones}, updateSong}) => {
  const [newName, setNewName] = useState(name)
  const [newTones, setNewTones] = useState(tones)

  const [visible, setVisible] = useState(false)

  const toggleVisible = () => setVisible(!visible)

  const handleUpdate = (event) => {
    event.preventDefault()

    const updatedSong = {
      id: id,
      name: newName,
      tones: newTones
    }

    updateSong(id, updatedSong)

    setVisible(false)
  }

  return [
  <div onClick={toggleVisible}>[{id}] {name} ({tones}) </div>,
  <div style={{display: visible ? '' : 'none'}}>
    <form onSubmit={handleUpdate}>
      <div>edit name: <input name='newname' value={newName} onChange={({target}) => setNewName(target.value)}/></div>
      <div>edit tones: <input name='newtones' value={newTones} onChange={({target}) => setNewTones(target.value)}/></div>
      <button type='submit'>Save</button>
    </form>
  </div>
]
      
  }

  export default Song