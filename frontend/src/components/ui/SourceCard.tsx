interface Source {
  filename: string;
  page: number;
}
interface SourceCardProps {
  source: Source | null;
  chunk: string;
}

export default function SourceCard({ source, chunk }: SourceCardProps) {

  if (!source) {
    return null;
  }

  return (

    <div className="border rounded p-3">

      <h4 className="font-semibold">
        {source.filename}
      </h4>

      <p>
        Page {source.page}
      </p>

      <p className="text-sm">
        {chunk.slice(0, 250)}...
      </p>

    </div>
  );
}