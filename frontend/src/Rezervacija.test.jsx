import { fireEvent, render, screen } from "@testing-library/react";
import Rezervacija from "./Rezervacija";

describe("Rezervacija", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("prikaze sporocilo, ce je ura izven delovnega casa", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    );

    render(<Rezervacija />);
    fireEvent.change(screen.getByLabelText("Datum"), { target: { value: "2026-12-01" } });

    const ura = screen.getByLabelText("Ura");
    const izven = document.createElement("option");
    izven.value = "07";
    ura.appendChild(izven);
    fireEvent.change(ura, { target: { value: "07" } });
    fireEvent.change(screen.getByLabelText("Minute"), { target: { value: "00" } });

    expect(await screen.findByText("Restavracija je odprta od 8. do 23. ure.")).toBeInTheDocument();
  });
});
