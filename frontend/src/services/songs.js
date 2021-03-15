import axios from 'axios'
const config = require('../config.json')

const path = `${config.apiurl}/songs/`

const getAll = () => {
    const request = axios.get(path)
    return request.then(response => response.data)
}


export default { getAll }