import subprocess
import sys


def deploy_program(version): 
    file_name = f'SeaingClearly_v{version}'
    
    try:
        print("Deploying...")
        subprocess.run(['pyinstaller', '--windowed', '--onedir', r'--icon=seaingclearly\assets\prawn\prawn.png', '--name', file_name, '--add-data', r'seaingclearly\assets;assets',  r'seaingclearly\app.py'], check=True)
                
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)


deploy_program("1.0.0")
