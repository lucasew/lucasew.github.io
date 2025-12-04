---

date: 2025-12-04T00:00:00
title: Setup Nomad com Coolify
summary: Como eu to conseguindo subir o Nomad e integrar com o Traefik do Coolify
---

# Passos

## Configuração extra no Reverse Proxy
- Abra o coolify
- Servers -> $SERVER -> Proxy -> Configuration -> Traefik (Coolify Proxy)
- Em command, cole no fim antes do labels. A ordem na verdade não importa muito mas é nessa lista.

```
- '--providers.nomad=true'
- '--providers.nomad.exposedbydefault=false'
- '--providers.nomad.endpoint.address=http://host.docker.internal:4646'
```

- Reinicia o reverse proxy pra aplicar (Coolify vai avisar)

## Serviço de exemplo.

- É o exemplo hello, só mexi no service.

```hcl
job "hello-world" {
  # Specifies the datacenter where this job should be run
  # This can be omitted and it will default to ["*"]
  datacenters = ["*"]

  meta {
    # User-defined key/value pairs that can be used in your jobs.
    # You can also use this meta block within Group and Task levels.
    foo = "bar"
  }

  # A group defines a series of tasks that should be co-located
  # on the same client (host). All tasks within a group will be
  # placed on the same host.
  group "servers" {

    # Specifies the number of instances of this group that should be running.
    # Use this to scale or parallelize your job.
    # This can be omitted and it will default to 1.
    count = 1

    network {
      port "www" {
        to = 8001
      }
    }

    service {
      provider = "nomad"
      port     = "www"
      tags = [
          "traefik.enable=true",
        	"traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https",
        	"traefik.http.routers.hello-http.entryPoints=http",
        	"traefik.http.routers.hello-http.middlewares=redirect-to-https",
        	"traefik.http.routers.hello-http.rule=Host(`hello.app.lew.tec.br`)", # teu dominio
        	"traefik.http.routers.hello-https.entryPoints=https",
        	"traefik.http.routers.hello-https.tls=true",
        	"traefik.http.routers.hello-https.rule=Host(`hello.app.lew.tec.br`)", # teu dominio dnv
        	"traefik.http.routers.hello-https.tls.certresolver=letsencrypt"
          # TODO: automatizar esse boilerplate?
        ]
    }

    # Tasks are individual units of work that are run by Nomad.
    task "web" {
      # This particular task starts a simple web server within a Docker container
      driver = "docker"

      config {
        image   = "busybox:1"
        command = "httpd"
        args    = ["-v", "-f", "-p", "${NOMAD_PORT_www}", "-h", "/local"]
        ports   = ["www"]
        
      }

      template {
        data        = <<-EOF
                      <h1>Hello, Nomad!</h1>
                      <ul>
                        <li>Task: {{env "NOMAD_TASK_NAME"}}</li>
                        <li>Group: {{env "NOMAD_GROUP_NAME"}}</li>
                        <li>Job: {{env "NOMAD_JOB_NAME"}}</li>
                        <li>Metadata value for foo: {{env "NOMAD_META_foo"}}</li>
                        <li>Currently running on port: {{env "NOMAD_PORT_www"}}</li>
                      </ul>
                      EOF
        destination = "local/index.html"
      }

      # Specify the maximum resources required to run the task
      resources {
        cpu    = 50
        memory = 64
      }
    }
  }
}
```

Ao dar apply já é pra tudo magicamente aparecer.
