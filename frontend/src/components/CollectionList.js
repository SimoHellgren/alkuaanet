import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import collectionService from '../services/collections'

const Collection = ({collection: {id, name}}) => {

    return [
        <div>{name}</div>
    ]
}

export const CollectionView = ({ id }) => {
    const [collection, setCollection] = useState({})
    const [songs, setSongs] = useState([])

    useEffect( () => {
        collectionService.getById(id).then(c => setCollection(c))
    }, [id])

    useEffect( () => {
        collectionService.getSongs(id).then(s => setSongs(s))
    }, [id])

    return [
        <h2>Songs in {collection.name}:</h2>,
        songs.map(s => <div>{s.name} ({s.tones})</div>)
    ]
}

const CollectionList = ({collections}) => {
    return [
        collections.map(c => <Link to={`/collections/${c.id}`}><Collection collection={c}/></Link>)
    ]
}

export default CollectionList