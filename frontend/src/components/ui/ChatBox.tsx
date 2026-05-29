"use client";

import api from "@/lib/api";
import { useState } from "react";

export default function ChatBox() {
    const [query, setQuery] = useState("");
    const [answer,setAnswer] = useState("");
    const [loading, setLoading] = useState(false);

    const askQuestion = async () => {
        try{
            setLoading(true);
            const response = await api.post("/query", { query });
            setAnswer(response.data.answer);
        } catch (error) {
            console.error("Error asking question:", error);
            alert("Failed to get answer.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-4 p-4 border rounded-md">
            <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about the uploaded lecture notes..."
                className="w-full p-2 border rounded"
            />
            <button
                onClick={askQuestion}
                className="px-4 py-2 bg-green-500 text-white rounded disabled:bg-gray-400"
                >
                {loading ? "Loading..." : "Ask"}
                </button>
            {answer && (
                <div className="border p-4 rounded">
                    <h2 className="text-lg font-bold mb-2">Answer:</h2>
                    <p>{answer}</p>
                </div>
            )}
        </div>
    );
};