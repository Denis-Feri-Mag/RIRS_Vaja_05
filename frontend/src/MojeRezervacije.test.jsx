import { render, screen, within } from "@testing-library/react";
import MojeRezervacije from "./MojeRezervacije";

const REZERVACIJE = [
  {
    id: 1,
    stevilka_mize: 1,
    zacetek: "2026-12-01T10:00:00+00:00",
    stevilo_oseb: 2,
    opomba: "",
    status: "gost_prisel",
  },
  {
    id: 2,
    stevilka_mize: 2,
    zacetek: "2026-12-02T18:00:00+00:00",
    stevilo_oseb: 3,
    opomba: "",
    status: "potrjena",
  },
];

describe("MojeRezervacije", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("pri prispelem gostu skrije odpoved", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => REZERVACIJE,
      }),
    );

    render(<MojeRezervacije />);

    const prisel = (await screen.findByText(/gost je prišel/)).closest("article");
    expect(within(prisel).queryByRole("button", { name: "Odpovej" })).not.toBeInTheDocument();

    const potrjena = screen.getByText(/· potrjena/).closest("article");
    expect(within(potrjena).getByRole("button", { name: "Odpovej" })).toBeInTheDocument();
  });
});
