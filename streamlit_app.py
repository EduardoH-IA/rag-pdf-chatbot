import sys
import os

# Agregar la carpeta raiz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la app
from src.app import main

if __name__ == "__main__":
    main()
