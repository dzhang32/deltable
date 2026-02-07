import shutil
import subprocess
from pathlib import Path

from deltable.error import RtfToHtmlConversionError


def is_soffice_available() -> bool:
    """Return True when the `soffice` command is available on PATH."""
    return shutil.which("soffice") is not None


def convert_rtf_to_html(input_path: Path, output_dir: Path) -> Path:
    """Convert one RTF file to HTML using LibreOffice's `soffice` CLI."""
    if not is_soffice_available():
        raise RtfToHtmlConversionError(
            "soffice is not installed or not available on PATH.",
        )

    if not input_path.exists():
        raise RtfToHtmlConversionError(f"RTF input file does not exist: {input_path}")

    if input_path.suffix.lower() != ".rtf":
        raise RtfToHtmlConversionError(
            f"Expected an .rtf input file, got: {input_path.name}",
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "soffice",
        "--headless",
        "--convert-to",
        "html",
        "--outdir",
        str(output_dir),
        str(input_path),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise RtfToHtmlConversionError(f"soffice failed with exit code {completed.returncode}.")

    output_path = output_dir / f"{input_path.stem}.html"

    return output_path
