{
  description = "Portable runtime for the Drell-Yan Kira notebook";

  inputs.kirapy.url = "path:../../../packages/kirapy";

  outputs =
    { kirapy, ... }:
    {
      devShells = kirapy.devShells;
      formatter = kirapy.formatter;
    };
}
