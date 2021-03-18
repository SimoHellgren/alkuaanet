import React from 'react'
import { useFormField } from '../hooks'

const SongForm = ({ createSong }) => {
    const name = useFormField('text', '')
    const tones = useFormField('text', '')
  
    const addSong = (event) => {
      event.preventDefault()
  
      createSong(
        { 
          name: name.value, 
          tones: tones.value 
        }
      )

      name.reset()
      tones.reset()
        
    }
    
    return [
      <h2>Create new song</h2>,
      <form onSubmit={addSong}>
        <div>name: <input {...name}/></div>
        <div>tones: <input {...tones}/></div>
        <button type='submit'>Make!</button>
      </form>
    ]
  
  }

  export default SongForm