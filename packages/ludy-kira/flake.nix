{
  description = "Portable development runtime for the ludy-kira Python package";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/b86751bc4085f48661017fa226dee99fab6c651b";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
    };
  };

  outputs =
    {
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;

      systems = [
        "aarch64-darwin"
        "x86_64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor =
        system:
        import nixpkgs {
          inherit system;
          config.allowUnfreePredicate = pkg: nixpkgs.lib.getName pkg == "fermat";
        };
      runtimeFor = system: import ./nix { pkgs = pkgsFor system; };

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      pythonSetFor =
        system:
        let
          pkgs = pkgsFor system;
          lockOverlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
        in
        (pkgs.callPackage pyproject-nix.build.packages { python = pkgs.python313; }).overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            lockOverlay
          ]
        );
      testEnvironmentFor =
        system:
        let
          pythonSet = pythonSetFor system;
        in
        pythonSet.mkVirtualEnv "ludy-kira-test-env" (
          workspace.deps.default
          // {
            pytest = [ ];
          }
        );
      pythonChecksFor =
        system:
        let
          pkgs = pkgsFor system;
          runtime = runtimeFor system;
          testEnvironment = testEnvironmentFor system;
          commonTestSetup = ''
            export HOME="$TMPDIR"
            export XDG_CACHE_HOME="$TMPDIR/cache"
            export PYTHONDONTWRITEBYTECODE=1
            cd ${./.}
          '';
          unitTests = pkgs.runCommand "ludy-kira-unit-tests" { nativeBuildInputs = [ testEnvironment ]; } ''
            ${commonTestSetup}
            pytest -q -p no:cacheprovider tests --ignore=tests/test_topo1_integration.py
            touch "$out"
          '';
          topo1Integration =
            pkgs.runCommand "ludy-kira-topo1-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # A restricted Symbolica runtime permits only one active engine.
                # Keep this separate check, but serialize it after the unit suite.
                unitTestResults = unitTests;
              }
              ''
                ${commonTestSetup}
                export LUDY_KIRA_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo1_integration.py
                touch "$out"
              '';
        in
        {
          unit-tests = unitTests;
          topo1-integration = topo1Integration;
        };
    in
    {
      packages = forAllSystems (
        system:
        let
          runtime = runtimeFor system;
        in
        {
          inherit (runtime) fermat kira;
          default = runtime.kira;
        }
      );

      checks = forAllSystems (
        system:
        let
          runtime = runtimeFor system;
        in
        {
          inherit (runtime) fermat kira;
        }
        // pythonChecksFor system
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
          runtime = runtimeFor system;
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python313
              pkgs.uv
              runtime.fermat
              runtime.kira
            ];

            FERMATPATH = "${runtime.fermat}/bin/fer64";
            UV_PYTHON = "${pkgs.python313}/bin/python3";
            UV_PYTHON_DOWNLOADS = "never";
          };
        }
      );

      formatter = forAllSystems (system: (pkgsFor system).nixfmt);
    };
}
