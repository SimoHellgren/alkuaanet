import React, { useEffect, useState } from 'react'
import composerService from '../services/composers'

const Composer = ({composer: {id, lastname, firstname}}) => {
    const [songs, setSongs] = useState([])

    useEffect( () => {
        composerService.getSongs(id).then(
            s => setSongs(s)
        )
    }, [id])

    return <>
        <h2>Songs by {firstname} {lastname}</h2>
        <div>{songs.map(
            s => <div key={s.id}>{s.name}</div>
        )}</div>
    </>
}



export default Composer