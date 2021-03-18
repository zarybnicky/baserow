{
  inputs.nixpkgs.url = github:NixOS/nixpkgs/nixos-20.09;

  outputs = { self, nixpkgs }: let
    inherit (nixpkgs.lib) flip mapAttrs mapAttrsToList;
    inherit (pkgs.nix-gitignore) gitignoreSourcePure gitignoreSource;
    getSrc = dir: gitignoreSourcePure [./.gitignore] dir;

    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [ self.overlay ];
    };
  in {
    overlay = final: prev: {
      python38 = prev.python38.override {
        packageOverrides = pyself: pysuper: {
          django-mjml = pkgs.python38Packages.buildPythonPackage rec {
            pname = "django-mjml";
            version = "0.10.2";
            src = pkgs.python38Packages.fetchPypi {
              inherit pname version;
              sha256 = "HiTd5S0dNckT1Y5eILc8mRhvvyTYCHg0VF6zqYqd1bM=";
            };
            propagatedBuildInputs = [ pkgs.python38Packages.django ];
            doCheck = false;
          };
          drf-spectacular = pkgs.python38Packages.buildPythonPackage rec {
            pname = "drf-spectacular";
            version = "0.14.0";
            src = pkgs.python38Packages.fetchPypi {
              inherit pname version;
              sha256 = "3z1aEkt+L3l68jryx5dYFfhtuiXUJRQymXzC97qHzkE=";
            };
            propagatedBuildInputs = [
              pkgs.python38Packages.django
              pkgs.python38Packages.djangorestframework
              pkgs.python38Packages.inflection
              pkgs.python38Packages.jsonschema
              pkgs.python38Packages.uritemplate
              pkgs.python38Packages.pyyaml
            ];
            doCheck = false;
          };
          advocate = pkgs.python38Packages.buildPythonPackage rec {
            pname = "advocate";
            version = "1.0.0";
            src = pkgs.python38Packages.fetchPypi {
              inherit pname version;
              sha256 = "G/EXDkEzQnmZZYAynFlOAXVAqw6vehUjI+dD8KhaNT0=";
            };
            propagatedBuildInputs = [
              pkgs.python38Packages.ndg-httpsclient
              pkgs.python38Packages.netifaces
              pkgs.python38Packages.requests
            ];
            doCheck = false;
          };
        };
      };
      baserow-web = final.mkYarnPackage {
        name = "baserow-web";
        src = ./web-frontend;
        packageJson = ./web-frontend/package.json;
        yarnLock = ./web-frontend/yarn.lock;
        yarnNix = ./web-frontend/yarn.nix;
      };

      baserow-web-build = final.runCommand "nuxt" ''
        mkdir -p $out
        cd $out
        ${final.baserow-web}/node_modules/nuxt/bin/nuxt.js build --config-file ${final.baserow-web}/config/nuxt.config.demo.js
      '' {};
    };

    devShell.x86_64-linux = pkgs.mkShell {
      buildInputs = [
        pkgs.yarn2nix
        (pkgs.python38.withPackages (ps: with ps; [
          django django-cors-headers
          djangorestframework djangorestframework-jwt
          psycopg2 mysqlclient ipython faker twisted
          gunicorn uvicorn django-mjml requests itsdangerous
          drf-spectacular pillow channels channels-redis
          celery advocate
        ]))
      ];
    };
  };
}
