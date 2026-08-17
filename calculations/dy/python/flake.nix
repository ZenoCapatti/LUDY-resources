{
  description = "Portable runtime for the Drell-Yan Kira notebook";

  inputs.ludy-kira.url = "path:../../../packages/ludy-kira";

  outputs =
    { ludy-kira, ... }:
    {
      devShells = ludy-kira.devShells;
      formatter = ludy-kira.formatter;
    };
}
