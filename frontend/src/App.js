import { useState, useEffect } from 'react'
import SongForm from './components/SongForm'
import SongList from './components/SongList'
import songService from './services/songs'

import './App.css';

const sortById = (a,b) => {
  if (a.id > b.id) return 1
  if (a.id === b.id) return 0
  return -1
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

  const handleUpdateSong = async (id, songdata) => {
    try {
      const response = await songService.update(id, songdata)
      setSongs(songs.map(s => s.id === id ? response : s))
    } catch (error){
      console.log(error)
    }
  }


  return [
    <SongForm createSong={handleCreateSong}/>,
    <SongList songs={songs} songUpdateFunc={handleUpdateSong}/>
  ]
}

export default App;
