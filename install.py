import subprocess
import sys
from pathlib import Path


def install_requirements(requirements_path: Path) -> int:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"Failed to install dependencies: {exc}")
        return exc.returncode


def main() -> int:
    requirements_path = Path(__file__).parent / "requirements.txt"
    if not requirements_path.exists():
        print("requirements.txt not found. Please make sure you are in the project root.")
        return 1

    print("Installing Testownik dependencies...")
    return install_requirements(requirements_path)


if __name__ == "__main__":
    raise SystemExit(main())
