{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python312;
in
pkgs.mkShell {
  buildInputs = [
    python
    python.pkgs.pip
    python.pkgs.numpy
    python.pkgs.pandas
    python.pkgs.matplotlib
    python.pkgs.pillow
    python.pkgs.plotly
    
    # System dependencies
    pkgs.gcc
    pkgs.zlib
  ];

  shellHook = ''
    echo "🌍 Earthquake Dashboard Development Environment"
    echo "Python version: $(python --version)"
    
    # Set up pip to install to local directory
    export PIP_PREFIX="$PWD/_pip_packages"
    export PYTHONPATH="$PIP_PREFIX/lib/python3.12/site-packages:$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    
    # Install packages not available in nixpkgs
    if [ ! -f "_pip_packages/.installed" ]; then
      echo "Installing additional Python packages..."
      mkdir -p "$PIP_PREFIX"
      pip install --quiet faicons shiny shinywidgets ridgeplot kagglehub
      touch "_pip_packages/.installed"
    fi
    
    echo ""
    echo "✅ Environment ready!"
    echo "Run 'shiny run app.py' to start the dashboard"
  '';
}
