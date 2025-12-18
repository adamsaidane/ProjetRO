"""
Script d'installation et de vérification pour le projet RO
Vérifie toutes les dépendances et guide l'installation
"""

import sys
import subprocess
import platform

def print_header(text):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60)

def check_python_version():
    """Vérifie la version de Python"""
    print("\n🐍 Vérification de Python...")
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 ou supérieur est requis!")
        print("📥 Téléchargez Python depuis: https://www.python.org/downloads/")
        return False
    else:
        print("✅ Version Python compatible")
        return True

def check_package(package_name, import_name=None):
    """Vérifie si un package est installé"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} est installé")
        return True
    except ImportError:
        print(f"❌ {package_name} n'est pas installé")
        return False

def install_package(package_name):
    """Installe un package via pip"""
    print(f"📦 Installation de {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erreur lors de l'installation de {package_name}")
        return False

def check_gurobi_license():
    """Vérifie si Gurobi a une licence valide"""
    print("\n🔑 Vérification de la licence Gurobi...")
    try:
        import gurobipy as gp
        try:
            # Tenter de créer un environnement
            env = gp.Env()
            env.dispose()
            print("✅ Licence Gurobi valide")
            return True
        except gp.GurobiError as e:
            print(f"❌ Erreur de licence Gurobi: {e}")
            print("\n📋 Pour obtenir une licence académique gratuite:")
            print("1. Créer un compte sur: https://www.gurobi.com/academia/")
            print("2. Demander une licence académique")
            print("3. Exécuter: grbgetkey VOTRE-CLE-DE-LICENCE")
            print("\n⚠️  Important: Vous devez être sur le réseau universitaire")
            return False
    except ImportError:
        print("❌ Gurobi n'est pas installé")
        return False

def check_all_dependencies():
    """Vérifie toutes les dépendances"""
    print_header("VÉRIFICATION DES DÉPENDANCES")
    
    packages = [
        ("gurobipy", "gurobipy"),
        ("PySide6", "PySide6"),
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy"),
        ("pandas", "pandas")
    ]
    
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    return missing_packages

def install_missing_packages(missing_packages):
    """Installe les packages manquants"""
    if not missing_packages:
        print("\n✅ Tous les packages sont déjà installés!")
        return True
    
    print(f"\n📦 {len(missing_packages)} package(s) à installer:")
    for pkg in missing_packages:
        print(f"  - {pkg}")
    
    response = input("\nVoulez-vous installer ces packages? (o/n): ")
    
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        print_header("INSTALLATION DES PACKAGES")
        success = True
        for pkg in missing_packages:
            if not install_package(pkg):
                success = False
        return success
    else:
        print("❌ Installation annulée")
        return False

def test_imports():
    """Teste l'importation de tous les modules"""
    print_header("TEST DES IMPORTS")
    
    modules = [
        ("gurobipy", "Gurobi"),
        ("PySide6.QtWidgets", "PySide6"),
        ("matplotlib.pyplot", "Matplotlib"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas")
    ]
    
    all_ok = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name} fonctionne")
        except Exception as e:
            print(f"❌ {display_name} ne fonctionne pas: {e}")
            all_ok = False
    
    return all_ok

def display_system_info():
    """Affiche les informations système"""
    print_header("INFORMATIONS SYSTÈME")
    print(f"Système d'exploitation: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print(f"Chemin Python: {sys.executable}")

def create_test_script():
    """Crée un script de test rapide"""
    test_code = '''"""Test rapide du projet"""
import sys

print("Test d'importation des modules...")

try:
    import gurobipy as gp
    print("✅ Gurobi OK")
except ImportError as e:
    print(f"❌ Gurobi: {e}")
    sys.exit(1)

try:
    from PySide6.QtWidgets import QApplication
    print("✅ PySide6 OK")
except ImportError as e:
    print(f"❌ PySide6: {e}")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    print("✅ Matplotlib OK")
except ImportError as e:
    print(f"❌ Matplotlib: {e}")
    sys.exit(1)

try:
    import numpy as np
    print("✅ NumPy OK")
except ImportError as e:
    print(f"❌ NumPy: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("✅ Pandas OK")
except ImportError as e:
    print(f"❌ Pandas: {e}")
    sys.exit(1)

print("\\n✅ Tous les modules sont fonctionnels!")
print("Vous pouvez maintenant lancer: python main.py")
'''
    
    with open("test_quick.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    print("✅ Fichier 'test_quick.py' créé")

def main():
    """Fonction principale"""
    print_header("INSTALLATION DU PROJET RO")
    print("Gestion Multi-Période des Stocks de Carburant")
    
    # Afficher les informations système
    display_system_info()
    
    # Vérifier Python
    if not check_python_version():
        sys.exit(1)
    
    # Vérifier les dépendances
    missing_packages = check_all_dependencies()
    
    # Installer les packages manquants
    if missing_packages:
        if not install_missing_packages(missing_packages):
            print("\n❌ Installation incomplète")
            sys.exit(1)
    
    # Tester les imports
    if not test_imports():
        print("\n❌ Certains modules ne fonctionnent pas correctement")
        sys.exit(1)
    
    # Vérifier Gurobi
    check_gurobi_license()
    
    # Créer un script de test rapide
    print_header("CRÉATION DU SCRIPT DE TEST")
    create_test_script()
    
    # Instructions finales
    print_header("INSTALLATION TERMINÉE")
    print("\n✅ Tous les packages sont installés!")
    print("\n📝 Prochaines étapes:")
    print("1. Si Gurobi n'a pas de licence valide:")
    print("   - Obtenir une clé sur https://www.gurobi.com/academia/")
    print("   - Exécuter: grbgetkey VOTRE-CLE")
    print("\n2. Tester l'installation:")
    print("   python test_quick.py")
    print("\n3. Tester le modèle:")
    print("   python test_model.py")
    print("\n4. Lancer l'application:")
    print("   python main.py")
    print("\n5. Générer des données de test:")
    print("   python generate_data.py")
    
    print("\n" + "="*60)
    print("📚 Pour plus d'informations, consultez README.md")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        sys.exit(1)