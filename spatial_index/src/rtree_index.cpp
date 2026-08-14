#include "rtree_index.hpp"

#include <chrono>
#include <stdexcept>

namespace smoothstreets {

bool RTreeIndex::insert(const Item& item) {
    std::lock_guard<std::mutex> lock(mutex_);
    Box box(Point(item.min_x, item.min_y), Point(item.max_x, item.max_y));
    Value value(box, item.id);
    if (registry_.find(item.id) != registry_.end()) {
        return false;
    }
    rtree_.insert(value);
    registry_[item.id] = value;
    return true;
}

bool RTreeIndex::update(const std::string& id, const Box& new_box) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = registry_.find(id);
    if (it == registry_.end()) {
        return false;
    }
    rtree_.remove(it->second);
    Value new_value(new_box, id);
    rtree_.insert(new_value);
    it->second = new_value;
    return true;
}

bool RTreeIndex::remove(const std::string& id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = registry_.find(id);
    if (it == registry_.end()) {
        return false;
    }
    rtree_.remove(it->second);
    registry_.erase(it);
    return true;
}

std::optional<Item> RTreeIndex::get(const std::string& id) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = registry_.find(id);
    if (it == registry_.end()) {
        return std::nullopt;
    }
    const auto& box = it->second.first;
    const auto& stored_id = it->second.second;
    Item item;
    item.id = stored_id;
    item.min_x = bg::get<bg::min_corner, 0>(box);
    item.min_y = bg::get<bg::min_corner, 1>(box);
    item.max_x = bg::get<bg::max_corner, 0>(box);
    item.max_y = bg::get<bg::max_corner, 1>(box);
    return item;
}

QueryResult RTreeIndex::range_query(const Box& box) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto start = std::chrono::steady_clock::now();
    QueryResult result;
    rtree_.query(bgi::intersects(box), std::back_inserter(result.items));
    auto end = std::chrono::steady_clock::now();
    result.elapsed_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    return result;
}

QueryResult RTreeIndex::nearest_neighbor(const Point& point, std::size_t k) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto start = std::chrono::steady_clock::now();
    QueryResult result;
    rtree_.query(bgi::nearest(point, k), std::back_inserter(result.items));
    auto end = std::chrono::steady_clock::now();
    result.elapsed_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    return result;
}

JoinResult RTreeIndex::spatial_join(const RTreeIndex& other) const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::lock_guard<std::mutex> other_lock(other.mutex_);
    auto start = std::chrono::steady_clock::now();
    JoinResult result;
    for (const auto& value : rtree_) {
        std::vector<Value> matches;
        other.rtree_.query(bgi::intersects(value.first), std::back_inserter(matches));
        for (const auto& match : matches) {
            result.pairs.emplace_back(value.second, match.second);
        }
    }
    auto end = std::chrono::steady_clock::now();
    result.elapsed_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    return result;
}

std::size_t RTreeIndex::size() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return registry_.size();
}

} // namespace smoothstreets
