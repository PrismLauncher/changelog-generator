{
  inputs,
  self,
  ...
}: {
  perSystem = {
    system,
    pkgs,
    ...
  }: {
    checks = {
      pre-commit-check = inputs.pre-commit-hooks.lib.${system}.run {
        src = self;
        hooks = {
          markdownlint.enable = true;
          prettier.enable = true;

          alejandra.enable = true;
          deadnix.enable = true;
          nil.enable = true;

          black.enable = true;
        };
      };
    };

    devShells.default = let
      pythonEnv = pkgs.python3.withPackages (p: with p; [pygithub]);
    in
      pkgs.mkShell {
        inherit (self.checks.${system}.pre-commit-check) shellHook;
        packages = [pythonEnv];
      };

    formatter = pkgs.alejandra;
  };
}
