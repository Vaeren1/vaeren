import { beforeEach, describe, expect, test } from "bun:test";
import { useAuthStore } from "@/lib/stores/auth-store";

beforeEach(() => {
  useAuthStore.getState().clear();
});

describe("auth-store", () => {
  test("initial state is empty", () => {
    const s = useAuthStore.getState();
    expect(s.user).toBeNull();
    expect(s.ephemeralToken).toBeNull();
  });

  test("setUser populates user and clears ephemeral token", () => {
    useAuthStore.getState().setMfaChallenge("EPH");
    useAuthStore
      .getState()
      .setUser({ pk: 1, email: "konrad@vaeren.de", tenant_role: "geschaeftsfuehrer" });
    const s = useAuthStore.getState();
    expect(s.user?.email).toBe("konrad@vaeren.de");
    expect(s.ephemeralToken).toBeNull();
  });

  test("setMfaChallenge sets token and clears user", () => {
    useAuthStore.getState().setUser({ pk: 1, email: "x@y.de" });
    useAuthStore.getState().setMfaChallenge("EPH-TOKEN");
    const s = useAuthStore.getState();
    expect(s.ephemeralToken).toBe("EPH-TOKEN");
    expect(s.user).toBeNull();
  });

  test("clear resets everything", () => {
    useAuthStore.getState().setUser({ pk: 1, email: "x@y.de" });
    useAuthStore.getState().clear();
    const s = useAuthStore.getState();
    expect(s.user).toBeNull();
    expect(s.ephemeralToken).toBeNull();
  });
});
