import axios from 'axios'
const config = require('../config.json')

const path = `${config.apiurl}/collections/`

const getAll = () => {
    const request = axios.get(path)
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

// eslint-disable-next-line import/no-anonymous-default-export
export default { getAll, create, update }