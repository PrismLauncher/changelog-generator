{
  self,
  version,
  ...
}: {
  perSystem = {pkgs, ...}: {
    packages = {
      inherit (pkgs) changelog-generator;
      default = pkgs.changelog-generator;
    };
  };

  flake = {
    overlays.default = final: _: {
      changelog-generator = final.python3Packages.callPackage ./derivation.nix {inherit self version;};
    };
  };
}
