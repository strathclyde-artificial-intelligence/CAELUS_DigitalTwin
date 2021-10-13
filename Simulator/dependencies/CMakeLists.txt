# CAELUS FDM Dependency
FetchContent_Declare(
        caelus_fdm
        GIT_REPOSITORY "https://github.com/strath-ace-labs/UAV-6dof-GNC.git"
        GIT_TAG "adff40a75ee3c250e700b689bbf8014c959b0271"
        SOURCE_SUBDIR CAELUS_FDM
)
add_subdirectory(caelus_fdm)