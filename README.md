[![Build Status](https://travis-ci.org/olaurino/rama.svg?branch=master)](https://travis-ci.org/olaurino/rama)
[![Build status](https://ci.appveyor.com/api/projects/status/e5b2u9jtf4yu4iwy?svg=true)](https://ci.appveyor.com/project/olaurino/rama)

[![Maintainability](https://api.codeclimate.com/v1/badges/4e460db47c6c597fd0f6/maintainability)](https://codeclimate.com/github/olaurino/rama/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/4e460db47c6c597fd0f6/test_coverage)](https://codeclimate.com/github/olaurino/rama/test_coverage)

# Overview
Python Package for parsing annotated data files and instantiating instances of VO Data Model Classes.

Currently supports
  * VOTable serializations with
    + VODML Mapping syntax annotation

# Package Contents
 rama/framework
   * VODML Meta-model classes
     + VodmlDescriptor base class
     + Composition class
     + Attribute class
     + Reference class
     + BaseType class
     + InstanceID class
     + Reference Wrapper classes (Single & Row references)
   * model classes are defined in terms of these
   * parser instantiates them

 rama/reader:
   * Base classes for readers
     + Document
     + InstanceRegistry
     + Reader

 rama/reader/votable
   * Reader for VOTable serializations
   * Interprets VOTable and VODML Mapping Syntax to VOTable(Document)
   * Generates instances of VO Data Model classes
   * notes
     + parse_column() extracts column name from FIELD;
     + parse_constant() does NOT do that for PARAM;

 rama/utils
   * TypeRegistry:
       maps VODML type identifiers (vodml-id) to Python Model Classes
   * VO:
       decorator associates Python Class to vodml-id (see Model classes)

 rama/models
   * Class specs for various IVOA Data Models
   * notes
     + test subdirectory is NOT TEST CODE, but rather TEST MODELS

 rama/adapters
   * Adapters translate Model Class instances to some other, 
     presumably more user-friendly, type
   * Act on Model instance, so independent of interpretation code
     So, adapters can be tested separately from the parser stuff.
   * Current adapters
     + coords:Point     -> Astropy SkyCoord
     + coords:TimeStamp -> Astropy Time
     + cube:NDPoint     -> CubePoint with enhanced axes (VOAxis), and associated plotters

 rama/tools
   * TimeSeries class
     + converts Cube to TimeSeries assigning independent 'time' axis
   * plot method
     + plots cube instance as TimeSeries


# Development instructions
## Environment
Developed in conda 'vodml' environment and requires pytest
```
$ conda create -n vodml -c ivoa rama jovial
$ conda activate vodml
$ conda install pytest
```
## Build from git repository
Clone and/or update repository
```
$ git clone https://github.com/mcdittmar/rama
$ git pull origin
$ cd rama
```
Build and install the python module
```
$ python setup.py install
```
Run test suite
```
$ pytest --pyargs rama
```
