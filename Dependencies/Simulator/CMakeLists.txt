cmake_minimum_required(VERSION 3.15)
include(FetchContent)

project(Sim6DOF VERSION 0.0.1)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Debug)

#add_definitions("-Wall -Wextra -O0")

file(GLOB_RECURSE src ./src/*.cc)

add_executable(6dof ${src})
add_library(6dof_lib ${src})

configure_file(${PROJECT_SOURCE_DIR}/src/Sim6DOFInfo.h.in ${PROJECT_SOURCE_DIR}/src/Sim6DOFInfo.h)
target_include_directories(6dof PUBLIC
                           ${PROJECT_BINARY_DIR}
                           )
add_definitions( -DCURL_STATICLIB )
# Eigen Headers
include_directories(PUBLIC "/usr/local/Cellar/eigen/3.3.9/include/eigen3/")
# MAVLink headers
target_include_directories(6dof PUBLIC ${CMAKE_SOURCE_DIR}/mavlink/standard/)
target_include_directories(6dof_lib PUBLIC ${CMAKE_SOURCE_DIR}/mavlink/standard/)

find_package(Boost COMPONENTS thread chrono REQUIRED)
find_package (Eigen3 3.3 REQUIRED NO_MODULE)
include_directories(${Boost_INCLUDE_DIRS})

target_link_libraries(6dof PUBLIC Eigen3::Eigen ${Boost_LIBRARIES} curl)

# Vertical Takeoff Example 
file(GLOB_RECURSE vertical_takeoff_example Examples/vertical_takeoff_example.cc)

add_executable(vertical_takeoff_example ${vertical_takeoff_example})
target_include_directories(vertical_takeoff_example PUBLIC ${CMAKE_SOURCE_DIR}/mavlink/standard/)
target_link_libraries(vertical_takeoff_example PUBLIC 6dof_lib Eigen3::Eigen ${Boost_LIBRARIES} curl)

# Manoeuvre plan Example 
file(GLOB_RECURSE manouvre_plan_example Examples/manouvre_plan_example.cc)

add_executable(manouvre_plan_example ${manouvre_plan_example})
target_include_directories(manouvre_plan_example PUBLIC ${CMAKE_SOURCE_DIR}/mavlink/standard/)
target_link_libraries(manouvre_plan_example PUBLIC 6dof_lib Eigen3::Eigen ${Boost_LIBRARIES} curl)

# RPY Manoeuvre Example 
file(GLOB_RECURSE rpy_maneuvers Examples/rpy_maneuvers.cc)

add_executable(rpy_maneuvers ${rpy_maneuvers})
target_include_directories(rpy_maneuvers PUBLIC ${CMAKE_SOURCE_DIR}/mavlink/standard/)
target_link_libraries(rpy_maneuvers PUBLIC 6dof_lib Eigen3::Eigen ${Boost_LIBRARIES} curl)

file(COPY "Resources/WMM.COF" DESTINATION ${CMAKE_BINARY_DIR})