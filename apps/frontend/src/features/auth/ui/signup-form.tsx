import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { appRoutes } from "@/shared/constants/routes";
import { UseSignup } from "@/features/auth/model/use-signup";
import { signupSchema, type SignupFormValues } from "@/features/auth/model/signup.schema";

export function SignupForm() {
    const signupMutation = UseSignup();
    const [isPasswordVisible, setIsPasswordVisible] = useState(false);

    const {
        register,
        handleSubmit,
        watch,
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
    const passwordValue = watch("password");
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
                <div className="auth-password-field">
                    <input
                        id="password"
                        className="auth-input auth-password-input"
                        type={isPasswordVisible ? "text" : "password"}
                        placeholder="●●●●●●●●"
                        {...register("password")}
                        autoComplete="new-password"
                        required
                    />
                    <button
                        className="auth-password-toggle"
                        type="button"
                        onClick={() => setIsPasswordVisible((value) => !value)}
                        aria-label={isPasswordVisible ? "Скрыть пароль" : "Показать пароль"}
                        aria-pressed={isPasswordVisible}
                    >
                        {isPasswordVisible ? <PasswordVisibleIcon /> : <PasswordHiddenIcon />}
                    </button>
                </div>
                {passwordValue && errors.password ? (
                    <p className="signup-input-error">{errors.password.message}</p>
                ) : null}
                <p
                    className={
                        !passwordValue
                            ? "signup-password-hint is-visible"
                            : "signup-password-hint"
                    }
                    aria-hidden={passwordValue ? "true" : "false"}
                >
                    Ваш пароль должен содержать минимум 8 символов, одну заглавную букву (A-Z), один специальный символ (%!?#_)
                </p>
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

function PasswordVisibleIcon() {
    return (
        <svg width="22" height="18" viewBox="0 0 22 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M10.8187 0C16.2108 0 20.6968 3.87976 21.6373 9C20.6968 14.1202 16.2108 18 10.8187 18C5.42648 18 0.94051 14.1202 0 9C0.94051 3.87976 5.42648 0 10.8187 0ZM10.8187 16C15.0543 16 18.6787 13.052 19.5961 9C18.6787 4.94803 15.0543 2 10.8187 2C6.58296 2 2.95858 4.94803 2.04114 9C2.95858 13.052 6.58296 16 10.8187 16ZM10.8187 13.5C8.33334 13.5 6.31862 11.4853 6.31862 9C6.31862 6.51472 8.33334 4.5 10.8187 4.5C13.3039 4.5 15.3187 6.51472 15.3187 9C15.3187 11.4853 13.3039 13.5 10.8187 13.5ZM10.8187 11.5C12.1994 11.5 13.3187 10.3807 13.3187 9C13.3187 7.6193 12.1994 6.5 10.8187 6.5C9.43796 6.5 8.31862 7.6193 8.31862 9C8.31862 10.3807 9.43796 11.5 10.8187 11.5Z" fill="#313131" fillOpacity="0.55"/>
        </svg>
    );
}

function PasswordHiddenIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M16.7011 17.9032C14.9998 18.9819 12.9822 19.6066 10.8187 19.6066C5.42648 19.6066 0.94051 15.7269 0 10.6067C0.43668 8.22927 1.63768 6.11935 3.33883 4.54102L0.21202 1.41422L1.62624 0L21.4253 19.7989L20.0111 21.2132L16.7011 17.9032ZM4.75396 5.95615C3.42509 7.1666 2.45616 8.77365 2.04114 10.6067C2.95858 14.6586 6.58296 17.6066 10.8187 17.6066C12.4181 17.6066 13.9304 17.1862 15.2427 16.4448L13.2144 14.4165C12.5207 14.8537 11.6992 15.1067 10.8187 15.1067C8.33334 15.1067 6.31862 13.0919 6.31862 10.6067C6.31862 9.72605 6.57153 8.90455 7.00867 8.21087L4.75396 5.95615ZM11.7323 12.9345L8.49082 9.69305C8.37966 9.97605 8.31862 10.2842 8.31862 10.6067C8.31862 11.9874 9.43796 13.1067 10.8187 13.1067C11.1411 13.1067 11.4493 13.0456 11.7323 12.9345ZM19.6252 15.199L18.1944 13.7682C18.8503 12.8333 19.3338 11.7651 19.5961 10.6067C18.6787 6.55463 15.0543 3.60661 10.8187 3.60661C9.97276 3.60661 9.15126 3.72418 8.37085 3.94463L6.79282 2.3666C8.03963 1.87604 9.39766 1.60661 10.8187 1.60661C16.2108 1.60661 20.6968 5.48637 21.6373 10.6067C21.3251 12.3063 20.6222 13.8693 19.6252 15.199ZM10.5413 6.11502C10.633 6.10944 10.7255 6.10661 10.8187 6.10661C13.3039 6.10661 15.3187 8.12133 15.3187 10.6067C15.3187 10.6997 15.3158 10.7923 15.3103 10.884L10.5413 6.11502Z" fill="#313131" fillOpacity="0.55"/>
        </svg>
    );
}
