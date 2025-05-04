import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

interface SensorData {
  id: number;
  hub_id: string;
  sensor_name: string;
  sensor_val: number;
  datetime: string;
}

export const SensorTrends = () => {
  const [data, setData] = useState<SensorData[]>([]);
  const [selectedSensor, setSelectedSensor] = useState<string>('atemp');
  const [selectedHub, setSelectedHub] = useState<string>('');
  const [compareAllHubs, setCompareAllHubs] = useState<boolean>(false);

  useEffect(() => {
    axios.get('https://spatialhub-backend-823061962201.us-central1.run.app/api/enriched/')
      .then((res) => {
        const flat = Array.isArray(res.data) && Array.isArray(res.data[0]) ? res.data[0] : res.data;
        setData(flat);
      })
      .catch((err) => {
        console.error('Error fetching enriched data:', err);
      });
  }, []);

  const sensorOptions = Array.from(new Set(data.map((d) => d.sensor_name))).sort();
  const hubOptions = Array.from(new Set(data.map((d) => d.hub_id))).sort();

  const filteredData = data
    .filter((d) => d.sensor_name === selectedSensor)
    .filter((d) => compareAllHubs || d.hub_id === selectedHub)
    .sort((a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime());

  const groupedData: { [key: string]: any }[] = [];

  filteredData.forEach((item) => {
    const time = new Date(item.datetime).toLocaleString();
    const existing = groupedData.find((entry) => entry.datetime === time);

    if (existing) {
      existing[item.hub_id] = item.sensor_val;
    } else {
      groupedData.push({
        datetime: time,
        [item.hub_id]: item.sensor_val,
      });
    }
  });

  return (
    <div className="p-4 max-w-screen-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">Sensor Trends Over Time</h2>

      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="block font-medium mb-1">Sensor Type</label>
          <select
            value={selectedSensor}
            onChange={(e) => setSelectedSensor(e.target.value)}
            className="p-2 border rounded"
          >
            {sensorOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-medium mb-1">Hub ID</label>
          <select
            value={selectedHub}
            onChange={(e) => setSelectedHub(e.target.value)}
            disabled={compareAllHubs}
            className="p-2 border rounded"
          >
            {hubOptions.map((hub) => (
              <option key={hub} value={hub}>{hub}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center">
          <label className="mr-2 font-medium">Compare All Hubs</label>
          <input
            type="checkbox"
            checked={compareAllHubs}
            onChange={() => setCompareAllHubs(!compareAllHubs)}
          />
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={groupedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="datetime" />
          <YAxis />
          <Tooltip />
          <Legend />
          {(compareAllHubs ? hubOptions : [selectedHub]).map((hub, i) => (
            <Line key={hub} type="monotone" dataKey={hub} stroke={`hsl(${i * 60}, 70%, 50%)`} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
