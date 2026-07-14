import argparse
import os
import sys
from pathlib import Path

import readchar

# Allow direct execution from a source checkout as well as installed console use.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from create_app.engine.ui.user_interface import InitUI
from create_app.engine.prompts import BuildPrompts
import create_app.constants as const
from create_app.initializer.controller import Controller 
from create_app.path_config import PathConfig

class AppEngine(InitUI):
    """Coordinates the two public channels: flag-driven CLI and interactive UI."""

    def __init__(self):
        super().__init__(const.APP_NAME, const.__version__)
        self.prompter = BuildPrompts(self, const)
        self.infra_keys = ["docker", "jenkins", "k8s", ".github", "db"]
        self.domain_folders = [f.lower() for f in const.ALL_CUSTOM_FOLDERS if f.lower() not in self.infra_keys]
        # The manifest is the hand-off contract between the UI/CLI and Controller.
        self.manifest = { 
            "infra_suites": [], 
            "infra_files": {}, 
            "init_strategy": {},
            "is_drf": False 
        } 

    def _setup_parser(self):
        """Defines the CLI command structure with high-performance overrides."""
        parser = argparse.ArgumentParser(description=f"{const.APP_NAME} - Advanced Project Engine")
        
        # Identity & Version
        parser.add_argument("name", nargs="?", help="Project name")
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {const.__version__}")
        parser.add_argument("--output-dir", help="Directory where the project folder is created. Defaults to ~/Documents.")
        parser.add_argument("--here", action="store_true", help="Create the project in the current working directory.")
        parser.add_argument("--path-behavior", choices=["documents", "current", "custom"], help="One-off path behavior for this project.")
        parser.add_argument("--set-default-path-behavior", choices=["documents", "current", "custom"], help="Persist the default project path behavior.")
        parser.add_argument("--set-default-output-dir", help="Persist a custom default output directory.")
        parser.add_argument("--show-path-config", action="store_true", help="Show saved path defaults and exit.")
        parser.add_argument("--reset-path-config", action="store_true", help="Reset saved path defaults and exit.")
        
        # Core Configuration
        parser.add_argument("-f", "--framework", choices=const.FRAMEWORKS + const.OTHERS_PROJECT_TYPES, help="Target framework")
        parser.add_argument("-s", "--server", help="Specific server (e.g., uvicorn, gunicorn, hypercorn)")
        parser.add_argument("-t", "--type", choices=["standard", "production", "custom", "auto_config"], dest="strategy", help="Build strategy")
        parser.add_argument("--drf", action="store_true", help="Enable Django Rest Framework (Django only)")
        
        # Architecture Overrides
        parser.add_argument("--folders", nargs="+", help="Manually specify folders (Custom mode only)")
        parser.add_argument("--packages", nargs="+", help="Specify which folders get __init__.py")
        
        # Environment & Database
        parser.add_argument("--db", default="sqlite", help="Database engine (sqlite, postgres, mysql, mongodb)")
        parser.add_argument("--venv", choices=["y", "n"], default="y", help="Enable virtual environment (y/n)")
        
        # Infrastructure Modules
        parser.add_argument("--docker", nargs="+", help="Select Docker files")
        parser.add_argument("--github", nargs="+", help="Select GitHub actions")
        parser.add_argument("--k8s", nargs="+", help="Select Kubernetes manifests")
        parser.add_argument("--jenkins", nargs="+", help="Select Jenkins pipeline files")
        parser.add_argument("--community", nargs="+", help="Select community files")
        parser.add_argument("--package-files", nargs="+", help="Select package metadata files")
        
        return parser

    def start(self):
        """Route the request to the CLI channel or the interactive channel."""
        parser = self._setup_parser()
        args = parser.parse_args()

        self._handle_path_config_flags(args)

        if args.name and args.framework:
            self._handle_cli_mode(args)
        else:
            self._handle_interactive_mode()

    def _handle_path_config_flags(self, args):
        """Handle persistent default path behavior flags before project creation."""
        if args.reset_path_config:
            path = PathConfig.reset()
            print(f"Reset path config: {path}")
            sys.exit(0)

        if args.show_path_config:
            print(PathConfig.describe())
            sys.exit(0)

        if args.set_default_path_behavior or args.set_default_output_dir:
            config = PathConfig.load()

            if args.set_default_path_behavior:
                config["path_behavior"] = args.set_default_path_behavior

            if args.set_default_output_dir:
                config["output_dir"] = str(Path(args.set_default_output_dir).expanduser().resolve())
                if not args.set_default_path_behavior:
                    config["path_behavior"] = "custom"

            path = PathConfig.save(config)
            print(f"Saved path config: {path}")
            print(PathConfig.describe())

            if not args.name:
                sys.exit(0)

    def _handle_cli_mode(self, args):
        """Processes logic based on CLI flags with full Django-aware support."""
        fw_slug = args.framework.lower()
        strategy = args.strategy or "standard"
        p_name = args.name
        
        # Convert optional flag groups into a single infrastructure manifest.
        infra_map = {
            "docker": args.docker,
            "github": args.github,
            "kubernetes": args.k8s,
            "jenkins": args.jenkins,
            "community": args.community,
            "pkg": args.package_files,
        }
        for key, files in infra_map.items():
            if files:
                self.manifest["infra_suites"].append(key)
                self.manifest["infra_files"][key] = files

        # Custom mode respects explicit folder lists; other modes use defaults.
        if strategy == "custom" and args.folders:
            selected_folders = args.folders
        else:
            selected_folders = self.prompter.get_smart_folders(fw_slug, strategy, self.domain_folders)

        # The init strategy decides which generated folders become Python packages.
        if strategy == "custom" and args.packages is not None:
            init_map = {folder: (folder in args.packages) for folder in selected_folders}
        else:
            init_map = {folder: True for folder in selected_folders}

        self.manifest.update({
            "project name": p_name,
            "core blueprint": f"{fw_slug} ({args.server or 'default'})",
            "fw_name": fw_slug, 
            "is_drf": args.drf,
            "build strategy": strategy,
            "environment": "venv" if args.venv == "y" else "no venv",
            "apps": "none", 
            "database": args.db or "sqlite",
            "venv_enabled": args.venv == "y",
            "app_name": "core_app",
            "init_strategy": init_map,
            "output_dir": args.output_dir,
            "create_in_current_dir": args.here,
            "path_behavior": args.path_behavior,
        })
        
        mission = Controller(self.manifest, list(selected_folders))
        mission.run_mission()

    def _handle_interactive_mode(self):
        """Interactive flow utilizing the High-Performance UI layer."""
        try:
            selected_folders = set()
            fw_display, _ = self.menu("core blueprint", const.FRAMEWORKS, sub_mapping=const.FRAMEWORK_SERVER_MAPPING, flow=["blueprint"])
            fw_slug = fw_display.split(" (")[0].lower()
            
            # The menu label carries the DRF choice, so normalize it into the manifest.
            self.manifest["is_drf"] = "rest framework" in fw_display.lower()

            if fw_slug == "others":
                project_type_display, _ = self.menu("engine type", const.OTHERS_PROJECT_TYPES, flow=["others"])
                fw_slug = project_type_display.lower()

            mode_raw, _ = self.menu("build strategy", const.PROJECT_MODES, flow=[fw_slug, "mode"])
            mode = mode_raw.lower()
            
            # The following choices become the generation context passed to Controller.
            db_raw, _ = self.menu("data nexus", const.DB_ENGINES, flow=[fw_slug, mode, "database"])
            db = db_raw.lower()
            
            if mode == "auto_config":
                env_display, _ = self.menu("environment", ["venv (recommended)", "no venv"], flow=[fw_slug, mode, "env"])
                p_name = self.prompter.get_project_name()
                apps_list = [] 
                selected_folders = self.prompter.get_smart_folders(fw_slug, "standard", self.domain_folders)
                self.manifest["init_strategy"] = {f: True for f in selected_folders}
            else:
                selected_folders = self._orchestrate_infra(fw_slug, mode)
                env_display, _ = self.menu("environment", ["venv (recommended)", "no venv"], flow=[fw_slug, mode, "env"])
                p_name, apps_list = self.prompter.collect_identity(fw_slug, mode)

            self.manifest.update({
                    "project name": p_name,
                    "core blueprint": fw_display,
                    "fw_name": fw_slug, 
                    "build strategy": mode,
                    "environment": env_display,
                    "apps": ", ".join(apps_list) if apps_list else "none", 
                    "app_name": apps_list[0] if apps_list else "core_app",
                    "database": db,
                    "venv_enabled": "no venv" not in env_display.lower(),
                })

            self._run_mission_control(fw_slug, p_name, mode, selected_folders)

        except (KeyboardInterrupt, EOFError):
            self.exit_gracefully()
        except Exception as e:
            self.cfg.write(f"\n  {self.cfg.C['accent']}✖ critical engine error: {self.cfg.C['white']}{str(e).lower()}")
            sys.exit(1)

    def _orchestrate_infra(self, fw, mode):
        """Handles manual infrastructure selection logic."""
        f_list = [fw, mode, "infra"]
        if mode == "custom":
            selected_dirs, init_map = self.architect(self.domain_folders, flow=[fw, "architect"])
            self.manifest["init_strategy"] = init_map
        else:
            selected_dirs = self.prompter.get_smart_folders(fw, mode, self.domain_folders)
            self.manifest["init_strategy"] = {d: True for d in selected_dirs}

        infra_options = [("docker", const.DOCKER_SUITE), ("jenkins", const.JENKINS_SUITE), ("github", const.GITHUB_SUITE)]
        if mode in ["production", "custom"]:
            infra_options.extend([
                ("community", const.COMMUNITY_CORE),
                ("pkg", const.PACKAGE_FILES),
                ("kubernetes", const.K8S_FILES),
            ])

        for key, suite in infra_options:
            res = self.checklist("infra forge", key, suite, flow=f_list)
            if res:
                self.manifest["infra_suites"].append(key)
                self.manifest["infra_files"][key] = list(res)
        return selected_dirs

    def _run_mission_control(self, fw, p_name, mode, folders):
        """Final summary matrix and execution trigger."""
        c = self.cfg.C
        self.header("mission control", "success")
        infra_total = sum(len(f) for f in self.manifest['infra_files'].values())
        db_clean = self.manifest['database'].split(' ')[0]
        
        # High-performance buffered write for the matrix
        matrix = [
            f"  {c['muted']}┌──────────────────────────────────────────┐",
            f"  {c['muted']}│ {c['white']}NAME  : {c['primary']}{p_name[:12].ljust(12)} {c['white']}ENGINE: {c['primary']}{fw[:10].ljust(10)} {c['muted']}│",
            f"  {c['muted']}│ {c['white']}MODE  : {c['primary']}{mode[:12].ljust(12)} {c['white']}DB    : {c['primary']}{db_clean[:10].ljust(10)} {c['muted']}│",
            f"  {c['muted']}│ {c['white']}DIRS  : {c['primary']}{str(len(folders)).ljust(12)} {c['white']}DRF   : {c['primary']}{str(self.manifest['is_drf']).ljust(10)} {c['muted']}│",
            f"  {c['muted']}└──────────────────────────────────────────┘"
        ]
        self.cfg.write("\n".join(matrix))

        sys.stdout.write(f"\n  {c['success']}? {c['white']}Initialize build sequence? (y/n): ")
        sys.stdout.flush()

        if readchar.readkey().lower() == 'y':
            self.cfg.write(f"{c['success']}yes")
            self.finalize(p_name)
            mission = Controller(self.manifest, list(folders))
            mission.run_mission()
        else:
            self.cfg.write(f"{c['accent']}no\n  {c['muted']}build cancelled.")
            sys.exit(0)

def main():
    """Entry point for the console script."""
    try:
        engine = AppEngine()
        engine.start()
    except KeyboardInterrupt:
        print("\n  Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
