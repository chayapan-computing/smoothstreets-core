#include "http_server.hpp"

#include <array>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

// Minimal POSIX socket-based HTTP server
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
using SocketType = SOCKET;
static constexpr SocketType INVALID_SOCKET_VALUE = INVALID_SOCKET;
static int close_socket(SocketType s) { return closesocket(s); }
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
using SocketType = int;
static constexpr SocketType INVALID_SOCKET_VALUE = -1;
static int close_socket(SocketType s) { return close(s); }
#endif

namespace smoothstreets {

namespace {

std::string make_response(int code, const std::string& body) {
    std::ostringstream oss;
    oss << "HTTP/1.1 " << code << " OK\r\n"
        << "Content-Type: application/json\r\n"
        << "Content-Length: " << body.size() << "\r\n"
        << "Connection: close\r\n\r\n"
        << body;
    return oss.str();
}

std::string read_request_body(const std::string& request) {
    auto pos = request.find("\r\n\r\n");
    if (pos == std::string::npos) {
        return "";
    }
    return request.substr(pos + 4);
}

void parse_request_line(const std::string& request,
                        std::string& method,
                        std::string& path) {
    std::istringstream iss(request);
    iss >> method >> path;
}

} // anonymous namespace

HttpServer::HttpServer(RTreeIndex& index, uint16_t port)
    : index_(index), port_(port) {
    register_routes();
}

HttpServer::~HttpServer() {
    stop();
}

void HttpServer::start() {
    if (running_.exchange(true)) {
        return;
    }

#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    thread_ = std::thread([this]() {
        SocketType server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd == INVALID_SOCKET_VALUE) {
            std::cerr << "Failed to create socket\n";
            running_ = false;
            return;
        }

        int opt = 1;
#ifdef _WIN32
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR,
                   reinterpret_cast<const char*>(&opt), sizeof(opt));
#else
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

        sockaddr_in address{};
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(port_);

        if (bind(server_fd, reinterpret_cast<sockaddr*>(&address),
                 sizeof(address)) < 0) {
            std::cerr << "Bind failed on port " << port_ << "\n";
            close_socket(server_fd);
            running_ = false;
            return;
        }

        if (listen(server_fd, 3) < 0) {
            std::cerr << "Listen failed\n";
            close_socket(server_fd);
            running_ = false;
            return;
        }

        while (running_) {
            sockaddr_in client_addr{};
#ifdef _WIN32
            int addrlen = sizeof(client_addr);
#else
            socklen_t addrlen = sizeof(client_addr);
#endif
            SocketType client_fd = accept(server_fd,
                                          reinterpret_cast<sockaddr*>(&client_addr),
                                          &addrlen);
            if (client_fd == INVALID_SOCKET_VALUE) {
                continue;
            }

            std::array<char, 8192> buffer{};
            std::string request;
            ssize_t bytes_read;
            while ((bytes_read = recv(client_fd, buffer.data(), buffer.size(), 0)) > 0) {
                request.append(buffer.data(), bytes_read);
                if (request.find("\r\n\r\n") != std::string::npos) {
                    break;
                }
            }

            std::string method, path;
            parse_request_line(request, method, path);
            std::string body = read_request_body(request);
            std::string response = route(method, path, body);
            send(client_fd, response.data(), static_cast<int>(response.size()), 0);
            close_socket(client_fd);
        }

        close_socket(server_fd);
    });
}

void HttpServer::stop() {
    running_ = false;
    if (thread_.joinable()) {
        thread_.join();
    }
}

bool HttpServer::running() const {
    return running_;
}

void HttpServer::register_routes() {
    handlers_["POST /insert"] = [this](const std::string& body) {
        // Expects JSON: {"id":"a","min_x":0,"min_y":0,"max_x":1,"max_y":1}
        Item item;
        if (sscanf(body.c_str(),
                   "{\"id\":\"%63[^\"]\",\"min_x\":%lf,\"min_y\":%lf,\"max_x\":%lf,\"max_y\":%lf",
                   item.id.data(), &item.min_x, &item.min_y, &item.max_x,
                   &item.max_y) < 5) {
            return make_response(400, "{\"error\":\"invalid payload\"}");
        }
        bool ok = index_.insert(item);
        return make_response(200,
                             ok ? "{\"status\":\"ok\"}" : "{\"status\":\"exists\"}");
    };

    handlers_["POST /update"] = [this](const std::string& body) {
        char id[64] = {};
        double min_x, min_y, max_x, max_y;
        if (sscanf(body.c_str(),
                   "{\"id\":\"%63[^\"]\",\"min_x\":%lf,\"min_y\":%lf,\"max_x\":%lf,\"max_y\":%lf",
                   id, &min_x, &min_y, &max_x, &max_y) < 5) {
            return make_response(400, "{\"error\":\"invalid payload\"}");
        }
        Box new_box(Point(min_x, min_y), Point(max_x, max_y));
        bool ok = index_.update(id, new_box);
        return make_response(200,
                             ok ? "{\"status\":\"ok\"}" : "{\"status\":\"not_found\"}");
    };

    handlers_["POST /delete"] = [this](const std::string& body) {
        char id[64] = {};
        if (sscanf(body.c_str(), "{\"id\":\"%63[^\"]\"", id) < 1) {
            return make_response(400, "{\"error\":\"invalid payload\"}");
        }
        bool ok = index_.remove(id);
        return make_response(200,
                             ok ? "{\"status\":\"ok\"}" : "{\"status\":\"not_found\"}");
    };

    handlers_["POST /range_query"] = [this](const std::string& body) {
        double min_x, min_y, max_x, max_y;
        if (sscanf(body.c_str(),
                   "{\"min_x\":%lf,\"min_y\":%lf,\"max_x\":%lf,\"max_y\":%lf",
                   &min_x, &min_y, &max_x, &max_y) < 4) {
            return make_response(400, "{\"error\":\"invalid payload\"}");
        }
        auto result = index_.range_query(Box(Point(min_x, min_y), Point(max_x, max_y)));
        std::ostringstream oss;
        oss << "{\"elapsed_us\":" << result.elapsed_us << ",\"items\":[";
        for (size_t i = 0; i < result.items.size(); ++i) {
            const auto& it = result.items[i];
            oss << "{\"id\":\"" << it.id << "\","
                << "\"min_x\":" << it.min_x << ",\"min_y\":" << it.min_y << ","
                << "\"max_x\":" << it.max_x << ",\"max_y\":" << it.max_y << "}";
            if (i + 1 < result.items.size()) oss << ",";
        }
        oss << "]}";
        return make_response(200, oss.str());
    };

    handlers_["POST /nearest_neighbor"] = [this](const std::string& body) {
        double x, y;
        std::size_t k;
        if (sscanf(body.c_str(), "{\"x\":%lf,\"y\":%lf,\"k\":%zu", &x, &y, &k) < 3) {
            return make_response(400, "{\"error\":\"invalid payload\"}");
        }
        auto result = index_.nearest_neighbor(Point(x, y), k);
        std::ostringstream oss;
        oss << "{\"elapsed_us\":" << result.elapsed_us << ",\"items\":[";
        for (size_t i = 0; i < result.items.size(); ++i) {
            const auto& it = result.items[i];
            oss << "{\"id\":\"" << it.id << "\","
                << "\"min_x\":" << it.min_x << ",\"min_y\":" << it.min_y << ","
                << "\"max_x\":" << it.max_x << ",\"max_y\":" << it.max_y << "}";
            if (i + 1 < result.items.size()) oss << ",";
        }
        oss << "]}";
        return make_response(200, oss.str());
    };

    handlers_["POST /spatial_join"] = [this](const std::string& body) {
        // For the standalone server, join is performed against itself.
        auto result = index_.spatial_join(index_);
        std::ostringstream oss;
        oss << "{\"elapsed_us\":" << result.elapsed_us << ",\"pairs\":[";
        for (size_t i = 0; i < result.pairs.size(); ++i) {
            const auto& p = result.pairs[i];
            oss << "{\"a\":\"" << p.first << "\",\"b\":\"" << p.second << "\"}";
            if (i + 1 < result.pairs.size()) oss << ",";
        }
        oss << "]}";
        return make_response(200, oss.str());
    };

    handlers_["GET /health"] = [](const std::string&) {
        return make_response(200, "{\"status\":\"ok\"}");
    };
}

std::string HttpServer::route(const std::string& method,
                              const std::string& path,
                              const std::string& body) const {
    std::string key = method + " " + path;
    auto it = handlers_.find(key);
    if (it == handlers_.end()) {
        return make_response(404, "{\"error\":\"not found\"}");
    }
    return it->second(body);
}

} // namespace smoothstreets
