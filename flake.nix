{
  description = "Marimo environment for local GammaLoop development";

  inputs = {
    # Public pin keeps the repository evaluable away from this workstation.
    # Local source edits are still supplied to uv through pyproject.toml.
    gammaloop.url = "github:alphal00p/gammaloop/728f9a3b4053259fbd0dbd4177801dadcebf6d8c";
    nixpkgs.follows = "gammaloop/nixpkgs";
  };

  outputs =
    {
      gammaloop,
      nixpkgs,
      ...
    }:
    {
      devShells = builtins.mapAttrs (
        system: shells:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          runtimePkgs = import nixpkgs {
            inherit system;
            config.allowUnfreePredicate = package: nixpkgs.lib.getName package == "fermat";
          };
          bundledKiraRuntime =
            if
              builtins.elem system [
                "aarch64-darwin"
                "x86_64-linux"
              ]
            then
              import ./packages/ludy-kira/nix { pkgs = runtimePkgs; }
            else
              null;
        in
        shells
        // {
          default = shells.default.overrideAttrs (
            old:
            {
              nativeBuildInputs =
                (old.nativeBuildInputs or [ ])
                ++ [ pkgs.nodejs ]
                ++ pkgs.lib.optionals (bundledKiraRuntime != null) [
                  bundledKiraRuntime.fermat
                  bundledKiraRuntime.kira
                ];
              NO_SYMBOLICA_OEM_LICENSE = "1";
              UV_PYTHON = "${pkgs.python313}/bin/python3";
              UV_PYTHON_DOWNLOADS = "never";
            }
            // pkgs.lib.optionalAttrs (bundledKiraRuntime != null) {
              FERMATPATH = "${bundledKiraRuntime.fermat}/bin/fer64";
            }
          );
        }
      ) gammaloop.devShells;
    };
}
