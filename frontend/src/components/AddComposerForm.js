import React from 'react'
import { useFormField } from '../hooks'


const AddComposerForm = ({createComposer}) => {
    const {reset: resetLastname, ...lastname} = useFormField('text', '')
    const {reset: resetFirstname, ...firstname} = useFormField('text', '')

    const addComposer = event => {
        event.preventDefault()

        createComposer(
            lastname.value, 
            firstname.value
        )

        resetLastname()
        resetFirstname()
    }

    return <>
        <h2>Add new composer</h2>
        <form onSubmit={addComposer}>
            <div>lastname: <input {...lastname}></input></div>
            <div>firstname: <input {...firstname}></input></div>
            <button type='submit'>Add composer!</button>
        </form>
    </>
}

export default AddComposerForm