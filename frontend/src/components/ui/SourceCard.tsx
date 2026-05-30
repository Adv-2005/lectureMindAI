interface Source {
  filename: string;
  page: number;
}
interface SourceCardProps {
  source: Source;
  chunk: string;
}

export default function SourceCard({ source, chunk }: SourceCardProps) {

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