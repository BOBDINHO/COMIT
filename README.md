CubeSat Center of Gravity Configuration Tool

A desktop application for defining a CubeSat component stack, evaluating its center of gravity, and searching for component arrangements that satisfy geometric and CG constraints.

This repository represents the starting point of the project. The current version provides a functional Python/Tkinter prototype that can be expanded into a more flexible CubeSat configuration and mechanical-layout tool.



Project Context

This project was developed by Eduardo Miguel Dias da Silva, a Mechanical Engineering student at the Faculty of Engineering of the University of Porto (FEUP), in the context of the Porto Space Team and the ICARUS 1U CubeSat project.

The initial objective is to support the preliminary arrangement of CubeSat components by:

defining internal and external components;

assigning masses, dimensions, and local center-of-mass positions;

imposing minimum and maximum distances between internal components;

calculating the overall CubeSat center of gravity;

searching for a valid component arrangement within a target CG interval;

saving and loading configurations through JSON files.

Current Starting Point

The current application is a single-file prototype built with Python and Tkinter.

It currently supports:

a graphical desktop interface;

English and Portuguese interface text;

dynamic creation and removal of internal components;

dynamic creation and removal of external components;

editable component names;

component mass, thickness, height, and center-of-mass inputs;

minimum and maximum separation constraints between internal component pairs;

a configurable CubeSat total height;

a configurable target CG interval;

JSON configuration import and export;

a recursive configuration search with basic pruning;

display of the best valid configuration and the number of tested iterations;

integration of a CubeSat reference diagram in the interface.

Calculation Principle

For a system with component masses (m_i) and center-of-mass positions (z_i), the overall center of gravity is calculated along the CubeSat longitudinal axis using:

[z_{CG} = \frac{\sum_i m_i z_i}{\sum_i m_i}]

The current prototype treats the CubeSat arrangement as a one-dimensional stack along its height axis.

The first internal component is fixed at the bottom of the CubeSat. The last internal component is fixed relative to the top. Intermediate component positions are obtained by iterating through admissible gaps.

For every candidate arrangement, the application:

calculates the effective center-of-mass position of each component;

checks the minimum and maximum distance constraints;

calculates the complete CubeSat center of gravity;

rejects arrangements outside the requested CG range;

retains the valid arrangement closest to the geometric midpoint of the CubeSat.

Repository Structure

The recommended repository structure for the current version is:

CubeSat-CG-Tool/
├── Config_it.py
├── CDR.json
├── README.md
└── resources/
    └── cubesat_diagram.png

Main files

File

Purpose

Config_it.py

Current Tkinter interface, configuration management, and CG calculation logic

CDR.json

Example CubeSat component configuration

resources/cubesat_diagram.png

Reference diagram displayed by the application

README.md

Project overview and setup instructions

The image must be placed inside the resources folder because the current Python code searches for resources/cubesat_diagram.png relative to the script location.

Requirements

Python 3

Tkinter

NumPy

The remaining imported modules are part of the Python standard library.

Tkinter availability

Tkinter is normally included with standard Python installations on Windows and macOS.

On Debian or Ubuntu systems, it may need to be installed separately:

sudo apt install python3-tk

Installation

Clone the repository:

git clone <repository-url>
cd CubeSat-CG-Tool

Create a virtual environment:

Windows

python -m venv .venv
.venv\Scripts\activate

Linux or macOS

python3 -m venv .venv
source .venv/bin/activate

Install NumPy:

python -m pip install numpy

The current application includes an automatic NumPy installation attempt when the package is missing. Manual installation inside a virtual environment is nevertheless recommended.

Running the Application

From the repository root, run:

python Config_it.py

On systems where Python 3 is invoked explicitly:

python3 Config_it.py

Using the Application

1. Define internal components

For every internal component, enter:

component name;

mass in grams;

thickness in millimetres;

local center-of-mass position in millimetres.

A local COM value of 0 causes the application to use the geometric midpoint of the component.

Component names can be edited by double-clicking their displayed name.

2. Define external components

For every external component, enter:

component name;

mass in grams;

reference height;

effective center-of-mass position.

External components are included in the CG calculation but are not repositioned by the current search algorithm.

3. Define the CubeSat limits

Set:

total CubeSat height;

minimum acceptable CG;

maximum acceptable CG.

All dimensional inputs are currently interpreted in millimetres.

4. Define distance constraints

The application generates minimum and maximum separation fields for every pair of internal components.

These constraints are checked against the component boundaries rather than only against their center points.

5. Calculate the configuration

Select Calculate CG.

The application searches the permitted gap combinations and reports:

the effective COM position of each internal component;

the COM position of each external component;

the resulting overall CubeSat CG;

the number of complete configurations tested.

6. Save or load a configuration

Use the Settings tab to export the current configuration to JSON or load an existing JSON configuration.

The included CDR.json file can be used as an initial example.

Example Configuration

The supplied CDR.json contains an example arrangement with:

EPS;

OBC and payload assembly;

OBC and ADCS assembly;

radio;

antenna;

chassis;

payload;

placeholder internal volumes.

It also defines:

a total height of 95.2 mm;

an acceptable CG interval from 40.0 mm to 60.0 mm;

initial pairwise distance limits;

English as the interface language.

The example is intended as a starting dataset and should be reviewed before being used for engineering decisions.

Current Limitations

This version is an early engineering prototype. Important limitations include:

only one-dimensional positioning is considered;

the X and Y center-of-gravity coordinates are not yet evaluated;

only the first and last internal components are explicitly fixed;

intermediate gap values are currently iterated as integer millimetres;

all internal component pairs are presented as constraints, which can make the interface crowded;

external components are not part of the arrangement optimization;

component orientation and collision geometry are not represented;

empty volumes and reserved regions are not yet first-class objects;

the search space can become very large when many components or wide gap intervals are used;

validation and user error messages remain limited;

the GUI, calculation engine, and file handling are still contained in one Python file;

no automated tests are currently included;

no executable release is currently provided.

The tool should therefore be treated as a preliminary configuration aid, not as a substitute for complete CAD, structural, thermal, or mission-level verification.



License

No license has yet been selected for this project.

Until a license is added, the source code remains protected by default copyright rules and should not be reused or redistributed without the author's permission.

Author

Eduardo Miguel Dias da SilvaMechanical Engineering — FEUPPorto Space Team — ICARUS 1U CubeSat
