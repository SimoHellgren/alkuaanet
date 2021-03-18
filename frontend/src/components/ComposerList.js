import React from 'react'
import { Link } from 'react-router-dom'

const ComposerList = ({composers}) => {
    return [
        composers.map(c => <div>
            <Link to={`/composers/${c.id}`}>{c.firstname} {c.lastname}</Link>
        </div>)
    ]
}

export default ComposerList