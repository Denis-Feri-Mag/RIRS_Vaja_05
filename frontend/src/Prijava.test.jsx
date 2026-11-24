import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Prijava from "./Prijava";

describe("Prijava", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("prikaze obrazec in ob uspesni prijavi shrani sejo", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ token: "abc", vloga: "gost", ime: "Ema", priimek: "Novak" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    const uporabnik = userEvent.setup();

    render(<Prijava />);
    expect(screen.getByRole("heading", { name: /prijava/i })).toBeInTheDocument();
    await uporabnik.type(screen.getByLabelText("Email"), "ema@test.com");
    await uporabnik.type(screen.getByLabelText("Geslo"), "skrivnost");
    await uporabnik.click(screen.getByRole("button", { name: "Prijavi se" }));

    await vi.waitFor(() => {
      expect(localStorage.getItem("token")).toBe("abc");
    });
    expect(fetchMock).toHaveBeenCalled();
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/login");
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({ email: "ema@test.com", geslo: "skrivnost" });
    expect(localStorage.getItem("token")).toBe("abc");
    expect(localStorage.getItem("vloga")).toBe("gost");
  });
});
