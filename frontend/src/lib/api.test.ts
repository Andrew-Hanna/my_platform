import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiGet, apiPost, getCsrfToken } from "./api";

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function noContentResponse(): Response {
  return new Response(null, { status: 204 });
}

function csrfResponse(token = "test-csrf-token"): Response {
  return jsonResponse({ csrf_token: token });
}

// Stubs global fetch with a vi.fn() that resolves the given responses in order.
function mockFetch(...responses: Response[]) {
  const fetchMock = vi.fn();
  for (const response of responses) {
    fetchMock.mockResolvedValueOnce(response);
  }
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("getCsrfToken", () => {
  it("returns the csrf_token value from the response body and calls /api/auth/csrf", async () => {
    const fetchMock = mockFetch(csrfResponse("abc123"));

    const token = await getCsrfToken();

    expect(token).toBe("abc123");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/csrf", {
      credentials: "same-origin",
    });
  });
});

describe("apiPost", () => {
  it("sends the X-CSRF-Token header from /api/auth/csrf, sends JSON, and uses method POST", async () => {
    const fetchMock = mockFetch(
      csrfResponse("tok-42"),
      jsonResponse({ ok: true }),
    );
    const body = { email: "user@example.com", password: "secret" };

    await apiPost("/auth/login", body);

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0]).toEqual([
      "/api/auth/csrf",
      { credentials: "same-origin" },
    ]);
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/api/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": "tok-42",
      },
      body: JSON.stringify(body),
    });
  });

  it("returns undefined for a 204 response", async () => {
    mockFetch(csrfResponse(), noContentResponse());

    const result = await apiPost("/auth/logout");

    expect(result).toBeUndefined();
  });

  it("returns the parsed JSON for a 200 response", async () => {
    mockFetch(csrfResponse(), jsonResponse({ id: 7, email: "a@b.co" }, 200));

    const result = await apiPost<{ id: number; email: string }>("/users", {
      email: "a@b.co",
    });

    expect(result).toEqual({ id: 7, email: "a@b.co" });
  });

  it("throws an ApiError with status 401 and the server detail message for a 401 response", async () => {
    mockFetch(
      csrfResponse(),
      jsonResponse({ detail: "Email or password is incorrect" }, 401),
    );

    const promise = apiPost("/auth/login", { email: "a@b.co", password: "x" });

    await expect(promise).rejects.toBeInstanceOf(ApiError);
    await expect(promise).rejects.toMatchObject({
      status: 401,
      message: "Email or password is incorrect",
    });
  });

  it("throws an ApiError with the fallback message when the error body has no detail field", async () => {
    mockFetch(csrfResponse(), jsonResponse({ error: "boom" }, 500));

    const promise = apiPost("/users", { email: "a@b.co" });

    await expect(promise).rejects.toBeInstanceOf(ApiError);
    await expect(promise).rejects.toMatchObject({
      status: 500,
      message: "Something went wrong. Please try again.",
    });
  });
});

describe("apiGet", () => {
  it("calls /api/auth/me and returns the user JSON on 200", async () => {
    const user = { id: 1, email: "a@b.co", role: "learner" };
    const fetchMock = mockFetch(jsonResponse(user, 200));

    const result = await apiGet<typeof user>("/auth/me");

    expect(result).toEqual(user);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/me", {
      credentials: "same-origin",
    });
  });

  it("throws an ApiError with status 401 on a 401 response", async () => {
    mockFetch(jsonResponse({ detail: "Not authenticated" }, 401));

    const promise = apiGet("/auth/me");

    await expect(promise).rejects.toBeInstanceOf(ApiError);
    await expect(promise).rejects.toMatchObject({ status: 401 });
  });
});

describe("ApiError", () => {
  it("is an instance of Error and carries the status", () => {
    const error = new ApiError(403, "Forbidden here");

    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(403);
    expect(error.message).toBe("Forbidden here");
  });
});
