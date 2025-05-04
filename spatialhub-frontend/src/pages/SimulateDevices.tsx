import { useEffect, useState } from "react";
import axios from "axios";

const CLOUD_FUNCTION_URL =
  "https://us-central1-interviewing-457222.cloudfunctions.net/ingest_data_publisher";
const COMMAND_URL =
  "https://spatialhub-backend-823061962201.us-central1.run.app/api/send-command/";

type SensorName = "ph" | "do" | "atemp" | "wtemp" | "hum" | "co2";

const sensorTypes: SensorName[] = ["ph", "do", "atemp", "wtemp", "hum", "co2"];

const sensorAddressMap: Record<SensorName, string> = {
  ph: "99",
  do: "97",
  atemp: "102",
  wtemp: "102",
  hum: "101",
  co2: "104",
};

const SimulateDevices = () => {
  const [hubIds, setHubIds] = useState<string[]>([]);
  const [selectedHubId, setSelectedHubId] = useState("");
  const [selectedSensors, setSelectedSensors] = useState<SensorName[]>([]);
  const [batchSize, setBatchSize] = useState(5);
  const [batchCount, setBatchCount] = useState(3);
  const [intervalMs, setIntervalMs] = useState(1000);
  const [log, setLog] = useState<string[]>([]);
  const [pumpAmount, setPumpAmount] = useState(10);

  useEffect(() => {
    axios
      .get("https://spatialhub-backend-823061962201.us-central1.run.app/api/hub/")
      .then((res) => setHubIds(res.data.map((h: any) => h.hub_id)))
      .catch(console.error);
  }, []);

  const getRandomValue = (sensor: SensorName): number => {
    const valueRanges: Record<SensorName, [number, number]> = {
      ph: [0.0, 14.0],
      do: [0.0, 2000.0],
      atemp: [32.0, 110.0],
      wtemp: [32.0, 110.0],
      hum: [0.0, 100.0],
      co2: [400.0, 5000.0],
    };
    const [min, max] = valueRanges[sensor];
    return parseFloat((Math.random() * (max - min) + min).toFixed(2));
  };

  const sendPayload = async (payload: any) => {
    try {
      await axios.post(CLOUD_FUNCTION_URL, payload);
      setLog((prev) => [`Sent ${payload.sensor_name} (${payload.sensor_val})`, ...prev.slice(0, 19)]);
    } catch (e) {
      setLog((prev) => [`Error sending ${payload.sensor_name}: ${e}`, ...prev.slice(0, 19)]);
    }
  };

  const simulateBatch = async () => {
    if (!selectedHubId || selectedSensors.length === 0) {
      alert("Please select a hub and at least one sensor.");
      return;
    }

    for (let b = 0; b < batchCount; b++) {
      const batchPayloads = Array.from({ length: batchSize }).flatMap(() =>
        selectedSensors.map((sensor) => {
          const sensor_val = getRandomValue(sensor);
          return {
            hub_id: selectedHubId,
            sensor_name: sensor,
            device_addr: sensorAddressMap[sensor],
            sensor_val,
            datetime: new Date().toISOString(),
            sensor_id: `${selectedHubId}_${sensorAddressMap[sensor]}`,
            collection_type: "sensor_data",
          };
        })
      );

      for (const payload of batchPayloads) {
        await sendPayload(payload);
      }

      if (b < batchCount - 1) {
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
      }
    }
  };

  const sendPumpCommand = async () => {
    if (!selectedHubId) {
      alert("Please select a hub to send command");
      return;
    }
    try {
      await axios.post(COMMAND_URL, {
        hub_id: selectedHubId,
        command: `D,${pumpAmount}`,
      });
      setLog((prev) => [`Sent Pump Command: D,${pumpAmount}`, ...prev.slice(0, 19)]);
    } catch (e) {
      setLog((prev) => [`Error sending pump command: ${e}`, ...prev.slice(0, 19)]);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">Simulate Devices</h2>

      <div className="mb-4">
        <label className="mr-2 font-medium">Select Hub:</label>
        <select
          className="border p-2"
          value={selectedHubId}
          onChange={(e) => setSelectedHubId(e.target.value)}
        >
          <option value="">-- Choose Hub --</option>
          {hubIds.map((h) => (
            <option key={h} value={h}>
              {h}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="mr-2 font-medium">Sensor Types:</label>
        {sensorTypes.map((sensor) => (
          <label key={sensor} className="mr-3">
            <input
              type="checkbox"
              value={sensor}
              onChange={(e) => {
                const val = e.target.value as SensorName;
                setSelectedSensors((prev) =>
                  prev.includes(val) ? prev.filter((s) => s !== val) : [...prev, val]
                );
              }}
              checked={selectedSensors.includes(sensor)}
            />{" "}
            {sensor}
          </label>
        ))}
      </div>

      <div className="mb-4 flex gap-4">
        <label>
          Batches:
          <input
            type="number"
            className="ml-2 p-1 border"
            value={batchCount}
            onChange={(e) => setBatchCount(Number(e.target.value))}
          />
        </label>
        <label>
          Readings per Batch:
          <input
            type="number"
            className="ml-2 p-1 border"
            value={batchSize}
            onChange={(e) => setBatchSize(Number(e.target.value))}
          />
        </label>
        <label>
          Interval (ms):
          <input
            type="number"
            className="ml-2 p-1 border"
            value={intervalMs}
            onChange={(e) => setIntervalMs(Number(e.target.value))}
          />
        </label>
      </div>

      <div className="mb-4">
        <label>
          Pump Amount (ml):
          <input
            type="number"
            className="ml-2 p-1 border"
            value={pumpAmount}
            onChange={(e) => setPumpAmount(Number(e.target.value))}
          />
        </label>
      </div>

      <button
        onClick={simulateBatch}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 mr-2"
      >
        Start Simulation
      </button>

      <button
        onClick={sendPumpCommand}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Send Pump Command
      </button>

      <div className="mt-4">
        <h3 className="font-medium">Logs</h3>
        <ul className="text-sm text-gray-700 max-h-64 overflow-y-auto">
          {log.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default SimulateDevices;
