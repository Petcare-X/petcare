import { z } from "zod";

export const signupSchema = z.object({
    name: z
        .string()
        .trim()
        .min(2, "Имя должно содержать минимум 2 символа")
        .max(50, "Имя должно содержать не более 50 символов"),

    email: z.email("Введите корректный email"),
    
    birth_date: z.string().refine((value) => {
        const date = new Date(value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return !Number.isNaN(date.getTime()) && date <= today;
    }, "Введите корректную дату рождения"),
    
    password: z
        .string()
        .min(8, "Пароль должен содержать минимум 8 символов")
        .regex(/[a-z, A-Z]/, "Пароль должен содержать латинские символы (a-z)")
        .regex(/[A-Z]/, "Пароль должен содержать хотя бы одну заглавную букву")
        .regex(/[a-z]/, "Пароль должен содержать хотя бы одну строчную букву")
        .regex(/[0-9]/, "Пароль должен содержать хотя бы одну цифру")
        .regex(/[@$!%*?&]/, "Пароль должен содержать хотя бы один специальный символ"),
});

export type SignupFormValues = z.infer<typeof signupSchema>;