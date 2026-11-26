import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Natakar from "./Natakar";

function odgovor(telo) {
  return {
    ok: true,
    status: 200,
    json: async () => telo,
  };
}

function pripraviFetch(rezervacije) {
  return vi.fn(async (url, options) => {
    const pot = String(url);
    if (pot.includes("/api/rezervacije/") && options?.method === "POST") {
      return odgovor({ status: "gost_prisel" });
    }
    if (pot.includes("/api/rezervacije/dan")) return odgovor(rezervacije);
    if (pot.includes("/api/narocila/mize")) return odgovor([]);
    if (pot.includes("/api/narocila/jedilnik")) return odgovor([]);
    if (pot.includes("/api/zaloge/")) return odgovor([]);
    return odgovor([]);
  });
}

describe("Natakar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("pri potrjeni rezervaciji oznaci prihod", async () => {
    const fetchMock = pripraviFetch([
      {
        id: 7,
        ura: "10:00",
        stevilka_mize: 1,
        ime: "Ana",
        priimek: "Gost",
        opomba: "",
        status: "potrjena",
      },
    ]);
    vi.stubGlobal("fetch", fetchMock);
    const uporabnik = userEvent.setup();

    render(<Natakar />);

    expect(await screen.findByRole("button", { name: "Prihod" })).toBeInTheDocument();
    expect(screen.getByText("potrjena")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Zaključi" })).toBeInTheDocument();

    await uporabnik.click(screen.getByRole("button", { name: "Prihod" }));

    await vi.waitFor(() => {
      const klic = fetchMock.mock.calls.find(
        ([url, options]) => String(url).includes("/api/rezervacije/7/prihod") && options?.method === "POST",
      );
      expect(klic).toBeTruthy();
    });
  });

  it("pri prispelem gostu skrije prihod in obdrzi zakljucek", async () => {
    vi.stubGlobal(
      "fetch",
      pripraviFetch([
        {
          id: 8,
          ura: "12:00",
          stevilka_mize: 2,
          ime: "Ana",
          priimek: "Gost",
          opomba: "",
          status: "gost_prisel",
        },
      ]),
    );

    render(<Natakar />);

    expect(await screen.findByText("gost je prišel")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Zaključi" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Prihod" })).not.toBeInTheDocument();
  });
});
