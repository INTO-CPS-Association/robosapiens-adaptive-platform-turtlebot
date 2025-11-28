cmake_minimum_required(VERSION 3.8)
project(rviz_plugin)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_ros REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rviz_common REQUIRED)
find_package(spin_interfaces REQUIRED)

set(CMAKE_AUTOMOC ON)
qt5_wrap_cpp(MOC_FILES
  include/rviz_plugin/rviz_panel.hpp
)

add_library(spin_panel src/rviz_panel.cpp ${MOC_FILES})
target_include_directories(spin_panel PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_include_directories(spin_panel SYSTEM PRIVATE
  ${CMAKE_SOURCE_DIR}/../3rdparties/frozen/include
)
ament_target_dependencies(spin_panel
  pluginlib
  rviz_common
  spin_interfaces
)
install(TARGETS spin_panel
        EXPORT export_rviz_plugin
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
)
install(DIRECTORY include/
        DESTINATION include
)
install(FILES rviz_common_plugins.xml
        DESTINATION share/${PROJECT_NAME}
)
install(FILES icons/classes/SpinPanel.png
        DESTINATION share/${PROJECT_NAME}/icons/classes
)
ament_export_include_directories(include)
ament_export_targets(export_rviz_plugin)
pluginlib_export_plugin_description_file(rviz_common rviz_common_plugins.xml)

ament_package()
