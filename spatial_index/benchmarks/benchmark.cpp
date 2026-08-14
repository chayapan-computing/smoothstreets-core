#include "rtree_index.hpp"

#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>

using namespace smoothstreets;

namespace {

double random_double(std::mt19937& gen, double min, double max) {
    std::uniform_real_distribution<double> dist(min, max);
    return dist(gen);
}

Item make_item(int id, std::mt19937& gen) {
    Item item;
    item.id = "item_" + std::to_string(id);
    double cx = random_double(gen, 0.0, 10000.0);
    double cy = random_double(gen, 0.0, 10000.0);
    double size = random_double(gen, 1.0, 10.0);
    item.min_x = cx - size;
    item.min_y = cy - size;
    item.max_x = cx + size;
    item.max_y = cy + size;
    return item;
}

} // anonymous namespace

int main(int argc, char* argv[]) {
    std::size_t n = 100000;
    if (argc >= 2) {
        n = std::stoul(argv[1]);
    }

    RTreeIndex index;
    std::mt19937 gen(42);

    auto t0 = std::chrono::steady_clock::now();
    for (std::size_t i = 0; i < n; ++i) {
        index.insert(make_item(static_cast<int>(i), gen));
    }
    auto t1 = std::chrono::steady_clock::now();
    double ingest_ms = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count() / 1000.0;
    double ingest_rate = (n / (ingest_ms / 1000.0));

    std::cout << "Ingested " << n << " items in " << ingest_ms << " ms\n";
    std::cout << "Ingestion rate: " << ingest_rate << " entries/sec\n";

    Box query_box(Point(4000.0, 4000.0), Point(6000.0, 6000.0));
    auto rq = index.range_query(query_box);
    std::cout << "Range query: " << rq.items.size() << " hits in " << rq.elapsed_us << " us\n";

    Point query_point(5000.0, 5000.0);
    auto nn = index.nearest_neighbor(query_point, 10);
    std::cout << "Nearest neighbor (k=10): " << nn.items.size() << " results in "
              << nn.elapsed_us << " us\n";

    RTreeIndex other;
    std::mt19937 gen2(123);
    for (std::size_t i = 0; i < n / 10; ++i) {
        other.insert(make_item(static_cast<int>(i), gen2));
    }
    auto join = index.spatial_join(other);
    std::cout << "Spatial join: " << join.pairs.size() << " pairs in " << join.elapsed_us
              << " us\n";

    return 0;
}
