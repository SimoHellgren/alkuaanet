import React from 'react'
import { useFormField } from '../hooks'
import { Link } from 'react-router-dom'


const SongList = ({songs}) => {
    const { reset: _, ...filter} = useFormField('text', '')

    const showSongs = songs.filter(
      s => s.name.toLowerCase().startsWith(filter.value.toLowerCase())
    )

    return <>
      <h2>Songs:</h2>
      <form>
        <input {...filter}/>
      </form>
      <div>
        {showSongs.map(s => 
          <div key={s.id}>
            <Link to={`/songs/${s.id}`}>
              [{s.id}] {s.name} ({s.tones})
            </Link>
          </div>
        )}
      </div>
    </>
  }


  export default SongList