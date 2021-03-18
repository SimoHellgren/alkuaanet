import React, { useEffect, useState } from 'react'
import collectionService from '../services/collections'

const Collection = ({ collection: { id, name }}) => {
    const [songs, setSongs] = useState([])

    useEffect( () => {
        collectionService.getSongs(id).then(s => setSongs(s))
    }, [id])

    return [
        <h2>Songs in {name}:</h2>,
        songs.map(s => <div>{s.name} ({s.tones})</div>)
    ]
}


export default Collection