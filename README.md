[![Build Status](https://travis-ci.org/FofanovLab/MTSv.svg?branch=master)](https://travis-ci.org/FofanovLab/MTSv)

# MTSv Pipeline

MTSv is a suite of metagenomic binning and analysis tools. It attempts to accurately identify which taxa are present in a given DNA sample by identifying *signature* reads that are unique to a single taxa. It assumes that read fragments in samples will be in a "shotgun" or short read format, typically ~50-200 bases in length.

**All commands listed in this document assume they're being executed from the repository's root directory. Adjust accordingly if you've installed the tools elsewhere.**

## Pipeline Overview
The pipeline is broken into two major sections: (1) the download and setup of sequences from the sequence database which only needs to be completed once per database and as needed to include updates and (2) the main binning and analysis pipeline that is completed for each new read set. 

0. [Installation](#installation)
1. [Sequence Download and Setup Quick Start Guide](https://github.com/FofanovLab/MTSv/wiki/Sequence-Download-and-Setup-Quick-Start-Guide)
2. [Binning and Analysis Quick Start Guide](https://github.com/FofanovLab/MTSv/wiki/Binning-and-Analysis-Quick-Start-Guide)

The MTSv pipeline is installed as a module on Northern Arizona University's Monsoon HPC Cluster. If running MTSv on Monsoon, check out the [MTSv on Monsoon ](https://github.com/FofanovLab/MTSv/wiki/Quickstart-for-NAU-Monsoon-Users) Quick Start Guide.


## Installation
MTSv is built in Rust, with a little bit of Python. You will need:
### Dependencies
1. [Anaconda or Miniconda to use Conda Environment](https://conda.io/docs/user-guide/install/index.html)
2. [rustc](#install-rustc-and-cargo)
3. [cargo >= 1.8.0](#install-rustc-and-cargo)
4. A C compiler (tested with GCC and clang)
5. Greater than GCC/5.2.0 on the PATH for runtime compilation of the C++11 code required for initial setup of the sequence databases.


### Clone Repository
Clone MTSv into desired location and move to `MTSv` directory
```
$ git clone https://github.com/FofanovLab/MTSv.git
$ cd MTSv
```

### Install Rustc and Cargo
* `rustc` and `cargo` >= 1.8.0 ([rustup.rs](https://rustup.rs) is the easiest installation method)
* a C compiler (tested with GCC and clang)

### Update
Update dependencies in `Cargo.lock`

```
$ cargo update
```

### Building

To build the MTSv binaries:

~~~
$ cargo build --release
~~~

They'll be available under `target/release/MTSv-*`.


### Create Conda environment with Python3 and required packages.
The environment only needs to be created once.
```
$ conda create --name biopy3 python=3.5.2 biopython pandas
```
The name `biopy3` can be changed to whatever name you want.  

#### Activate Conda Environment
```
$ source activate biopy3
```

#### Install etetoolkit
```
$ conda install -c etetoolkit ete3 ete_toolchain
```

#### Deactivate Conda Environment
```
$ source deactivate
```

#### If you already have a Python3.5.2 environment you can just use Conda to install the required packages.
```
$ source activate ENV_NAME
$ conda install -c etetoolkit ete3 ete_toolchain
$ conda install pandas
$ conda install biopython
```
