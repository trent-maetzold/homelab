#!/usr/bin/env python3
"""Render the Helm releases assembled by Kustomize; no cluster required."""
import pathlib
import subprocess
import sys
import tempfile

import yaml


def run(*args):
    return subprocess.check_output(args, text=True)


output = pathlib.Path(sys.argv[1])
output.mkdir(parents=True, exist_ok=True)
objects = list(yaml.safe_load_all(run('kubectl', 'kustomize', 'apps/media')))
configs = {(o['metadata']['namespace'], o['metadata']['name']): o['data']
           for o in objects if o['kind'] == 'ConfigMap'}
sources = {(o['metadata']['namespace'], o['metadata']['name']): o['spec']
           for o in objects if o['kind'] == 'OCIRepository'}
releases = [o for o in objects if o['kind'] == 'HelmRelease']
if not releases:
    raise SystemExit('No media HelmReleases found')

with tempfile.TemporaryDirectory() as temp:
    temp = pathlib.Path(temp)
    charts = {}
    for release in releases:
        namespace = release['metadata']['namespace']
        spec = release['spec']
        ref = spec['chartRef']
        if ref['kind'] != 'OCIRepository':
            raise SystemExit(f'Unsupported chart reference: {ref}')
        source = sources[(ref.get('namespace', namespace), ref['name'])]
        uri = source['url'] + '@' + source['ref']['digest']
        if uri not in charts:
            folder = temp / str(len(charts))
            folder.mkdir()
            subprocess.run(['helm', 'pull', uri, '--destination', folder], check=True)
            charts[uri], = folder.glob('*.tgz')
        args = []
        for index, values_ref in enumerate(spec.get('valuesFrom', [])):
            if values_ref['kind'] != 'ConfigMap' or 'targetPath' in values_ref:
                raise SystemExit(f'Unsupported values reference: {values_ref}')
            data = configs[(namespace, values_ref['name'])]
            values = temp / f'values-{index}.yaml'
            values.write_text(data[values_ref.get('valuesKey', 'values.yaml')])
            args.extend(['-f', str(values)])
        inline = temp / 'inline.yaml'
        inline.write_text(yaml.safe_dump(spec.get('values', {})))
        name = spec['releaseName']
        rendered = run('helm', 'template', name, str(charts[uri]),
                       '--namespace', namespace, '--kube-version', '1.36.0',
                       *args, '-f', str(inline))
        (output / f'{name}.yaml').write_text(rendered)
        print(f'Rendered {namespace}/{name}')
