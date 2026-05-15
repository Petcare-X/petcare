import { useState, useRef } from "react";
import { PetDocument } from "@/entities/document/model/document.types"

import "./documents-list-item.css";
import { getPetDocumentDownloadUrl } from "@/entities/document/api/document.api";

type Props = {
    petId: number;
    document: PetDocument;
    onRequestDelete: (documentId: number) => void;
}

export function DocumentsListItem({ petId, document, onRequestDelete }: Props) {
    const [isDownloading, setIsDownloading] = useState(false);

    const uploadedAtLabel = document.uploaded_at
        ? new Date(document.uploaded_at).toLocaleDateString("ru-RU", {
            day: "2-digit",
            month: "long",
            year: "numeric",
        })
        : "Дата не указана";

    async function handleDownload() {
        try {
            setIsDownloading(true);

            const response = await getPetDocumentDownloadUrl(petId, document.id);
            const fileResponse = await fetch(response.download_url);
            
            if (!fileResponse.ok) {
                throw new Error("Failed to download file");
            }
        
            const blob = await fileResponse.blob();
            const objectUrl = window.URL.createObjectURL(blob);
        
            const link = window.document.createElement("a");
            link.href = objectUrl;
            link.download = document.custom_name;
            window.document.body.appendChild(link);
            link.click();
            link.remove();
        
            window.URL.revokeObjectURL(objectUrl);
        } catch {
            console.error("Не удалось получить ссылку на скачивание документа")
        } finally {
            setIsDownloading(false);
        }
    }

    const longPressTimeoutRef = useRef<number | null>(null);

    const startLongPress = () => {
        longPressTimeoutRef.current = window.setTimeout(() => {
            onRequestDelete(document.id);
        }, 500);
    }

    const clearLongPress = () => {
        if (longPressTimeoutRef.current !== null) {
            window.clearTimeout(longPressTimeoutRef.current);
            longPressTimeoutRef.current = null;
        }
    }

    return (
        <li className="documents-list-item">
            <div className="documents-list-item-icon-conteiner">
                <svg className="document-icon" viewBox="0 0 19 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11.6331 0.800049H2.96647C2.39184 0.800049 1.84074 1.02832 1.43441 1.43465C1.02808 1.84098 0.799805 2.39208 0.799805 2.96672V20.3C0.799805 20.8747 1.02808 21.4258 1.43441 21.8321C1.84074 22.2384 2.39184 22.4667 2.96647 22.4667H15.9665C16.5411 22.4667 17.0922 22.2384 17.4985 21.8321C17.9049 21.4258 18.1331 20.8747 18.1331 20.3V7.30005M11.6331 0.800049L18.1331 7.30005M11.6331 0.800049L11.6331 7.30005H18.1331M13.7998 12.7167H5.13314M13.7998 17.05H5.13314M7.2998 8.38338H5.13314" stroke="#FAFAFA" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
            </div>

            <div 
                className="documents-list-item-content"
                onPointerDown={startLongPress}
                onPointerUp={clearLongPress}
                onPointerLeave={clearLongPress}
                onPointerCancel={clearLongPress}
            >
                <p className="documents-list-item-title">{document.custom_name}</p>
                <p className="documents-list-item-subtitle">
                    {document.document_type_name ?? "Документ"}
                </p>
                <p className="documents-list-item-meta">{uploadedAtLabel}</p>
            </div>

            <button
                type="button"
                className="documents-list-item-download"
                onClick={handleDownload}
                disabled={isDownloading}
                aria-label={`Скачать документ ${document.custom_name}`}
            >
                <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 17H18V19H0V17ZM10 11.1716L16.0711 5.1005L17.4853 6.51472L9 15L0.51472 6.51472L1.92893 5.1005L8 11.1716V0H10V11.1716Z" fill="#FAFAFA"/>
                </svg>
            </button>
        </li>
    )
}
