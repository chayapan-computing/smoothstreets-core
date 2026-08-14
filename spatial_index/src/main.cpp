#include "http_server.hpp"
#include "rtree_index.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    uint16_t port = 8080;
    if (argc >= 2) {
        port = static_cast<uint16_t>(std::stoul(argv[1]));
    }
    if (const char* env_port = std::getenv("SMOOTHSTREETS_PORT")) {
        port = static_cast<uint16_t>(std::stoul(env_port));
    }

    smoothstreets::RTreeIndex index;
    smoothstreets::HttpServer server(index, port);
    server.start();

    std::cout << "smoothstreets spatial_index server listening on port " << port << "\n";
    std::cout << "Press Enter to stop...\n";
    std::cin.get();

    server.stop();
    return 0;
}
