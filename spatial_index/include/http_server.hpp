#ifndef SMOOTHSTREETS_HTTP_SERVER_HPP
#define SMOOTHSTREETS_HTTP_SERVER_HPP

#include "rtree_index.hpp"

#include <atomic>
#include <cstdint>
#include <functional>
#include <string>
#include <thread>
#include <unordered_map>

namespace smoothstreets {

using Handler = std::function<std::string(const std::string& body)>;

class HttpServer {
public:
    explicit HttpServer(RTreeIndex& index, uint16_t port = 8080);
    ~HttpServer();

    void start();
    void stop();
    bool running() const;

private:
    void register_routes();
    std::string route(const std::string& method,
                      const std::string& path,
                      const std::string& body) const;

    RTreeIndex& index_;
    uint16_t port_{8080};
    std::atomic<bool> running_{false};
    std::thread thread_;
    std::unordered_map<std::string, Handler> handlers_;
};

} // namespace smoothstreets

#endif // SMOOTHSTREETS_HTTP_SERVER_HPP
