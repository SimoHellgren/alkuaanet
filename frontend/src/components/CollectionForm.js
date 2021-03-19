import React, { useState } from 'react'
import collectionService from '../services/collections'


const CollectionForm = ({collection, songs}) => {
    const [songId, setSongId] = useState(null)

    const addSong = event=> {
        event.preventDefault()

        collectionService.addSong(collection.id, songId)

    }

    return <>
        <h2>Add song to {collection.name}</h2>
        <form onSubmit={addSong}>
          <select onChange={e => setSongId(e.target.value)}>
              {songs.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button type='submit'>Add!</button>
        </form>
      </>
}


export default CollectionForm