"""Utility helpers for working with the UIUC airfoil archive."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Tuple

import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Summary of a download operation performed by :func:`get_save_airfoils`."""

    saved: List[Path]
    skipped: List[Path]
    errors: List[Tuple[Path, str]]

    @property
    def had_failures(self) -> bool:
        """Return ``True`` if at least one airfoil failed to download."""

        return bool(self.errors)


def _iter_airfoil_files(directory: Path) -> Iterable[Tuple[str, Path]]:
    """Yield ``(name, path)`` pairs for every ``.dat`` file in ``directory``."""

    if not directory.exists():
        return []

    for entry in sorted(directory.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() != ".dat":
            continue
        yield entry.name, entry


def get_foils_from_dir(data_path: str) -> List[Tuple[str, str]]:
    """Return the ``(filename, absolute_path)`` pairs for airfoils in ``data_path``.

    The original implementation returned directories and non-airfoil files which
    subsequently caused runtime errors in the controllers.  The helper now
    filters out non-files and normalises paths, making it safe to use in tests
    and production code.
    """

    directory = Path(data_path)
    if not directory.exists():
        logger.debug("Airfoil directory %s does not exist", directory)
        return []

    return [(name, os.fspath(path)) for name, path in _iter_airfoil_files(directory)]


class AirfoilDownloadError(RuntimeError):
    """Raised when downloading the UIUC airfoil archive fails."""


def get_save_airfoils(
    target_directory: str | os.PathLike[str] | None = None,
    *,
    overwrite: bool = False,
    limit: int | None = None,
    progress_callback: Callable[[int, str, Path], None] | None = None,
) -> DownloadResult:
    """Download the UIUC airfoil archive into ``target_directory``.

    Args:
        target_directory: Directory where the ``.dat`` files should be stored.
            When omitted the current working directory is used.  The directory
            is created automatically when necessary.
        overwrite: Re-download files that already exist when ``True``.
        limit: Optional limit of airfoils to download (useful for tests).
        progress_callback: Optional callback invoked after each successful
            download with ``(index, filename, path)``.

    Returns:
        :class:`DownloadResult` describing saved, skipped and failed downloads.

    Raises:
        AirfoilDownloadError: Raised when the UIUC page cannot be accessed.
    """

    try:  # pragma: no cover - import fallback depends on Python version
        import urllib.request as urllib2
    except ImportError:  # pragma: no cover - Python 2 fallback retained
        import urllib2  # type: ignore[no-redef]

    target_path = Path(target_directory or Path.cwd())
    target_path.mkdir(parents=True, exist_ok=True)

    base_url = "https://m-selig.ae.illinois.edu/ads/"
    index_url = base_url + "coord_database.html"

    try:
        html_page = urllib2.urlopen(index_url)
    except Exception as exc:  # pragma: no cover - network failure path
        raise AirfoilDownloadError(f"Failed to download airfoil index: {exc}") from exc

    soup = BeautifulSoup(html_page, "lxml")
    matches = soup.find_all("a", attrs={"href": re.compile("\\.dat", re.IGNORECASE)})

    saved: List[Path] = []
    skipped: List[Path] = []
    errors: List[Tuple[Path, str]] = []

    for counter, link in enumerate(matches, start=1):
        if limit is not None and counter > limit:
            break

        href = link.get("href")
        if not href:
            continue

        filename = href.rsplit("/", 1)[-1]
        destination = target_path / filename

        if destination.exists() and not overwrite:
            skipped.append(destination)
            continue

        try:
            urllib2.urlretrieve(base_url + href, os.fspath(destination))
        except Exception as exc:  # pragma: no cover - depends on network failures
            logger.warning("Failed to download %s: %s", filename, exc)
            errors.append((destination, str(exc)))
            continue

        saved.append(destination)
        if progress_callback:
            progress_callback(counter, filename, destination)

    return DownloadResult(saved=saved, skipped=skipped, errors=errors)


def refresh_local_airfoil_directory(
    data_path: str | os.PathLike[str],
    *,
    overwrite: bool = False,
    limit: int | None = None,
    progress_callback: Callable[[int, str, Path], None] | None = None,
) -> DownloadResult:
    """High-level convenience wrapper around :func:`get_save_airfoils`."""

    result = get_save_airfoils(
        data_path,
        overwrite=overwrite,
        limit=limit,
        progress_callback=progress_callback,
    )

    for _, path in _iter_airfoil_files(Path(data_path)):
        logger.debug("Local airfoil available: %s", path)

    return result


if __name__ == "__main__":  # pragma: no cover - utility execution helper
    target = Path.cwd()
    summary = get_save_airfoils(target)
    print(
        f"Downloaded {len(summary.saved)} airfoils, "
        f"skipped {len(summary.skipped)}, "
        f"errors: {len(summary.errors)}"
    )
