import { QueryProvider } from "@/app/providers/query-provider";
import { RouterProvider } from "@/app/providers/router-provider";

export function Providers() {
    return (
        <QueryProvider>
            <RouterProvider />
        </QueryProvider>
    )
};