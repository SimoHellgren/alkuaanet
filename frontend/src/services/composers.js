import axios from 'axios'
const config = require('../config.json')

const path = `${config.apiurl}/composers/`

const getAll = () => {
    const request = axios.get(path)
    return request.then(response => response.data)
}

const getSongs = (id) => {
    const request = axios.get(`${path}${id}/songs`)
    return request.then(response => response.data)
}

const create = async newComposer => {
    const response = await axios.post(path, newComposer)
    return response.data
}

const update = async (id, updatedComposer) => {
    const response = await axios.put(`${path}${id}`, updatedComposer)
    return response.data
}

// eslint-disable-next-line import/no-anonymous-default-export
export default { getAll, create, update, getSongs }