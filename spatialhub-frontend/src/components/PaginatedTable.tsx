// src/components/PaginatedTable.tsx
import React from 'react';

interface PaginatedTableProps {
  data: any[];
  page: number;
  setPage: (page: number) => void;
}

export const PaginatedTable: React.FC<PaginatedTableProps> = ({ data, page, setPage }) => {
  if (!Array.isArray(data)) {
    return <p>Error: Data is not in an array format.</p>;
  }

  if (data.length === 0) {
    return <p>No data found on this page.</p>;
  }

  const headers = Object.keys(data[0]);

  return (
    <div>
      <table>
        <thead>
          <tr>
            {headers.map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
            {Array.isArray(data) && data.length > 0 ? (
                data.map((item, index) => (
                <tr key={index}>
                    {Object.values(item).map((val, i) => (
                    <td key={i}>{JSON.stringify(val)}</td>
                    ))}
                </tr>
                ))
            ) : (
                <tr>
                <td colSpan={10}>No data available</td>
                </tr>
            )}
        </tbody>

      </table>
      <div className="pagination">
        <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}>
          Previous
        </button>
        <span>Page {page}</span>
        <button onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
};
