import { api } from "./api";

describe("api", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("doda predpono VITE_API_URL", async () => {
    vi.stubEnv("VITE_API_URL", "https://rirs-vaja-05.fly.dev");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await api("/api/jedilnik");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url] = fetchMock.mock.calls[0];
    expect(url).toBe("https://rirs-vaja-05.fly.dev/api/jedilnik");
  });

  it("ob zetunu doda Authorization glavo", async () => {
    localStorage.setItem("token", "skrivni-zeton");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 1 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await api("/api/rezervacije", { method: "GET" });

    const [, options] = fetchMock.mock.calls[0];
    expect(options.headers.Authorization).toBe("Bearer skrivni-zeton");
  });
});
