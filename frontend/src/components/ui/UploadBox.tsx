"use client";

import { useState } from "react";
import api from "@/lib/api";

export default function UploadBox() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setloading] = useState(false);

    const uploadFile = async () => {
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);
        try {
            setloading(true);
            const response = await api.post("/upload", formData);
            console.log(response.data);
            alert("File uploaded successfully!");
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("Failed to upload file.");
        } finally {
            setloading(false);
        }
    };
    return (
        <div className="space-y-4 p-4 border rounded-md">
            <input
                type="file"
                accept=".pdf"
                onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0){
                        setFile(e.target.files[0]);
                    }
                }}
            />
            <button
                onClick={uploadFile}
                className = "px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
            > 
                {loading ? "Uploading..." : "Upload PDF"}  
            </button>
        </div>
    );
}