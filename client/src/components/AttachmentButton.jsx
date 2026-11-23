import { useRef } from "react";
import { Plus, LoaderCircle } from "lucide-react";

export default function AttachmentButton({
  onUpload,
  isUploading = false,
}) {
  const fileInputRef = useRef(null);

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (file) {
      onUpload(file);
    }

    event.target.value = "";
  }

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        onChange={handleFileChange}
        className="hidden"
      />

      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
        title="Add PDF or image"
        aria-label="Add attachment"
        className="
          flex h-9 w-9 shrink-0 items-center
          justify-center rounded-full border
          border-[#e8e6dc] text-[#6b6a68]
          transition hover:bg-[#f0eee6]
          disabled:cursor-not-allowed
          disabled:opacity-50
          dark:border-[#454541]
          dark:text-[#b8b6ad]
          dark:hover:bg-[#3a3a37]
        "
      >
        {isUploading ? (
          <LoaderCircle size={19} className="animate-spin" />
        ) : (
          <Plus size={21} />
        )}
      </button>
    </>
  );
}