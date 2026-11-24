import { odjavi, shraniSejo } from "./seja";

describe("seja", () => {
  it("shrani zeton in vlogo ter sporoci spremembo", () => {
    const sporocilo = vi.fn();
    window.addEventListener("glass-seja", sporocilo);
    shraniSejo({ token: "abc", vloga: "gost" });
    expect(localStorage.getItem("token")).toBe("abc");
    expect(localStorage.getItem("vloga")).toBe("gost");
    expect(sporocilo).toHaveBeenCalledTimes(1);
    window.removeEventListener("glass-seja", sporocilo);
  });

  it("ob odjavi pobrise sejo in hash", () => {
    localStorage.setItem("token", "abc");
    localStorage.setItem("vloga", "gost");
    window.location.hash = "#moje";
    odjavi();
    expect(localStorage.getItem("token")).toBeNull();
    expect(localStorage.getItem("vloga")).toBeNull();
    expect(window.location.hash).toBe("");
  });
});
