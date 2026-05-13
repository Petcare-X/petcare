import { z } from "zod";

export const UploadDocumentSchema = z.object({
    documentTypeId: z
        .number({error: "Выберите тип документа"})
        .int()
        .positive("Выберите тип документа"),

    customName: z
        .string()
        .trim()
        .max(255, "Название слишком длинное")
        .optional()
        .or(z.literal("")),
    
    file: z
        .instanceof(File, {
            error: "Выберите файл",
        })
        .refine((file) => file.size > 0, "Файл пустой")
        .refine(
            (file) => file.size < 1024 * 1024 * 10,
            "Файл должен быть не более 10 МБ",
        )
        .refine(
            (file) => [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/webp",
            ].includes(file.type),
            "Разрешены только PDF, JPEG, PNG, WEBP",
        ),
});

export type UploadDocumentFormValues = z.infer<typeof UploadDocumentSchema>;