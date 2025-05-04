import { useEffect, useState } from "react";
import axios from "axios";

export function EnrichedSensorData() {
  const [data, setData] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => { // Fetch enriched sensor data on component mount
    axios
      .get("https://spatialhub-backend-823061962201.us-central1.run.app/api/enriched/")
      .then((res) => {
        const flat = res.data.flat(); // Flatten the data if it's nested
        setData(flat);
      })
      .catch((err) => console.error("Failed to fetch enriched data:", err));
  }, []);

  const paginatedData = data.slice( // Get the current page data
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );
  const totalPages = Math.ceil(data.length / itemsPerPage); // Calculate total pages

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Enriched Sensor Data</h2>
      <table className="min-w-full border text-sm">
        <thead>
          <tr>
            {paginatedData[0] &&
              Object.keys(paginatedData[0]).map((key) => (
                <th className="border px-2 py-1" key={key}>
                  {key}
                </th>
              ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.length > 0 ? (
            paginatedData.map((item, i) => (
              <tr key={i}>
                {Object.values(item).map((val, j) => (
                  <td className="border px-2 py-1" key={j}>
                    {String(val)}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={10} className="text-center p-2">
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="mt-4 flex gap-2">
        <button
          onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
          disabled={currentPage === 1}
          className="px-2 py-1 bg-gray-200 rounded"
        >
          Prev
        </button>
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-2 py-1 bg-gray-200 rounded"
        >
          Next
        </button>
      </div>
    </div>
  );
}
