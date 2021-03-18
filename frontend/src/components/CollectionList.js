import React from 'react'
import { Link } from 'react-router-dom'


const CollectionList = ({collections}) => {
    return [
        collections.map(c => <div><Link to={`/collections/${c.id}`}>{c.name}</Link></div>)
    ]
}

export default CollectionList