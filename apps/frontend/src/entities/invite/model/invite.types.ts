export type CreateInvitePayload = {
    pet_id: number;
    max_uses?: number | null;
    expires_at?: string | null;
};

export type Invite = {
    invite_code: string;
    invite_url: string | null;
};
