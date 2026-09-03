{
  description = "Portable development runtime for the kirapy Python package";

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
          # Nixpkgs' fetchCargoVendor helper still downloads registry crates
          # through crates.io's API redirect.  That endpoint rejects the
          # sandboxed fetcher, while crates.io's canonical static endpoint is
          # intended for direct crate downloads.  Keep using the pinned
          # Nixpkgs helper and its Cargo.lock validation, changing only that
          # download URL.
          patchedFetchCargoVendorUtil =
            pkgs.writers.writePython3Bin "fetch-cargo-vendor-util"
              {
                libraries =
                  with pkgs.python3Packages;
                  [
                    requests
                    tomli-w
                  ]
                  ++ requests.optional-dependencies.socks;
                flakeIgnore = [ "E501" ];
              }
              (
                builtins.replaceStrings
                  [ ''return f"https://crates.io/api/v1/crates/{pkg["name"]}/{pkg["version"]}/download"'' ]
                  [ ''return f"https://static.crates.io/crates/{pkg["name"]}/{pkg["name"]}-{pkg["version"]}.crate"'' ]
                  (builtins.readFile "${nixpkgs}/pkgs/build-support/rust/fetch-cargo-vendor-util.py")
              );
          symbolicaOverlay = final: prev: {
            symbolica =
              assert lib.assertMsg (final.maturin.version == "1.14.1") "Symbolica must build with Maturin 1.14.1";
              prev.symbolica.overrideAttrs (
                old:
                let
                  # Symbolica's Git source intentionally no longer tracks its
                  # generated Cargo.lock.  Reattach the lock generated at the
                  # exact Python dependency revision so that both vendoring and
                  # the Maturin build consume the same dependency graph.
                  srcWithCargoLock = pkgs.runCommand "symbolica-${old.version}-source" { } ''
                    cp -R ${old.src} "$out"
                    chmod -R u+w "$out"
                    cp ${./nix/symbolica-Cargo.lock} "$out/Cargo.lock"
                  '';
                in
                {
                  src = srcWithCargoLock;
                  cargoDeps = pkgs.rustPlatform.fetchCargoVendor {
                    src = srcWithCargoLock;
                    name = "symbolica-${old.version}-vendor";
                    hash = "sha256-Dj4rK2/22s0ZfseJUPemIR3MApWj84as4gMod1xe7SA=";
                    preBuild = ''
                      export PATH="${patchedFetchCargoVendorUtil}/bin:$PATH"
                    '';
                  };
                  nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
                    pkgs.rustPlatform.cargoSetupHook
                    pkgs.cargo
                    pkgs.rustc
                    pkgs.m4
                  ];
                }
              );
          };
        in
        (pkgs.callPackage pyproject-nix.build.packages { python = pkgs.python313; }).overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            lockOverlay
            symbolicaOverlay
          ]
        );
      testEnvironmentFor =
        system:
        let
          pythonSet = pythonSetFor system;
        in
        pythonSet.mkVirtualEnv "kirapy-test-env" (
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
          unitTests = pkgs.runCommand "kirapy-unit-tests" { nativeBuildInputs = [ testEnvironment ]; } ''
            ${commonTestSetup}
            pytest -q -p no:cacheprovider tests \
              --ignore=tests/test_topo1_integration.py \
              --ignore=tests/test_topo2_integration.py \
              --ignore=tests/test_topo3_integration.py \
              --ignore=tests/test_topo4_integration.py \
              --ignore=tests/test_topo5_integration.py \
              --ignore=tests/test_topo6_integration.py \
              --ignore=tests/test_topo7_integration.py \
              --ignore=tests/test_topo8_integration.py \
              --ignore=tests/test_topo10_integration.py \
              --ignore=tests/test_topo11_integration.py \
              --ignore=tests/test_topo20_integration.py \
              --ignore=tests/test_topo21_integration.py \
              --ignore=tests/test_crossed_box_integration.py
            touch "$out"
          '';
          topo1Integration =
            pkgs.runCommand "kirapy-topo1-integration"
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
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo1_integration.py
                touch "$out"
              '';
          topo2Integration =
            pkgs.runCommand "kirapy-topo2-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo1IntegrationResults = topo1Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo2_integration.py
                touch "$out"
              '';
          topo3Integration =
            pkgs.runCommand "kirapy-topo3-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo2IntegrationResults = topo2Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo3_integration.py
                touch "$out"
              '';
          topo4Integration =
            pkgs.runCommand "kirapy-topo4-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo3IntegrationResults = topo3Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo4_integration.py
                touch "$out"
              '';
          topo5Integration =
            pkgs.runCommand "kirapy-topo5-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo4IntegrationResults = topo4Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo5_integration.py
                touch "$out"
              '';
          topo6Integration =
            pkgs.runCommand "kirapy-topo6-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo5IntegrationResults = topo5Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo6_integration.py
                touch "$out"
              '';
          topo7Integration =
            pkgs.runCommand "kirapy-topo7-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo6IntegrationResults = topo6Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo7_integration.py
                touch "$out"
              '';
          topo8Integration =
            pkgs.runCommand "kirapy-topo8-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo7IntegrationResults = topo7Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo8_integration.py
                touch "$out"
              '';
          topo10Integration =
            pkgs.runCommand "kirapy-topo10-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo8IntegrationResults = topo8Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo10_integration.py
                touch "$out"
              '';
          topo11Integration =
            pkgs.runCommand "kirapy-topo11-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo10IntegrationResults = topo10Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo11_integration.py
                touch "$out"
              '';
          topo20Integration =
            pkgs.runCommand "kirapy-topo20-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                topo11IntegrationResults = topo11Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo20_integration.py
                touch "$out"
              '';
          topo21Integration =
            pkgs.runCommand "kirapy-topo21-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                topo20IntegrationResults = topo20Integration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider tests/test_topo21_integration.py
                touch "$out"
              '';
          crossedBoxIntegration =
            topologyId: previousIntegration:
            pkgs.runCommand "kirapy-topo${toString topologyId}-integration"
              {
                nativeBuildInputs = [
                  testEnvironment
                  runtime.kira
                ];
                # Serialize restricted Symbolica and native Kira checks.
                previousIntegrationResults = previousIntegration;
              }
              ''
                ${commonTestSetup}
                export KIRAPY_RUN_INTEGRATION=1
                export KIRA_BIN="${runtime.kira}/bin/kira"
                export FERMATPATH="${runtime.fermat}/bin/fer64"
                pytest -q -p no:cacheprovider \
                  "tests/test_crossed_box_integration.py::test_real_kira_matches_regenerated_fire_crossed_box[topo${toString topologyId}]"
                touch "$out"
              '';
          topo22Integration = crossedBoxIntegration 22 topo21Integration;
          topo23Integration = crossedBoxIntegration 23 topo22Integration;
          topo24Integration = crossedBoxIntegration 24 topo23Integration;
          topo25Integration = crossedBoxIntegration 25 topo24Integration;
          topo26Integration = crossedBoxIntegration 26 topo25Integration;
          topo27Integration = crossedBoxIntegration 27 topo26Integration;
          topo28Integration = crossedBoxIntegration 28 topo27Integration;
          topo29Integration = crossedBoxIntegration 29 topo28Integration;
          topo30Integration = crossedBoxIntegration 30 topo29Integration;
          topo31Integration = crossedBoxIntegration 31 topo30Integration;
        in
        {
          unit-tests = unitTests;
          topo1-integration = topo1Integration;
          topo2-integration = topo2Integration;
          topo3-integration = topo3Integration;
          topo4-integration = topo4Integration;
          topo5-integration = topo5Integration;
          topo6-integration = topo6Integration;
          topo7-integration = topo7Integration;
          topo8-integration = topo8Integration;
          topo10-integration = topo10Integration;
          topo11-integration = topo11Integration;
          topo20-integration = topo20Integration;
          topo21-integration = topo21Integration;
          topo22-integration = topo22Integration;
          topo23-integration = topo23Integration;
          topo24-integration = topo24Integration;
          topo25-integration = topo25Integration;
          topo26-integration = topo26Integration;
          topo27-integration = topo27Integration;
          topo28-integration = topo28Integration;
          topo29-integration = topo29Integration;
          topo30-integration = topo30Integration;
          topo31-integration = topo31Integration;
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
              pkgs.cargo
              pkgs.rustc
              pkgs.m4
              pkgs.git
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
