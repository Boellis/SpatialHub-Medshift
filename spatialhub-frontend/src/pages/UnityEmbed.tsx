import { useState } from "react";

const UnityEmbed = () => {
  const [width, setWidth] = useState(960);
  const [height, setHeight] = useState(600);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Unity WebGL Simulation</h2>

      <div className="mb-4 space-x-4">
        <label>
          Width (px):
          <input
            type="number"
            className="ml-2 p-1 border rounded"
            value={width}
            onChange={(e) => setWidth(parseInt(e.target.value))}
          />
        </label>
        <label>
          Height (px):
          <input
            type="number"
            className="ml-2 p-1 border rounded"
            value={height}
            onChange={(e) => setHeight(parseInt(e.target.value))}
          />
        </label>
      </div>

      <iframe
        src="https://itch.io/embed-upload/10601498?color=ffffff"
        title="Unity WebGL Build"
        width={width}
        height={height}
        allowFullScreen
        className="border shadow-lg"
      ></iframe>
    </div>
  );
};

export default UnityEmbed;
