import textwrap
from pathlib import Path
from string import Template

files_dir = Path(__file__).parent / "dev"

with open(files_dir / "sops", 'r') as f:
    secret = f.read()

with open(files_dir / "conf_sops.yaml", 'r') as f:
    conf_sops = f.read()

with open(files_dir / "conf_vw.yaml", 'r') as f:
    conf_src_vw = f.read()

with open(files_dir / "conf_dav.yaml", 'r') as f:
    conf_src_dav = f.read()

with open("manifest.template.yaml", 'r') as f:
    tpl = Template(f.read())
    manifest = tpl.substitute({
        "SECRET": secret,
        "SOPS_CONF": textwrap.indent(conf_sops, "    "),
        "BACKUPSTER_CONF_VW": textwrap.indent(conf_src_vw, "    "),
        "BACKUPSTER_CONF_DAV": textwrap.indent(conf_src_dav, "    ")
    })

with open("manifest.yaml", "w") as f:
    f.write(manifest)