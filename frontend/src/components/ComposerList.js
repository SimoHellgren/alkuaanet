import React from 'react'

const ComposerList = ({composers}) => {
    return [
        composers.map(c => <div>{c.firstname} {c.lastname}</div>)
    ]
}

export default ComposerList