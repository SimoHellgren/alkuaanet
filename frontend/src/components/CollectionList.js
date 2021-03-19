import React from 'react'
import { Link } from 'react-router-dom'


const CollectionList = ({collections}) => {
    return <>
        {collections.map(c => <div key={c.id}><Link to={`/collections/${c.id}`}>{c.name}</Link></div>)}
    </>
}

export default CollectionList