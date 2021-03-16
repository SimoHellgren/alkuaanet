import React, { useState } from 'react'

const SongForm = ({ createSong }) => {
    const [name, setName] = useState("")
    const [tones, setTones] = useState("")
  
    const addSong = (event) => {
      event.preventDefault()
  
      createSong(
        { name, tones }
      )
        
      setName("")
      setTones("")
    }
    
    return [
      <h2>Create new song</h2>,
      <form onSubmit={addSong}>
        <div>name: <input id='name' value={name} onChange={({target}) => setName(target.value)}/></div>
        <div>tones: <input id='tones' value={tones} onChange={({target}) => setTones(target.value)}/></div>
        <button type='submit'>Make!</button>
      </form>
    ]
  
  }

  export default SongForm