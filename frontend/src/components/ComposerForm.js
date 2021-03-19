import React, { useState } from 'react'
import composerService from '../services/composers'


const ComposerForm = ({composer, songs}) => {
    const [songId, setSongId] = useState(null)

    const addSong = event=> {
        event.preventDefault()

        composerService.addSong(composer.id, songId)

    }

    return <>
        <h2>Add song for {composer.firstname} {composer.lastname}</h2>
        <form onSubmit={addSong}>
          <select onChange={e => setSongId(e.target.value)}>
              {songs.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button type='submit'>Add!</button>
        </form>
      </>
}


export default ComposerForm