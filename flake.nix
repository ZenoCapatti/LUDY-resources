{
  description = "Marimo environment for local GammaLoop development";

  inputs = {
    # Keep the previously working Darwin toolchain while GammaLoop's current
    # Fenix lock is missing libLLVM.dylib for rust-lld's WASM link step.
    crane.url = "github:ipetkov/crane/dc7496d8ea6e526b1254b55d09b966e94673750f";
    fenix = {
      url = "github:nix-community/fenix/d0ff0a903e7db7f8e71d5f7862446b7c92f12df7";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.rust-analyzer-src.follows = "";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/b86751bc4085f48661017fa226dee99fab6c651b";

    # Public pin keeps the repository evaluable away from this workstation.
    # Local source edits are still supplied to uv through pyproject.toml.
    gammaloop = {
      url = "github:alphal00p/gammaloop/4f44c86382977bade32a230801034b5c37faddbd";
      inputs.crane.follows = "crane";
      inputs.fenix.follows = "fenix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
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
              import ./packages/kirapy/nix { pkgs = runtimePkgs; }
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
