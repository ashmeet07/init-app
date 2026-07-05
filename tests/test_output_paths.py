import json
from pathlib import Path
from create_app.initializer.controller import Controller
from create_app.path_config import PathConfig


def test_default_output_base_prefers_documents():
    assert Controller._default_output_base() == (Path.home() / "Documents").resolve()


def test_output_dir_manifest_controls_project_root(tmp_path):
    manifest = {
        "project name": "path_demo",
        "core blueprint": "fastapi",
        "build strategy": "standard",
        "framework": "fastapi",
        "output_dir": str(tmp_path),
    }

    controller = Controller(manifest, [])

    expected_root = tmp_path.resolve() / "path_demo"
    assert controller.root == expected_root
    assert controller.ctx["project_path"] == str(expected_root)
    assert controller.ctx["output_dir"] == str(tmp_path.resolve())


def test_project_metadata_tracks_paths(tmp_path):
    manifest = {
        "project name": "meta_demo",
        "core blueprint": "fastapi",
        "build strategy": "standard",
        "framework": "fastapi",
        "output_dir": str(tmp_path),
    }
    controller = Controller(manifest, [])
    controller.root.mkdir(parents=True)

    controller._write_project_metadata()

    metadata = json.loads((tmp_path / "meta_demo" / ".init-app.json").read_text())
    assert metadata["project_path"] == str(tmp_path.resolve() / "meta_demo")
    assert metadata["output_dir"] == str(tmp_path.resolve())
    assert metadata["generated_by"] == "init-app"


def test_saved_current_path_behavior_uses_invocation_dir(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("INIT_APP_CONFIG_PATH", str(config_path))
    PathConfig.save({"path_behavior": "current"})
    monkeypatch.chdir(tmp_path)

    controller = Controller(
        {
            "project name": "current_demo",
            "core blueprint": "fastapi",
            "build strategy": "standard",
            "framework": "fastapi",
        },
        [],
    )

    assert controller.root == tmp_path.resolve() / "current_demo"


def test_saved_custom_path_behavior_uses_saved_output_dir(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "apps"
    monkeypatch.setenv("INIT_APP_CONFIG_PATH", str(config_path))
    PathConfig.save({"path_behavior": "custom", "output_dir": str(output_dir)})

    controller = Controller(
        {
            "project name": "custom_demo",
            "core blueprint": "fastapi",
            "build strategy": "standard",
            "framework": "fastapi",
        },
        [],
    )

    assert controller.root == output_dir.resolve() / "custom_demo"


def test_one_off_output_dir_overrides_saved_default(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    saved_output = tmp_path / "saved"
    one_off_output = tmp_path / "one-off"
    monkeypatch.setenv("INIT_APP_CONFIG_PATH", str(config_path))
    PathConfig.save({"path_behavior": "custom", "output_dir": str(saved_output)})

    controller = Controller(
        {
            "project name": "override_demo",
            "core blueprint": "fastapi",
            "build strategy": "standard",
            "framework": "fastapi",
            "output_dir": str(one_off_output),
        },
        [],
    )

    assert controller.root == one_off_output.resolve() / "override_demo"
