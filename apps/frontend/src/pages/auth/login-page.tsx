import { LoginForm } from "@/features/auth/ui/login-form"; 

import "./auth-page.css";

export function LoginPage() {
    return (
        <main className="auth-page page-transition">
            <LoginForm />
        </main>
    )
}