import UploadBox from "@/components/ui/UploadBox";
import Link from "next/link";

export default function HomePage() {
    return (
      <main className="container mx-auto p-10">
      <h1 className="text-3xl font-bold mb-6">LectureMindAI</h1>
      <UploadBox />

      <div className="mt-6">

        <Link
          href="/chat"
          className="bg-black text-white px-4 py-2 rounded"
        >
          Go To Chat →
        </Link>

      </div>
    </main>
    );
  }