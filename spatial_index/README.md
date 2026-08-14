# smoothstreets spatial_index subsystem

A lightweight C++ spatial database subsystem built around Boost.Geometry's R-Tree. It provides a REST/JSON API for data management and spatial queries.

## Components

- `RTreeIndex` — thread-safe R-Tree wrapper over Boost.Geometry.
- `HttpServer` — minimal POSIX-socket HTTP server exposing a JSON API.
- `spatial_index_server` — runnable server binary.
- `spatial_index_benchmark` — ingestion and query benchmark.
- `spatial_index_test` — unit tests.

## Build

Requirements:
- C++17 compiler
- CMake >= 3.16
- Boost >= 1.70 (header-only `boost::geometry` is sufficient)
- POSIX sockets / pthreads

On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libboost-all-dev
```

Build:

```bash
cd spatial_index
mkdir -p build && cd build
cmake ..
cmake --build . -j$(nproc)
```

## Run the server

Default port is `8080`:

```bash
./spatial_index_server
```

Specify a port on the command line:

```bash
./spatial_index_server 18080
```

Or set the environment variable:

```bash
SMOOTHSTREETS_PORT=18080 ./spatial_index_server
```

## API

All endpoints return JSON.

### Data Management

**Insert**
```bash
curl -s -X POST http://127.0.0.1:8080/insert \
  -d '{"id":"a","min_x":0,"min_y":0,"max_x":1,"max_y":1}'
```

**Update**
```bash
curl -s -X POST http://127.0.0.1:8080/update \
  -d '{"id":"a","min_x":10,"min_y":10,"max_x":11,"max_y":11}'
```

**Delete**
```bash
curl -s -X POST http://127.0.0.1:8080/delete -d '{"id":"a"}'
```

### Queries

**Range query**
```bash
curl -s -X POST http://127.0.0.1:8080/range_query \
  -d '{"min_x":0.5,"min_y":0.5,"max_x":2,"max_y":2}'
```

**Nearest neighbor**
```bash
curl -s -X POST http://127.0.0.1:8080/nearest_neighbor \
  -d '{"x":0,"y":0,"k":5}'
```

**Spatial join** (joins the index against itself)
```bash
curl -s -X POST http://127.0.0.1:8080/spatial_join
```

### Health

```bash
curl -s http://127.0.0.1:8080/health
```

## Benchmark

```bash
./spatial_index_benchmark 100000
```

Example output on a modern x86-64 host:

```
Ingested 100000 items in 4482.57 ms
Ingestion rate: 22308.6 entries/sec
Range query: 3973 hits in 1627 us
Nearest neighbor (k=10): 10 results in 136 us
Spatial join: 5372 pairs in 682410 us
```

## Test

```bash
ctest --output-on-failure
```

## Architecture notes

- The R-Tree stores `(bounding_box, id)` pairs and supports insert, remove, update, range queries, nearest-neighbor queries, and spatial joins.
- A registry map keeps the current value for each id so updates and deletes can efficiently remove the old bounding box from the tree.
- All index operations are protected by a mutex, making the server safe for concurrent requests.
- The HTTP server is intentionally minimal (no external HTTP library dependency) to keep the subsystem self-contained.
