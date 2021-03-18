import React, { useState } from 'react'
import { Link } from 'react-router-dom'


const SongList = ({songs}) => {
    const [filter, setFilter] = useState("")
   
    return [
      <h2>Songs:</h2>,
      <form>
        <input id='songsearch' value={filter} onChange={({target}) => setFilter(target.value)}/>
      </form>,
      <div>{songs.filter(s => s.name.toLowerCase().startsWith(filter.toLowerCase())).map(
        s => <div><Link to={`/songs/${s.id}`}>[{s.id}] {s.name} ({s.tones})</Link></div>)}</div>
    ]
  }


  export default SongList