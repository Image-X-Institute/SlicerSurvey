cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(QualitativeSurvey)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/FelixBenter/SlicerQualitativeSurvey")
set(EXTENSION_CATEGORY "Training")
set(EXTENSION_CONTRIBUTORS "Felix Benter (The University of Sydney)")
set(EXTENSION_DESCRIPTION "An extension for Slicer that allows it to import, run questionnaires and export the user responses. ")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/FelixBenter/SlicerQualitativeSurvey/main/QualitativeSurvey/QualitativeSurvey.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/FelixBenter/SlicerQualitativeSurvey/main/Screenshot1.png, https://raw.githubusercontent.com/FelixBenter/SlicerQualitativeSurvey/main/Screenshot2.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SurveyLoader)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
