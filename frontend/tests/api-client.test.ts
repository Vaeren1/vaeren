import { afterEach, beforeEach, describe, expect, mock, test } from "bun:test";
import { ApiError, _resetCsrfCacheForTests, api } from "@/lib/api/client";

interface FetchCall {
  url: string;
  init: RequestInit;
}

let calls: FetchCall[] = [];
const originalFetch = globalThis.fetch;

function makeFetch(responder: (url: string) => Response) {
  return mock(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString();
    calls.push({ url, init: init ?? {} });
    return responder(url);
  });
}

beforeEach(() => {
  calls = [];
  _resetCsrfCacheForTests();
});

afterEach(() => {
  globalThis.fetch = originalFetch;
});

describe("api()", () => {
  test("GET returns parsed JSON", async () => {
    globalThis.fetch = makeFetch((url) => {
      if (url === "/api/auth/user/") {
        return new Response(JSON.stringify({ pk: 1, email: "a@b.de" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        });
      }
      return new Response("not found", { status: 404 });
    }) as unknown as typeof fetch;

    const res = await api<{ pk: number; email: string }>("/api/auth/user/");
    expect(res.email).toBe("a@b.de");
    expect(calls).toHaveLength(1);
  });

  test("POST adds CSRF header from /api/auth/csrf/", async () => {
    globalThis.fetch = makeFetch((url) => {
      if (url === "/api/auth/csrf/") {
        return new Response(JSON.stringify({ csrf_token: "TOKEN-123" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        });
      }
      if (url === "/api/mitarbeiter/") {
        return new Response(JSON.stringify({ id: 5 }), {
          status: 201,
          headers: { "content-type": "application/json" },
        });
      }
      return new Response("not found", { status: 404 });
    }) as unknown as typeof fetch;

    const res = await api<{ id: number }>("/api/mitarbeiter/", {
      method: "POST",
      json: { vorname: "Anna" },
    });

    expect(res.id).toBe(5);
    expect(calls).toHaveLength(2);
    expect(calls[0]?.url).toBe("/api/auth/csrf/");
    expect(calls[1]?.url).toBe("/api/mitarbeiter/");
    const headers = new Headers(calls[1]?.init.headers);
    expect(headers.get("X-CSRFToken")).toBe("TOKEN-123");
    expect(headers.get("Content-Type")).toBe("application/json");
    expect(calls[1]?.init.body).toBe(JSON.stringify({ vorname: "Anna" }));
  });

  test("POST caches CSRF token for subsequent calls", async () => {
    let csrfCalls = 0;
    globalThis.fetch = makeFetch((url) => {
      if (url === "/api/auth/csrf/") {
        csrfCalls += 1;
        return new Response(JSON.stringify({ csrf_token: "T" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        });
      }
      return new Response("", { status: 204 });
    }) as unknown as typeof fetch;

    await api("/api/x/", { method: "POST", json: {} });
    await api("/api/y/", { method: "POST", json: {} });
    expect(csrfCalls).toBe(1);
  });

  test("non-2xx throws ApiError with parsed body", async () => {
    globalThis.fetch = makeFetch(
      () =>
        new Response(JSON.stringify({ detail: "denied" }), {
          status: 403,
          headers: { "content-type": "application/json" },
        }),
    ) as unknown as typeof fetch;

    let caught: unknown;
    try {
      await api("/api/x/");
    } catch (err) {
      caught = err;
    }
    expect(caught).toBeInstanceOf(ApiError);
    expect((caught as ApiError).status).toBe(403);
    expect((caught as ApiError).body).toEqual({ detail: "denied" });
  });

  test("204 returns undefined without body parse", async () => {
    globalThis.fetch = makeFetch((url) => {
      if (url === "/api/auth/csrf/") {
        return new Response(JSON.stringify({ csrf_token: "T" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        });
      }
      return new Response(null, { status: 204 });
    }) as unknown as typeof fetch;

    const res = await api("/api/auth/logout/", { method: "POST" });
    expect(res).toBeUndefined();
  });
});
