cmake_minimum_required(VERSION 3.16)
project(smoothstreets_spatial_index VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Boost 1.70 REQUIRED)
find_package(Threads REQUIRED)

add_library(spatial_index STATIC
    src/rtree_index.cpp
    src/http_server.cpp
)

target_include_directories(spatial_index
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(spatial_index
    PUBLIC
        Boost::boost
        Threads::Threads
)

add_executable(spatial_index_server src/main.cpp)
target_link_libraries(spatial_index_server PRIVATE spatial_index)

add_executable(spatial_index_benchmark benchmarks/benchmark.cpp)
target_link_libraries(spatial_index_benchmark PRIVATE spatial_index)

enable_testing()
add_executable(spatial_index_test tests/test_rtree.cpp)
target_link_libraries(spatial_index_test PRIVATE spatial_index)
add_test(NAME spatial_index_test COMMAND spatial_index_test)
