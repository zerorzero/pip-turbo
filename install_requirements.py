import subprocess
import concurrent.futures
import threading
import os
import sys


def install_package(package):
    """
    Attempts to install a single package using pip.

    Args:
        package (str): The package name to install.

    Returns:
        tuple: (package, success, error_message)
    """
    try:
        # Use the full path to the pip executable
        pip_executable = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'pip.exe')
        subprocess.check_call([pip_executable, 'install', package])
        return (package, True, "")
    except subprocess.CalledProcessError as e:
        return (package, False, str(e))
    except Exception as e:
        return (package, False, str(e))


def install_requirements(file_path, encoding='utf-8', max_workers=4, failed_output='requirements_failed.txt'):
    """
    Reads the requirements file and installs packages concurrently.
    Outputs failed packages to a new requirements file.

    Args:
        file_path (str): Path to the requirements file.
        encoding (str): Encoding of the requirements file.
        max_workers (int): Maximum number of concurrent threads.
        failed_output (str): Path to output the failed packages.
    """
    packages = []
    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            package = line.strip()
            if package and not package.startswith('#'):
                packages.append(package)

    if not packages:
        print("No packages to install.")
        return

    print(f"Starting installation of {len(packages)} packages...\n")

    # To store installation results
    results = []
    lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Start the installation processes
        future_to_package = {executor.submit(install_package, pkg): pkg for pkg in packages}

        for future in concurrent.futures.as_completed(future_to_package):
            pkg = future_to_package[future]
            try:
                package, success, error = future.result()
                with lock:
                    if success:
                        print(f"✅ Successfully installed: {package}")
                    else:
                        print(f"❌ Failed to install: {package}\n   Error: {error}")
                results.append((package, success, error))
            except Exception as exc:
                with lock:
                    print(f"❌ Exception occurred while installing {pkg}: {exc}")
                results.append((pkg, False, str(exc)))

    # Summary
    print("\nInstallation Summary:")
    success_count = sum(1 for _, success, _ in results if success)
    failure_count = len(results) - success_count
    print(f"✅ Successfully installed: {success_count}")
    print(f"❌ Failed to install: {failure_count}")

    # Write failed packages to a new requirements file
    if failure_count > 0:
        failed_packages = [pkg for pkg, success, _ in results if not success]
        with open(failed_output, 'w', encoding='utf-8') as f:
            for pkg in failed_packages:
                f.write(f"{pkg}\n")
        print(f"\n❌ Failed packages have been written to `{failed_output}`.")
    else:
        print("🎉 All packages installed successfully. No failed packages.")


if __name__ == "__main__":
    install_requirements('requirements.txt')
