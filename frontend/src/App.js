import { useState, useEffect } from 'react'
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

  return (
    <SongList songs={songs}/>
  )
}

export default App;
