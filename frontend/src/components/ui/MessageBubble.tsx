// components/MessageBubble.tsx

import ReactMarkdown from "react-markdown";
interface MessageBubbleProps {
  content: string;
  role: "user" | "assistant";
}


export default function MessageBubble({content,role}: MessageBubbleProps) 
{

  return (

    <div
      className={
        role === "user"
          ? "bg-blue-100 ml-auto"
          : "bg-gray-100"
      }
    >

      <ReactMarkdown>
        {content}
      </ReactMarkdown>

    </div>
  );
}