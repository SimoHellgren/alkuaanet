import { useState, useEffect } from 'react'
import {
  Switch, Route, Link, Redirect, useRouteMatch
} from 'react-router-dom'

import Song from './components/Song'
import SongForm from './components/SongForm'
import SongList from './components/SongList'
import Composer from './components/Composer'
import ComposerList from './components/ComposerList'
import CollectionList, { CollectionView } from './components/CollectionList'
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

const SongsView = ({songs, handleCreateSong}) => {
  return [
    <SongForm createSong={handleCreateSong}/>,
    <SongList songs={songs}/>
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

  const collectionMatch = useRouteMatch('/collections/:id')
  const collectionId = collectionMatch 
    ? Number(collectionMatch.params.id) 
    : null

  const songMatch = useRouteMatch('/songs/:id')
  const song = songMatch
    ? songs.find(s => s.id === Number(songMatch.params.id))
    : null

  const composerMatch = useRouteMatch('/composers/:id')
  const composer = composerMatch
    ? composers.find(s => s.id === Number(composerMatch.params.id))
    : null

  const padding = {
    padding: 5
  }

  return [
      <div>
        <Link style={padding} to='/songs'>songs</Link>
        <Link style={padding} to='/composers'>composers</Link>
        <Link style={padding} to='/collections'>collections</Link>
      </div>,

      <Switch>
        <Route path='/songs/:id'>
          <Song song={song} updateSong={handleUpdateSong}/>
        </Route>

        <Route path='/songs'>
          <SongsView songs={songs} handleCreateSong={handleCreateSong}/>
        </Route>

        <Route path='/composers/:id'>
          <Composer composer={composer}/>
        </Route>

        <Route path='/composers'>
          <ComposerList composers={composers}/>
        </Route>

        <Route path='/collections/:id'>
          <CollectionView id={collectionId}/>
        </Route>

        <Route path='/collections'>
          <CollectionList collections={collections}/>
        </Route>

        <Route path='/'>
          <Redirect to='/songs'/>
        </Route>

      </Switch>
  ]
}

export default App;
