{
  lib,
  stdenvNoCC,
  fetchurl,
  autoPatchelfHook,
  glibc ? null,
}:

let
  system = stdenvNoCC.hostPlatform.system;

  sources = {
    aarch64-darwin = {
      url = "https://home.bway.net/lewis/fermat64/Ferm7a.tar.gz";
      hash = "sha256-rm1PYlE6dbS2m/9LYQjw4ne960DI3JJKBy+SWkOpk+Q=";
      sourceRoot = "Ferm7a";
    };
    x86_64-linux = {
      url = "https://home.bway.net/lewis/fermat64/Ferl7.tar.gz";
      hash = "sha256-Z5VMxMvG6WuKIIDhQuDOfK0F0QNu3JKOZgDeR4iKYGw=";
      sourceRoot = "Ferl7";
    };
  };

  source =
    sources.${system} or (throw ''
      Fermat 7.9b has no pinned official binary for ${system}.
      Bundled support is limited to aarch64-darwin and x86_64-linux.
      Configure an external Kira/Fermat runtime instead.
    '');

  backwardFiles = [
    "f256d"
    "f2t16d"
    "ferstart.txt"
    "Qerrs"
    "pow228"
    "chdat"
    "pprods"
    "primelist"
    "bprimes"
    "lrgpmes"
  ];
in
stdenvNoCC.mkDerivation (finalAttrs: {
  pname = "fermat";
  version = "7.9b";

  src = fetchurl {
    inherit (source) url hash;
  };
  inherit (source) sourceRoot;

  strictDeps = true;
  dontBuild = true;
  # The Darwin download is an ad-hoc signed Mach-O executable. Preserve it.
  dontStrip = true;

  nativeBuildInputs = lib.optionals stdenvNoCC.hostPlatform.isLinux [ autoPatchelfHook ];
  buildInputs = lib.optionals stdenvNoCC.hostPlatform.isLinux [ glibc ];

  installPhase = ''
    runHook preInstall

    install -Dm755 fer64 "$out/bin/fer64"
    mkdir -p "$out/bin/BACKWARD" "$out/share/fermat"

    for dataFile in ${lib.concatStringsSep " " backwardFiles}; do
      install -m644 "BACKWARD/$dataFile" "$out/bin/BACKWARD/$dataFile"
    done

    install -m644 dixon resul factr "$out/share/fermat/"

    runHook postInstall
  '';

  doInstallCheck = stdenvNoCC.buildPlatform.canExecute stdenvNoCC.hostPlatform;
  installCheckPhase = ''
    runHook preInstallCheck

    printf '&q\n' | "$out/bin/fer64" > fermat-smoke.log
    grep -F "rational C version ${finalAttrs.version}" fermat-smoke.log
    grep -F "Reading initialization data from directory $out/bin/BACKWARD/" fermat-smoke.log

    runHook postInstallCheck
  '';

  meta = {
    description = "Fermat computer algebra system";
    homepage = "https://home.bway.net/lewis/ferm7.html";
    # Upstream permits redistribution but forbids business and for-profit use
    # without express written permission from the copyright holder.
    license = lib.licenses.unfreeRedistributable;
    platforms = builtins.attrNames sources;
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    mainProgram = "fer64";
  };
})
