import { useQuery } from "@tanstack/react-query";
import { getSharedUsers } from "../api/shared-users.api";

export const sharedUsersQueryKey = {
    all: ["shared-users"] as const,
    byPet: (petId: number) => [...sharedUsersQueryKey.all, petId] as const,
}

export function useSharedUsersQuery(petId: number, enabled: boolean) {
    return useQuery({
        queryKey: sharedUsersQueryKey.byPet(petId),
        queryFn: () => getSharedUsers(petId),
        enabled,
        staleTime: 60_000,
    })
}