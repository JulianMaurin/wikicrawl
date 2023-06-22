# Quick start

## Run the docker compose instance locally

### Requirement

- `docker`,
- `docker-compose`
- `make`

__Nb: Managing docker as a non-root user is required (see: [Docker post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/)).__

### Steps

- [Generate stub data](/doc/services/stub.md#run-stub-data-generation)
- [Build and start the local instance](/doc/dockerCompose.md#manage-the-instance)
- [Create a crawling task](/doc/services/workers.md#create-task)
- [Monitore the pipeline execution](/doc/services/monitoring.md#dashboard)
- [Explore the data](/doc/services/database.md#representation)
