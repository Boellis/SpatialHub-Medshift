import axios from 'axios';

const BASE_URL = 'https://spatialhub-backend-823061962201.us-central1.run.app/api';

export async function fetchRawSensorData(_page = 1): Promise<any[]> {
    const response = await axios.get(`${BASE_URL}/api/raw/`);
    return response.data; // this is already an array
  }
  

export const fetchEnrichedSensorData = async (page: number) =>
  axios.get(`${BASE_URL}/enriched/?page=${page}`).then(res => res.data);

export const provisionHub = async (payload: {
  location: string;
  owner: string;
  workers: string[];
}) =>
  axios.post(`${BASE_URL}/provision/`, payload).then(res => res.data);
