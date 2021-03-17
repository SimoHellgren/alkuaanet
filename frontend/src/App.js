import { useState, useEffect } from 'react'
import SongForm from './components/SongForm'
import SongList from './components/SongList'
import ComposerList from './components/ComposerList'
import songService from './services/songs'
import composerService from './services/composers'

import './App.css';

const sortById = (a,b) => {
  if (a.id > b.id) return 1
  if (a.id === b.id) return 0
  return -1
}

const sortByLastname = (a,b) => {
  if (a.lastname > b.lastname) return 1
  if (a.lastname === b.lastname) return 0
  return -1
}

const SongsView = ({songs, handleCreateSong, handleUpdateSong}) => {
  return [
    <SongForm createSong={handleCreateSong}/>,
    <SongList songs={songs} songUpdateFunc={handleUpdateSong}/>
  ]
}

function App() {
  const [songs, setSongs] = useState([])
  const [composers, setComposers] = useState([])

  useEffect( () => {
    songService.getAll().then(s => setSongs(s.sort(sortById)))
  }, [])
  
  useEffect( () => {
    composerService.getAll().then(s => setComposers(s.sort(sortByLastname)))
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
    <SongsView songs={songs} handleCreateSong={handleCreateSong} handleUpdateSong={handleUpdateSong}/>,
    <ComposerList composers={composers}/>
  ]
}

export default App;
