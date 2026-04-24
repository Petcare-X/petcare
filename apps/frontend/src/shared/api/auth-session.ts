let accessToken: string | null = null;

export function getAccessToken() {
    return accessToken;
};

export function setAuthSession(tokens: {access_token: string; refresh_token: string;}) {
    accessToken = tokens.access_token;
    sessionStorage.setItem("refresh_token", tokens.refresh_token);
};

export function clearAuthSession() {
    accessToken = null;
    sessionStorage.removeItem("refresh_token");
};