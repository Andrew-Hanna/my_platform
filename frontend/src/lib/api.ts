// Small helpers for calling the backend through the /api proxy.
// Changing requests first fetch a CSRF token and send it back in a header.

const FALLBACK_MESSAGE = "Something went wrong. Please try again.";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/auth/csrf", {
    credentials: "same-origin",
  });
  const body = (await response.json()) as { csrf_token: string };
  return body.csrf_token;
}

async function readError(response: Response): Promise<ApiError> {
  let message = FALLBACK_MESSAGE;
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      message = body.detail;
    }
  } catch {
    // The body was not JSON; keep the fallback message.
  }
  return new ApiError(response.status, message);
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const token = await getCsrfToken();
  const response = await fetch(`/api${path}`, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw await readError(response);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`, { credentials: "same-origin" });
  if (!response.ok) {
    throw await readError(response);
  }
  return (await response.json()) as T;
}
