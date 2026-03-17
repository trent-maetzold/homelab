set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

unraid_appdata_root := "/mnt/user/appdata"
unraid_stacks_root := "/mnt/user/stacks"

default:
    @just --list

sync host='unraid':
    @just sync-configs {{ host }}
    @just sync-stacks {{ host }}

sync-config service host='unraid':
    @tar -C config/{{ service }} -cf - . | ssh {{ host }} 'mkdir -p {{ unraid_appdata_root }}/{{ service }} && tar -C {{ unraid_appdata_root }}/{{ service }} -xf -'

sync-configs host='unraid':
    @for service_dir in config/*; do \
      service="$${service_dir#config/}"; \
      just sync-config "$${service}" {{ host }}; \
    done

sync-stacks host='unraid':
    @ssh {{ host }} 'mkdir -p {{ unraid_stacks_root }}'
    @rsync -av --delete stacks/ {{ host }}:{{ unraid_stacks_root }}/
