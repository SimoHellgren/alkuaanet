import React, { useState } from 'react'
import Song from './Song'


const SongList = ({songs, songUpdateFunc}) => {
    const [filter, setFilter] = useState("")
   
    return [
      <h2>Songs:</h2>,
      <form>
        <input id='songsearch' value={filter} onChange={({target}) => setFilter(target.value)}/>
      </form>,
      <div>{songs.filter(s => s.name.toLowerCase().startsWith(filter.toLowerCase())).map(s => <Song key={s.id} song={s} updateSong={songUpdateFunc}/>)}</div>
    ]
  }


  export default SongList