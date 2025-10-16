"""
Install dependencies needed for migration scripts
"""
import subprocess
import sys

def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_package(package):
    """Check if a package is installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRATION DEPENDENCIES INSTALLER")
    print("=" * 60)
    
    packages = ['tabulate']
    
    print("\nChecking required packages...")
    
    all_installed = True
    for package in packages:
        if check_package(package):
            print(f"✅ {package} is already installed")
        else:
            print(f"⚠️  {package} is not installed")
            all_installed = False
    
    if not all_installed:
        print("\nInstalling missing packages...")
        for package in packages:
            if not check_package(package):
                install_package(package)
    
    print("\n" + "=" * 60)
    print("Verifying installation...")
    print("=" * 60)
    
    success = True
    for package in packages:
        if check_package(package):
            print(f"✅ {package} is ready")
        else:
            print(f"❌ {package} installation failed")
            success = False
    
    if success:
        print("\n✅ All dependencies are installed!")
        print("   You can now run: python verify_role_migration.py")
    else:
        print("\n⚠️  Some dependencies failed to install")
        print("   Try installing manually: pip install tabulate")