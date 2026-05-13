import { FormEvent, useState } from "react";
import { useDocumentTypesQuery } from "@/entities/document/model/document.queries";
import { useUploadDocument } from "../model/use-upload-document";
import { UploadDocumentFormValues, UploadDocumentSchema } from "../model/upload-document.schema";



type UploadDocumentFormProps = {
    petId: number;
    onUploaded?: () => void;
    onCancel?: () => void;
}

export function UploadDocumentForm({ petId, onUploaded, onCancel }: UploadDocumentFormProps) {
    const documentTypesQuery = useDocumentTypesQuery();
    const uploadDocument = useUploadDocument();

    const [documentTypeId, setDocumentTypeId] = useState("");
    const [customName, setCustomName] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [formErrors, setFormErrors] = useState<String | null>(null);

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setFormErrors(null);

        if (!file) {
            setFormErrors("Please select a file to upload.");
            return;
        }

        const parsed = UploadDocumentSchema.safeParse({
            documentTypeId: Number(documentTypeId),
            customName,
            file,
        });

        if (!parsed.success) {
            setFormErrors(parsed.error.issues[0]?.message ?? "Проверьте форму");
            return;
        }

        const values: UploadDocumentFormValues = parsed.data;

        uploadDocument.mutate(
            {
                petId,
                file: values.file,
                documentTypeId: values.documentTypeId,
                customName: values.customName,
            },
            {
                onSuccess: () => {
                    setDocumentTypeId("");
                    setCustomName("");
                    setFile(null);
                    onUploaded?.();
                },
                onError: (error) => {
                    setFormErrors("Не удалось загрузить файл");
                },
            },
        );
    }

    return (
        <form className="upload-document-form" onSubmit={handleSubmit}>
            <div className="upload-document-form-heading">
                <p className="upload-document-form-title">Добавить документ</p>
                <p className="upload-document-form-subtitle">
                    Сохраните важный файл питомца, чтобы он всегда был под рукой.
                </p>
            </div>

            <label className="upload-document-field">
                <span>Тип документа</span>
                <select
                    className="upload-document-input"
                    value={documentTypeId}
                    onChange={(event) => setDocumentTypeId(event.target.value)}
                    disabled={documentTypesQuery.isLoading || uploadDocument.isPending}
                    required
                >
                    <option value="">Выберите тип документа</option>
                    {documentTypesQuery.data?.map((item) => (
                        <option key={item.id} value={item.id}>
                            {item.document_name}
                        </option>
                    ))}
                </select>
            </label>

            <label className="upload-document-field">
                <span>Имя файла</span>
                <input
                    className="upload-document-input"
                    type="text"
                    value={customName}
                    onChange={(event) => setCustomName(event.target.value)}
                    maxLength={255}
                    placeholder="Паспорт Барни"
                    disabled={uploadDocument.isPending}
                    required
                />
            </label>

            <label className="upload-document-field">
                <span>Файл</span>
                <input
                    className="upload-document-file-input"
                    type="file"
                    accept=".pdf,image/png,image/jpeg,image/webp"
                    onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                    disabled={uploadDocument.isPending}
                    required
                />
            </label>

            {file ? (
                <div className="upload-document-file-meta">
                    <span className="upload-document-file-name">{file.name}</span>
                    <span className="upload-document-file-size">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                </div>
            ) : null}

            {formErrors ? <p className="upload-document-error">{formErrors}</p> : null}

            {uploadDocument.isSuccess ? (
                <p className="upload-document-success">Файл успешно загружен</p>
            ) : null}

            <div className="upload-document-actions">
                {onCancel ? (
                    <button 
                        className="upload-document-button upload-document-button-secondary"
                        type="button" 
                        onClick={onCancel} 
                        disabled={uploadDocument.isPending}
                    >
                        Отмена
                    </button>
                ) : null}

                <button
                    className="upload-document-button upload-document-button-primary"
                    type="submit"
                    disabled={uploadDocument.isPending}
                >
                    {uploadDocument.isPending ? "Загрузка..." : "Загрузить"}
                </button>
            </div>
        </form>
    );
}
