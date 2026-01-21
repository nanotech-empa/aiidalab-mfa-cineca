# AiiDAlab MFA CINECA

AiiDAlab app for Multi-Factor Authentication (MFA) with CINECA HPC systems.

This application provides integration with CINECA's HPC infrastructure using smallstep CLI for secure authentication. For more information about CINECA HPC access, see the [official documentation](https://docs.hpc.cineca.it/general/access.html).

## Requirements

- Python >= 3.7
- smallstep CLI (step)
- curl and ca-certificates (system packages)

## Installation

### 1. Install System Dependencies

If you're on a Debian/Ubuntu system:

```bash
sudo apt-get install curl ca-certificates
```

### 2. Install smallstep CLI

Run the installation script provided:

```bash
bash install.sh
```

This will download and install the smallstep CLI tool (step) to `/usr/local/bin` (if you have sudo access) or `~/.local/bin` (for user installation).

### 3. Install Python Package

Install the package and its Python dependencies:

```bash
pip install -e .
```

Or using conda:

```bash
conda env create -f environment.yml
conda activate aiidalab-mfa-cineca
```

## Verification

Verify that smallstep CLI is installed correctly:

```bash
step version
```

## About smallstep CLI

smallstep CLI is a versatile toolkit for working with certificates, keys, and other PKI/security operations. It's required for MFA authentication with CINECA's HPC systems.

For more information about smallstep CLI, visit: https://smallstep.com/docs/step-cli/

## License

MIT License - See LICENSE file for details.
