# ebanx-challenge

## Requirements

- Docker
- Docker Compose

Check if Docker is installed:

```bash
docker --version
docker compose version
```

---

## Run the project locally

From the root of the project, build the image:

```bash
docker compose build
```

Start the container:

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

---

## Access locally

Once the container is running, the API will be available at:

```
http://localhost:8000
```

Stop the container:

```bash
docker compose down
```

---

## Deployed version (AWS EC2)

The application is available at:

```
http://ec2-54-242-4-186.compute-1.amazonaws.com:8000
```

Swagger documentation:

```
http://ec2-54-242-4-186.compute-1.amazonaws.com:8000/docs
```
