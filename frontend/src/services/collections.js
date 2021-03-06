import axios from 'axios'
const config = require('../config.json')

const path = `${config.apiurl}/collections/`

const getAll = () => {
    const request = axios.get(path)
    return request.then(response => response.data)
}

const getById = async (id) => {
    const request = axios.get(`${path}${id}`)
    return request.then(response => response.data)
}

const getSongs = async (id) => {
    const request = axios.get(`${path}${id}/songs`)
    return request.then(response => response.data)
}

const create = async newCollection => {
    const response = await axios.post(path, newCollection)
    return response.data
}

const update = async (id, updatedCollection) => {
    const response = await axios.put(`${path}${id}`, updatedCollection)
    return response.data
}

const addSong = async (id, song_id) => {
    const response = await axios.put(`${path}${id}/songs/${song_id}`)
    return response.data
}

// eslint-disable-next-line import/no-anonymous-default-export
export default { getAll, create, update, getSongs, getById, addSong }