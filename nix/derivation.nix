{
  lib,
  buildPythonApplication,
  poetry-core,
  pygithub,
  # flake
  self,
  version,
}: let
  inherit (lib.sources) cleanSource;
in
  buildPythonApplication {
    pname = "changelog-generator";
    inherit version;
    format = "pyproject";

    src = cleanSource self;

    nativeBuildInputs = [poetry-core];

    propagatedBuildInputs = [pygithub];

    pythonImportsCheck = ["changelog_generator"];

    meta = with lib; {
      description = "Prism Launcher changelog generator";
      homepage = "https://github.com/PrismLauncher/changelog-generator";
      license = licenses.agpl3Only;
      maintainers = with maintainers; [Scrumplex];
    };
  }
