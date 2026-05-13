import { QueryProvider } from "@/app/providers/query-provider";
import { RouterProvider } from "@/app/providers/router-provider";
import { AuthBootstrap } from "@/app/providers/auth-bootstrap";

export function Providers() {
    return (
        <QueryProvider>
            <AuthBootstrap>
                <RouterProvider />
            </AuthBootstrap>
        </QueryProvider>
    )
};