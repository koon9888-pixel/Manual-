
import React, { useState } from "react";
import axios from "axios";

export default function Dashboard() {

  const [result, setResult] = useState(null);

  const analyze = async () => {
    const response = await axios.post(
      "http://localhost:8000/diagnostics/analyze",
      {
        rpm: 3000,
        rail_actual: 60,
        rail_target: 80,
        boost: 90,
        maf: 12,
        coolant_temp: 85
      }
    );

    setResult(response.data);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>1VD-FTV Intelligent Diagnostics</h1>

      <button onClick={analyze}>
        Analyze Stream Data
      </button>

      {result && (
        <pre>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
