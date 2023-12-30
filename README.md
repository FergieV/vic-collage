# Vic Collage Creator

## Overview
The Vic Collage Creator is a Python script designed to create a digital collage of Vic Rattlehead NFTs from the Megadeth Digital project. It downloads images from multiple Ethereum wallet addresses and assembles them into a single image collage.

### Features
- Download Vic Rattlehead NFT images from specified Ethereum wallet addresses.
- Scale images and compile them into a single collage.
- Display progress for image downloads.
- Output collage details such as resolution, number of images, and file size.

## Installation

To run this script, you'll need Python installed on your system. The script is compatible with Python 3.6 and above. Additionally, you need to install some dependencies:

```bash
pip install aiohttp pillow web3 eth-utils
```

## Infura API Key
The script relies on the Infura service to access the Ethereum blockchain. To use it, you'll need to obtain an Infura API key. You can sign up for a free account on the [Infura website](https://infura.io/) to get your API key.

Once you have your API key, you will need to insert it into the `config.json` file of this repo before you can proceed with running the script.

## Usage
First, clone the repository and navigate to the script's directory:

```bash
git clone https://github.com/FergieV/vic-collage-creator.git
cd vic-collage-creator
```

## Running the Script
To run the script, use the following command:

```bash
python vic_collage_creator.py <wallet_address_1> <wallet_address_2> ... [--collage_scale SCALE]
```

- `<wallet_address_n>`: Replace with Ethereum wallet addresses from which to download Vic images.
- `--collage_scale SCALE`: (Optional) Specify the scale factor for images in the collage. The scale ranges from 0.10 (10%) to 1.00 (100%). The default value is 0.10.

## Examples
**Example 1**: Create a collage from two wallet addresses with the default scale:

```bash
python vic_collage_creator.py 0x123abc456def 0x789ghi012jkl
```

**Example 2**: Create a collage from three wallet addresses with a custom scale of 50%:

```bash
python vic_collage_creator.py 0x123abc456def 0x789ghi012jkl 0xmno456pqr --collage_scale 0.50
```

## Output
The script saves the generated collage in the 'output' directory, printing details like resolution, total number of images, and file size to the console.

![image](https://github.com/FergieV/vic-collage/assets/108777042/42b02b29-4421-4f28-a3c4-74d3cde9702a)
