function decodeToken(token) {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(payload);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

export function getRole() {
  const claims = decodeToken(localStorage.getItem('access'));
  return claims?.role || null;
}

export function getUsername() {
  const claims = decodeToken(localStorage.getItem('access'));
  return claims?.username || null;
}

export function isAuthenticated() {
  return !!localStorage.getItem('access');
}
