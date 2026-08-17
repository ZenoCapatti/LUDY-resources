{
  lib,
  stdenv,
  fetchzip,
  meson,
  ninja,
  pkg-config,
  makeWrapper,
  cln,
  ginac,
  zlib,
  yaml-cpp,
  fermat,
}:

let
  rev = "dad964cd79a39a9fca728bb2606f59537a95109c";

  # In the pinned Nixpkgs revision CLN uses gccStdenv while GiNaC uses the
  # default Darwin stdenv. The resulting incompatible C++ standard-library
  # symbols make GiNaC crash while printing numbers. Build both with the same
  # stdenv on Darwin. Linux already uses the GCC stdenv consistently.
  clnForKira = if stdenv.hostPlatform.isDarwin then cln.override { gccStdenv = stdenv; } else cln;

  ginacForKira = ginac.override { cln = clnForKira; };
in
stdenv.mkDerivation (finalAttrs: {
  pname = "kira";
  version = "3.1-git-${builtins.substring 0 7 rev}";

  src = fetchzip {
    url = "https://gitlab.com/kira-pyred/kira/-/archive/${rev}/kira-${rev}.tar.gz";
    hash = "sha256-1gHuR2e5rX5OcOHcTBnLO7gRV/bbxiDvRdSjd/aD9Nk=";
  };

  strictDeps = true;
  enableParallelBuilding = true;

  nativeBuildInputs = [
    meson
    ninja
    pkg-config
    makeWrapper
  ];

  buildInputs = [
    ginacForKira
    zlib
    yaml-cpp
  ];

  nativeCheckInputs = [ fermat ];

  mesonFlags = [
    "-Dfirefly=false"
    "-Dflint=false"
    "-Dmpi=false"
    "-Djemalloc=false"
    "-Dkyotocabinet=false"
    "-Dpyredtests=false"
    "-Dstatic=false"
    "-Dweight_width=64"
    "-Dtest-level=full"
  ];

  postPatch = ''
    substituteInPlace src/pyred/meson.build \
      --replace-fail "fallback : 'no'" \
                     "fallback : '${rev}'"
  '';

  doCheck = stdenv.buildPlatform.canExecute stdenv.hostPlatform;
  preCheck = ''
    export FERMATPATH="${fermat}/bin/fer64"
  '';

  postFixup = ''
    wrapProgram "$out/bin/kira" \
      --set-default FERMATPATH "${fermat}/bin/fer64"
  '';

  passthru = {
    inherit rev fermat;
  };

  meta = {
    description = "Feynman integral reduction with integration-by-parts identities";
    homepage = "https://gitlab.com/kira-pyred/kira";
    license = lib.licenses.gpl3Plus;
    platforms = [
      "aarch64-darwin"
      "x86_64-linux"
    ];
    mainProgram = "kira";
  };
})
