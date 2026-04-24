import { PropsWithChildren, useEffect, useState } from "react";

import { refreshSession } from "@/entities/auth/api/auth.api";
import {
    getAuthStatus,
    hasLoggedOutMarker,
    setAuthSession,
    setAuthStatus,
} from "@/shared/api/auth-session";

export function AuthBootstrap({ children }: PropsWithChildren) {
    const [isReady, setIsReady] = useState(getAuthStatus() !== "unknown");

    useEffect(() => {
        let cancelled = false;

        async function bootstrap() {
            if (hasLoggedOutMarker()) {
                setAuthStatus("guest");
                if (!cancelled) {
                    setIsReady(true);
                }
                return;
            }

            try {
                const session = await refreshSession();
                setAuthSession(session);
            } catch {
                setAuthStatus("guest");
            } finally {
                if (!cancelled) {
                    setIsReady(true);
                }
            }
        }

        if (getAuthStatus() === "unknown") {
            void bootstrap();
        } else {
            setIsReady(true);
        }

        return () => {
            cancelled = true;
        };
    }, []);

    if (!isReady) {
        return null;
    }

    return children;
}
