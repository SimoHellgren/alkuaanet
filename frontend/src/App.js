import { useState, useEffect } from 'react'
import SongList from './components/SongList'
import songService from './services/songs'

import './App.css';

const sortById = (a,b) => {
  if (a.id > b.id) return 1
  if (a.id === b.id) return 0
  return -1
}

const SongForm = ({ createSong }) => {
  const [name, setName] = useState("")
  const [tones, setTones] = useState("")

  const addSong = (event) => {
    event.preventDefault()

    createSong(
      { name, tones }
    )
      
    setName("")
    setTones("")
  }
  
  return [
    <h2>Create new song</h2>,
    <form onSubmit={addSong}>
      <div>name: <input id='name' value={name} onChange={({target}) => setName(target.value)}/></div>
      <div>tones: <input id='tones' value={tones} onChange={({target}) => setTones(target.value)}/></div>
      <button type='submit'>Make!</button>
    </form>
  ]

}


function App() {
  const [songs, setSongs] = useState([])

  useEffect( () => {
    songService.getAll().then(s => setSongs(s.sort(sortById)))
  }, [])

  const handleCreateSong = async (song) => {
    try {
      const response = await songService.create(song)
      setSongs(songs.concat(response))
      
    } catch (error) {
      console.log(error)
    }
  }


  return [
    <SongForm createSong={handleCreateSong}/>,
    <SongList songs={songs}/>
  ]
}

export default App;
