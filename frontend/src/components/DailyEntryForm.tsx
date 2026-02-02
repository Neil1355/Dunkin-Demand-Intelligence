import { useState } from "react";
import { apiFetch } from '../utils/api';

export default function DailyEntryForm() {
  const [store_id, setStoreId] = useState(1);
  const [product_id, setProductId] = useState(3);
  const [date, setDate] = useState("");
  const [produced, setProduced] = useState(0);
  const [waste, setWaste] = useState(0);

  const submitDailyEntry = async () => {
    try {
      await apiFetch("/daily", {
        method: "POST",
        body: JSON.stringify({
          store_id,
          product_id,
          date,
          produced,
          waste
        })
      });

      const data = await res.json();
      console.log("Saved:", data);
      alert("Daily entry saved!");
    } catch (err) {
      console.error(err);
      alert("Error saving entry");
    }
  };

  return (
    <div>
      <h2>Daily Entry Form</h2>

      <input
        type="number"
        value={store_id}
        onChange={e => setStoreId(+e.target.value)}
        placeholder="Store ID"
      />

      <input
        type="number"
        value={product_id}
        onChange={e => setProductId(+e.target.value)}
        placeholder="Product ID"
      />

      <input
        type="date"
        value={date}
        onChange={e => setDate(e.target.value)}
      />

      <input
        type="number"
        value={produced}
        onChange={e => setProduced(+e.target.value)}
        placeholder="Produced"
      />

      <input
        type="number"
        value={waste}
        onChange={e => setWaste(+e.target.value)}
        placeholder="Waste"
      />

      <button onClick={submitDailyEntry}>Save</button>
    </div>
  );
}
