import { PetDocument } from "@/entities/document/model/document.types";
import { DocumentsListItem } from "./documents-list-item";

import "./documents-list.css";

type Props = {
    petId: number;
    documents: PetDocument[];
    onRequestDelete: (documentId: number) => void;
}

export function DocumentsList({ petId, documents, onRequestDelete }: Props) {
    if (documents.length === 0) {
        return (
            <div className="documents-list-placeholder">
                <div className="documents-list-placeholder-icon-conteiner">
                    <svg className="document-icon" viewBox="0 0 19 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11.6331 0.800049H2.96647C2.39184 0.800049 1.84074 1.02832 1.43441 1.43465C1.02808 1.84098 0.799805 2.39208 0.799805 2.96672V20.3C0.799805 20.8747 1.02808 21.4258 1.43441 21.8321C1.84074 22.2384 2.39184 22.4667 2.96647 22.4667H15.9665C16.5411 22.4667 17.0922 22.2384 17.4985 21.8321C17.9049 21.4258 18.1331 20.8747 18.1331 20.3V7.30005M11.6331 0.800049L18.1331 7.30005M11.6331 0.800049L11.6331 7.30005H18.1331M13.7998 12.7167H5.13314M13.7998 17.05H5.13314M7.2998 8.38338H5.13314" stroke="#FAFAFA" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div className="documents-list-text-conteiner">
                    <p className="documents-list-placeholder-title">
                        Документов ещё нет
                    </p>
                    <p className="documents-list-placeholder-text">
                        Давайте сохраним их, чтобы они всегда были под рукой.
                    </p>
                </div>
            </div>
        )
    }

    return (
        <ul className="documents-list">
            {documents.map((document) => (
                <DocumentsListItem 
                    key={document.id} 
                    petId={petId}
                    document={document}
                    onRequestDelete={onRequestDelete}
                />
            ))}
        </ul>
    )
}
