import { z } from "zod";

export const loginSchema = z.object({
    email: z.email("Введите корректный email"),
    password: z.string().min(8, "Введите корректный пароль")
});

export type LoginFormValues = z.infer<typeof loginSchema>;