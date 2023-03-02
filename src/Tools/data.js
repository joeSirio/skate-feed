
const getAll = async (id) => {
    const results = await fetch(`http://127.0.0.1/get/${id}`, {method: 'GET'})
    const data = await results.json()

    return data
}