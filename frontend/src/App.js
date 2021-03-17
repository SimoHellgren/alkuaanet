import { useState, useEffect } from 'react'
import {
  BrowserRouter as Router,
  Switch, Route, Link, Redirect
} from 'react-router-dom'

import SongForm from './components/SongForm'
import SongList from './components/SongList'
import ComposerList from './components/ComposerList'
import CollectionList from './components/CollectionList'
import songService from './services/songs'
import composerService from './services/composers'
import collectionService from './services/collections'

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
  const [collections, setCollections] = useState([])

  useEffect( () => {
    songService.getAll().then(s => setSongs(s.sort(sortById)))
  }, [])
  
  useEffect( () => {
    composerService.getAll().then(c => setComposers(c.sort(sortByLastname)))
  }, [])
  
  useEffect( () => {
    collectionService.getAll().then(c => setCollections(c.sort(sortById)))
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

  const padding = {
    padding: 5
  }

  return [
    <Router>
      <div>
        <Link style={padding} to='/songs'>songs</Link>
        <Link style={padding} to='/composers'>composers</Link>
        <Link style={padding} to='/collections'>collections</Link>
      </div>

      <Switch>
        <Route path='/songs'>
          <SongsView songs={songs} handleCreateSong={handleCreateSong} handleUpdateSong={handleUpdateSong}/>
        </Route>

        <Route path='/composers'>
          <ComposerList composers={composers}/>
        </Route>

        <Route path='/collections'>
          <CollectionList collections={collections}/>
        </Route>

        <Route path='/'>
          <Redirect to='/songs'/>
        </Route>

      </Switch>
    </Router>,
  ]
}

export default App;
