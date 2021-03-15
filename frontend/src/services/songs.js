import axios from 'axios'
const config = require('../config.json')

const path = `${config.apiurl}/songs/`

const getAll = () => {
    const request = axios.get(path)
    return request.then(response => response.data)
}

const create = async newSong => {
    const response = await axios.post(path, newSong)
    return response.data
}

export default { getAll, create }