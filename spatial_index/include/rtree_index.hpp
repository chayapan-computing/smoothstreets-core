#ifndef SMOOTHSTREETS_RTREE_INDEX_HPP
#define SMOOTHSTREETS_RTREE_INDEX_HPP

#include <boost/geometry.hpp>
#include <boost/geometry/index/rtree.hpp>
#include <cstdint>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace smoothstreets {

namespace bg = boost::geometry;
namespace bgi = boost::geometry::index;

using Point = bg::model::point<double, 2, bg::cs::cartesian>;
using Box = bg::model::box<Point>;
using Value = std::pair<Box, std::string>;
using RTree = bgi::rtree<Value, bgi::quadratic<16>>;

struct Item {
    std::string id;
    double min_x;
    double min_y;
    double max_x;
    double max_y;
    std::string payload;
};

struct QueryResult {
    std::vector<Item> items;
    long long elapsed_us{0};
};

struct JoinResult {
    std::vector<std::pair<std::string, std::string>> pairs;
    long long elapsed_us{0};
};

class RTreeIndex {
public:
    RTreeIndex() = default;

    bool insert(const Item& item);
    bool update(const std::string& id, const Box& new_box);
    bool remove(const std::string& id);
    std::optional<Item> get(const std::string& id) const;

    QueryResult range_query(const Box& box) const;
    QueryResult nearest_neighbor(const Point& point, std::size_t k) const;
    JoinResult spatial_join(const RTreeIndex& other) const;

    std::size_t size() const;

private:
    mutable std::mutex mutex_;
    RTree rtree_;
    std::unordered_map<std::string, Value> registry_;
};

} // namespace smoothstreets

#endif // SMOOTHSTREETS_RTREE_INDEX_HPP
