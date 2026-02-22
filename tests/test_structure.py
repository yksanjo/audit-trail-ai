from pathlib import Path


def test_project_has_core_artifacts():
    assert Path('README.md').exists()
    assert Path('SECURITY.md').exists()
