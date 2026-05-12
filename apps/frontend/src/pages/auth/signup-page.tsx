import { SignupForm } from "@/features/auth/ui/signup-form";
import "./auth-page.css"

export function SignupPage() {
    return (
        <main className="auth-page page-transition">
            <SignupForm />
        </main>
    );
}