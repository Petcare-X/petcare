import { FormEvent, useState } from "react";
import { useLogin } from "@/features/auth/model/use-login";

export function LoginPage() {
    const login = useLogin();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        login.mutate({
            email,
            password,
        });
    };

    return (
        <div>
            <h1>Войти</h1>
            <form onSubmit={handleSubmit}>
                <input 
                    type="email" 
                    value={email} 
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="Email"
                    required
                />
                <input 
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Password"
                    required
                />
                <button type="submit">Войти</button>
            </form>
        </div>
    )
}