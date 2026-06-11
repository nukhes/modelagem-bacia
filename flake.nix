{
  description = "devshell para modelagem de bacias com blender e python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      pythonPackages = ps: with ps; [
        attrs
        black
        cattrs
        certifi
        charset-normalizer
        click
        cython
        geopandas
        idna
        mypy-extensions
        numpy
        packaging
        pandas
        pathspec
        platformdirs
        pyogrio
        pyproj
        python-dateutil
        requests
        scipy
        shapely
        six
        typing-extensions
        urllib3
        zstandard
      ];

      pythonEnv = pkgs.python3.withPackages pythonPackages;
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.blender
          pythonEnv
        ];

        shellHook = ''
          export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
        '';
      };
    };
}
