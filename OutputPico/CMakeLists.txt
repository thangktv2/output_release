cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(conveyer)

pico_sdk_init()

add_subdirectory(freertos)
add_subdirectory(ProjectFiles)