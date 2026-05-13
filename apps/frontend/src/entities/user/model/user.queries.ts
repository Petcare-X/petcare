import { useQuery } from "@tanstack/react-query"

import { getUser } from "../api/user.api"

export function useUserQueries() {
    return useQuery({
        queryKey: ["user"],
        queryFn: getUser,
        staleTime: 60_000,
    })
}