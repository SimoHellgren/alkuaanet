import React from 'react'
import { useFormField } from '../hooks'

const SongForm = ({ createSong }) => {
    const { reset: resetName, ...name} = useFormField('text', '')
    const { reset: resetTones, ...tones} = useFormField('text', '')
  
    const addSong = (event) => {
      event.preventDefault()
  
      createSong(
        { 
          name: name.value, 
          tones: tones.value 
        }
      )

      resetName()
      resetTones()
        
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