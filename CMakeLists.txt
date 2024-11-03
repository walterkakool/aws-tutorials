cmake_minimum_required(VERSION 3.3)
project(DeleteAll)

add_definitions(-w)

set   ( HOME_PATH_ROOT              ${CMAKE_CURRENT_SOURCE_DIR} )
set   ( CMAKE_CXX_STANDARD          11 )
set   ( CMAKE_CXX_STANDARD_REQUIRED true )
#set   ( CMAKE_PREFIX_PATH        "${HOME_PATH_ROOT}/AWSInstalls" )

find_package(
                aws-lambda-runtime
                REQUIRED
                #PATHS
                #"${HOME_PATH_ROOT}/AWSInstalls"
)

#find_package( AWSSDK REQUIRED )

add_library   (
                 project_includes_libraries
                 ${HOME_PATH_ROOT}/runner.cpp
)

add_executable(
                 runner
                 ${HOME_PATH_ROOT}/runner.cpp
)

target_include_directories(
                             project_includes_libraries
                             PUBLIC include
                             "${HOME_PATH_ROOT}"
                             "${HOME_PATH_ROOT}/aws-lambda-cpp/include"
)

install(
          TARGETS
          project_includes_libraries
          DESTINATION
          "${HOME_PATH_ROOT}"
)

target_link_libraries(
                       project_includes_libraries
                       AWS::aws-lambda-runtime

)

target_link_libraries(
                        runner
                        project_includes_libraries
)
