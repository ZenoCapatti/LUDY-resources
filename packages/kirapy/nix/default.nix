{
  pkgs,
  externalKira ? null,
  externalFermat ? null,
}:

let
  system = pkgs.stdenv.hostPlatform.system;
  bundledSystems = [
    "aarch64-darwin"
    "x86_64-linux"
  ];
  supportsBundledRuntime = builtins.elem system bundledSystems;

  bundledFermat = pkgs.callPackage ./fermat.nix { };
  bundledKira = pkgs.callPackage ./kira.nix { fermat = bundledFermat; };
in
if externalKira != null then
  {
    kira = externalKira;
    fermat = externalFermat;
    bundled = false;
    inherit supportsBundledRuntime;
  }
else if supportsBundledRuntime then
  {
    kira = bundledKira;
    fermat = bundledFermat;
    bundled = true;
    inherit supportsBundledRuntime;
  }
else
  throw ''
    No bundled Kira/Fermat runtime is available for ${system}.
    Supported bundled systems: ${builtins.concatStringsSep ", " bundledSystems}.
    Pass externalKira (and, if needed, externalFermat) to nix/default.nix.
  ''
