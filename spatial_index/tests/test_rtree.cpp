#include "rtree_index.hpp"

#include <cassert>
#include <iostream>

using namespace smoothstreets;

void test_insert_and_get() {
    RTreeIndex index;
    Item item{"a", 0.0, 0.0, 1.0, 1.0};
    assert(index.insert(item));
    assert(index.size() == 1);
    auto got = index.get("a");
    assert(got.has_value());
    assert(got->id == "a");
    assert(got->min_x == 0.0);
    assert(got->max_x == 1.0);
    std::cout << "test_insert_and_get passed\n";
}

void test_update() {
    RTreeIndex index;
    index.insert({"a", 0.0, 0.0, 1.0, 1.0});
    Box new_box(Point(2.0, 2.0), Point(3.0, 3.0));
    assert(index.update("a", new_box));
    auto got = index.get("a");
    assert(got->min_x == 2.0);
    std::cout << "test_update passed\n";
}

void test_delete() {
    RTreeIndex index;
    index.insert({"a", 0.0, 0.0, 1.0, 1.0});
    assert(index.remove("a"));
    assert(index.size() == 0);
    std::cout << "test_delete passed\n";
}

void test_range_query() {
    RTreeIndex index;
    index.insert({"a", 0.0, 0.0, 1.0, 1.0});
    index.insert({"b", 5.0, 5.0, 6.0, 6.0});
    auto result = index.range_query(Box(Point(0.5, 0.5), Point(2.0, 2.0)));
    assert(result.items.size() == 1);
    assert(result.items[0].id == "a");
    std::cout << "test_range_query passed\n";
}

void test_nearest_neighbor() {
    RTreeIndex index;
    index.insert({"a", 0.0, 0.0, 1.0, 1.0});
    index.insert({"b", 10.0, 10.0, 11.0, 11.0});
    auto result = index.nearest_neighbor(Point(0.0, 0.0), 1);
    assert(result.items.size() == 1);
    assert(result.items[0].id == "a");
    std::cout << "test_nearest_neighbor passed\n";
}

void test_spatial_join() {
    RTreeIndex a;
    a.insert({"a1", 0.0, 0.0, 2.0, 2.0});
    RTreeIndex b;
    b.insert({"b1", 1.0, 1.0, 3.0, 3.0});
    auto result = a.spatial_join(b);
    assert(result.pairs.size() == 1);
    assert(result.pairs[0].first == "a1");
    assert(result.pairs[0].second == "b1");
    std::cout << "test_spatial_join passed\n";
}

int main() {
    test_insert_and_get();
    test_update();
    test_delete();
    test_range_query();
    test_nearest_neighbor();
    test_spatial_join();
    std::cout << "All tests passed.\n";
    return 0;
}
