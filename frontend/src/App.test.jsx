import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("gosta z napačnim naslovom preusmeri na rezervacijo", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    );
    localStorage.setItem("token", "abc");
    localStorage.setItem("vloga", "gost");
    window.location.hash = "#natakar";

    render(<App />);

    expect(await screen.findByRole("heading", { name: /rezervacija mize/i })).toBeInTheDocument();
    expect(screen.queryByText("Natakar")).not.toBeInTheDocument();
    await waitFor(() => {
      expect(window.location.hash).toBe("#rezervacija");
    });
  });
});
