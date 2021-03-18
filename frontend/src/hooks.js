import { useState } from 'react'

export const useFormField = (type, initval) => {
    const [value, setValue] = useState(initval)

    const onChange = (event) => {
        setValue(event.target.value)
    }    

    return {
        type,
        value,
        onChange
    }
}