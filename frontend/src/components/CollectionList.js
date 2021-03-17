import React from 'react'

const CollectionList = ({collections}) => {
    return [
        collections.map(c => <div>{c.name}</div>)
    ]
}

export default CollectionList