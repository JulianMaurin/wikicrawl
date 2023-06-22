# Docker compose

## Local instance

[Docker compose](https://docs.docker.com/compose/) manage the local execution of the pipeline.

The [docker compose configuration](/docker-compose.yaml) reference:

- service docker images and command
- ports mapped to the host
- volume mounted from the host
- environment variable

### Manage the instance

If the pipeline docker images are not built, it's the case if you are running `wikicrawl` for the first time, the [Makefile](/Makefile) provides a command to get the instance runnig easily:

```sh
make buildup
```

Once images are ready, you can manage the instance using the standard docker-compose command:

```sh
docker-compose up 
# [...]
docker-compose down
# [...]
```

Using [lazydocker](https://github.com/jesseduffield/lazydocker) is recommended to monitor the health of the insrance properly.

## Devlopment

Docker compose is also used to enable [testing](/doc/tests.md), building and [stub generation](/doc/services/stub.md) without installing any more dependency.

In this case [another docker compose configuration](/docker-compose.dev.yaml) is used.
