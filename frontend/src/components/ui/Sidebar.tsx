// components/Sidebar.tsx
interface SidebarProps {
  files: string[];
}
export default function Sidebar({files}: SidebarProps) 
{

  return (

    <div className="w-64 border-r">

      <h2 className="font-bold">
        Uploaded PDFs
      </h2>

      {files.map((file) => (

        <div
          key={file}
          className="p-2"
        >
          {file}
        </div>

      ))}

    </div>
  );
}