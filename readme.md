---
name: gln-setup
primary: Matthew Gamble
participants: [Matthew Gamble]
tags: [code, gln, plugin, gln-v3, python]
---

# gln-setup: A plugin for gln-v3 and a standalone cli to automate the setup for both required and optional programs and settings for gln to function.

This is a tool to help automate the setup process for using gln.
There are several non-python dependencies that must be taken care of before gln will work property.

## Installation

The most straightforward way to install gln-setup is with uv.

### Install uv

`curl -LsSf https://astral.sh/uv/install.sh | sh`

This will work on your local machine or the cluster.

See [https://docs.astral.sh/uv/getting-started/installation/#installation-methods]() for help.

### Install gln-setup

`uv tool install --python 3.12 https://github.com/TheRealGambleLab/gln-setup.git`

## 1. Install dependencies

Run the `install-deps` command by either running `gln-setup install-deps` or `gln setup install-deps` if you already have installed the gln app.
The command tries to intall the necessary depedencies (if not already present on your system. 

## 2. Set up git

You must tell git your name and email so that your commits can record that information.
Run `gln-setup git --name "John Doe" --email john.doe@somewhere.com`, replacing the nonsense with your information.

## 3. Set up ssh keys

gln requires the ability to communicate with remote indexed archives (RIAs) which are hosted on the HPC.
Setting up ssh keys will prevent the program from asking you for a password all the time.
gln can also communicate with github to download repositories and datasets (without an annex). 
So setting up an ssh key for github, will also be helpful.

It is helpful for ssh keys to have information about where they are from.
So, if you are on a computer called foo and you want to set up an ssh key for the HPC and your username was jdoe you might run, `gln-setup ssh-key fooToHPC jdoe@jdoe.einsteinmed.edu`

In this case, ssh-key will generate public and private keys called fooToHPC and fooToHPC.pub, it will add the configuration for the key to .ssh/config, and it will attempt to send the public key to jdoe.einsteinmed.edu. 
You will be prompted for your password on the cluster, but this should be the last time you needed.
Fun fact, even when you need to change your password for you institution, ssh-keys keep working.

This also works for generating an ssh-key for github, and would look like, `gln-setup ssh-key "fooToGH" git@github.com`.
Some prompts may come up on your screen to guide you through the github authentication process.
Some times this doesn't work and if so, you will have to copy the public key (fooToGH.pub) to the github.com website manually.
See [https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account]() for help.

## 4. install gln

This one is pretty simple.
`gln-setup gln-install` will install the gln (and datalad for free) on your machine.
The default is to install on python3.12.
You can use the --python option to change the default to another version (anything >=3.11 will work).
As a bonus, if you don't have the python version specified, it will be installed on your system.

## TODO

- [x] automate git setup
- [x] automate git-annex install
- [x] automate rclone install
- [x] automate git-annex-remote-rclone install
- [x] automate datalad install
- [x] automate ssh-key setup for HPC
- [x] automate ssh-key setup for github.com
- [x] automate gh install
- [x] automate pdm install
- [x] automaate gh repo setup?? This goes elsewhere?? Is there a github extension like there is a ria extension?
- [x] fix bug where setting up an ssh-key for github leads to erasing of the .ssh/config. WTF

