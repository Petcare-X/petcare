export type AuthStatus = "unknown" | "authenticated" | "guest";

let accessToken: string | null = null;
let authStatus: AuthStatus = "unknown";

const LOGOUT_MARKER_KEY = "petcare_logged_out";

export function getAccessToken() {
    return accessToken;
}

export function getAuthStatus() {
    return authStatus;
}

export function setAuthSession(tokens: { access_token: string }) {
    accessToken = tokens.access_token;
    authStatus = "authenticated";
    clearLoggedOutMarker();
}

export function setAuthStatus(status: AuthStatus) {
    authStatus = status;
}

export function clearAuthSession() {
    accessToken = null;
    authStatus = "guest";
}

export function resetAuthState() {
    accessToken = null;
    authStatus = "unknown";
}

export function setLoggedOutMarker() {
    sessionStorage.setItem(LOGOUT_MARKER_KEY, "1");
}

export function hasLoggedOutMarker() {
    return sessionStorage.getItem(LOGOUT_MARKER_KEY) === "1";
}

export function clearLoggedOutMarker() {
    sessionStorage.removeItem(LOGOUT_MARKER_KEY);
}