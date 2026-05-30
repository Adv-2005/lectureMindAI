"use client";

import api from "@/lib/api";
import { useState } from "react";
import SourceCard from "@/components/ui/SourceCard";
import MessageBubble from "@/components/ui/MessageBubble";
interface Source {
  filename: string;
  page: number;
}

interface QueryResponse {
    answer?: string;
    sources?: Source[];
    context?: string[];
    chunks?: string[];
}

export default function ChatBox() {
    const [query, setQuery] = useState("");
    const [answer, setAnswer] = useState<string>("");
    const [loading, setLoading] = useState(false);
    const [sources, setSources] = useState<Source[]>([]);
    const [chunks, setChunks] = useState<string[]>([]);
    const askQuestion = async () => {
        try{
            setLoading(true);
            const response = await api.post("/query", { query });
        const data = response.data as QueryResponse;
        const responseChunks = data.context ?? data.chunks ?? [];

        setAnswer(data.answer ?? "");
        setSources(data.sources ?? []);
        setChunks(responseChunks);
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

  <div className="space-y-4">

    <div className="border rounded p-4">

      <h2 className="font-bold mb-2">
        Answer
      </h2>

      <MessageBubble
  content={answer}
  role="assistant"
/>

    </div>

    <div>

      <h3 className="font-semibold mb-2">
        Sources
      </h3>

      <div className="space-y-2">

        {sources.map((source, index) => (

          <SourceCard
            key={index}
            source={source}
            chunk={chunks[index] ?? ""}
          />

        ))}

      </div>

    </div>

  </div>

)}
        </div>
    );
};