import { useDocumentQueries } from "@/entities/document/model/document.queries";

export function DocumentListItem() {
    return (
        <ul>
            <li>
                {document.name}
            </li>
        </ul>
    )
}