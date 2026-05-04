import { Link } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { appRoutes } from "@/shared/constants/routes";
import { UseSignup } from "@/features/auth/model/use-signup";
import { signupSchema, type SignupFormValues } from "@/features/auth/model/signup.schema";

export function SignupForm() {
    const signupMutation = UseSignup();

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setError,
    } = useForm<SignupFormValues>({
        resolver: zodResolver(signupSchema),
        defaultValues: {
            name: "",
            email: "",
            birth_date: "",
            password: "",
        },
        mode: "onBlur",
    });
        const onSubmit = async (value: SignupFormValues) => {
            try {
                await signupMutation.mutateAsync(value);
            } catch (error) {
                setError("root", {
                    message: "Произошла ошибка при регистрации. Попробуйте снова.",
                });
            }
        };


    return (
        <form className="auth-form" onSubmit={handleSubmit(onSubmit)}>
            <div className="auth-top">
                <svg className="auth-logo" viewBox="0 0 70 71" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14.1256 42.9278C10.0725 43.398 6.32058 39.7592 5.74636 34.8015C5.00017 28.3652 7.59955 22.0661 11.6532 21.5967C15.7063 21.1266 19.7321 27.132 20.4241 33.1002C20.9983 38.0579 18.1795 42.4578 14.1256 42.9278Z" fill="#FAFAFA"/>
                    <path d="M45.8743 64.1326C40.104 63.971 37.9201 61.3843 34.2197 61.2799C30.5184 61.1762 28.1936 63.6364 22.4235 63.4742C14.8698 63.2614 9.52824 53.7269 16.5522 47.7191C25.2812 40.2541 27.9757 30.6318 35.0746 30.8315C42.1743 31.0314 44.3242 40.789 52.6204 48.7328C59.2958 55.1253 53.4273 64.3452 45.8743 64.1326Z" fill="#FAFAFA"/>
                    <path d="M37.2785 18.3223C37.959 12.3534 41.9741 6.34032 46.0275 6.80198C50.0822 7.26464 52.6933 13.5585 51.9593 19.9958C51.3939 24.9551 47.6493 28.6006 43.5954 28.1381C39.5412 27.6763 36.7131 23.2815 37.2785 18.3223Z" fill="#FAFAFA"/>
                    <path d="M18.8245 19.0646C18.4536 12.5965 21.414 6.45865 25.4879 6.22553C29.5612 5.99154 33.2322 12.2205 33.5762 18.2182C33.8625 23.2013 30.7922 27.43 26.7189 27.6639C22.6448 27.8979 19.1108 24.0478 18.8245 19.0646Z" fill="#FAFAFA"/>
                    <path d="M55.312 44.0849C51.2913 43.3883 48.7232 38.8365 49.5749 33.9186C50.6008 27.9995 54.9584 22.2295 58.9782 22.9267C62.999 23.6233 65.2409 30.0579 64.1346 36.4416C63.2823 41.3594 59.332 44.7813 55.312 44.0849Z" fill="#FAFAFA"/>
                </svg>
                <h1 className="auth-title">Регистрация</h1>
            </div>

            <div className="auth-inputs-conteiner">
                <label htmlFor="name">ИМЯ</label>
                <input
                    id="name"
                    className="auth-input" 
                    type="text"
                    {...register("name")}
                    placeholder="Пользователь"
                    autoComplete="name"
                    required
                />
                {errors.name && <p className="signup-input-error">{errors.name.message}</p>}

                <label htmlFor="email">ПОЧТА</label>
                <input
                    id="email"
                    className="auth-input" 
                    type="email"
                    {...register("email")}
                    placeholder="user@example.com"
                    autoComplete="email"
                    required
                />
                {errors.email && <p className="signup-input-error">{errors.email.message}</p>}
                
                <label htmlFor="birth_date">ДАТА РОЖДЕНИЯ</label>
                <input
                    id="birth_date"
                    className="auth-input" 
                    type="date"
                    {...register("birth_date")}
                    required
                />
                {errors.birth_date && <p className="signup-input-error">{errors.birth_date.message}</p>}
                
                <label htmlFor="password">ПАРОЛЬ</label>
                <input
                    id="password"
                    className="auth-input" 
                    type="password" 
                    placeholder="●●●●●●●●"
                    {...register("password")}
                    required
                />
                {errors.password && <p className="signup-input-error">{errors.password.message}</p>}
            </div>

            <div>
                <button className="auth-button" type="submit" disabled={isSubmitting || signupMutation.isPending}>
                    {isSubmitting || signupMutation.isPending ? "Регистрируем..." : "Зарегистрироваться"}
                </button>
                <p className="login-register">
                    Уже есть аккаунт? <Link to={appRoutes.login}>Войти</Link>
                </p>
            </div>
        </form>
    )
}