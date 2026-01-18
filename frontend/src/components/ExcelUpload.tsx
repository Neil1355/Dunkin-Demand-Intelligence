export default function ExcelUpload() {
  const uploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const formData = new FormData();
    formData.append("file", e.target.files[0]);

    const res = await fetch("https://YOUR_BACKEND_URL/excel/upload", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    alert(JSON.stringify(data));
  };

  return <input type="file" onChange={uploadFile} />;
}
