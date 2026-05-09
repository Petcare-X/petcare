import { apiClient } from "@/shared/api/client";
import type { CreateInvitePayload, Invite } from "@/entities/invite/model/invite.types";

export async function createInvite(payload: CreateInvitePayload): Promise<Invite> {
    const response = await apiClient.post<Invite>("/invites", payload);
    return response.data;
}

export async function acceptInvite(inviteCode: string): Promise<void> {
    await apiClient.post("/invites/accept", {
        invite_code: inviteCode,
    });
}