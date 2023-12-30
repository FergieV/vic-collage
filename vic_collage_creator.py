"""
Author: Fergie V
Description: Script to create a collage of Vic NFTs from multiple wallet addresses.
Date: 2023-12-29

This script downloads Vic Rattlehead NFT images from given Ethereum wallet addresses and creates a collage out of them.
"""

import os
import math
import json
import argparse
import shutil
import aiohttp
import asyncio
import time
from PIL import Image, ImageDraw, ImageFont
from web3 import Web3
from eth_utils import to_checksum_address

def print_ascii_vic():
    """Prints 'VIC' in ASCII art."""
    ascii_art = """
                        ██╗   ██╗██╗ ██████╗
                        ██║   ██║██║██╔════╝
                        ██║   ██║██║██║     
                        ╚██╗ ██╔╝██║██║     
                         ╚████╔╝ ██║╚██████╗
                          ╚═══╝  ╚═╝ ╚═════╝
 ______     ______     __         __         ______     ______     ______    
/\  ___\   /\  __ \   /\ \       /\ \       /\  __ \   /\  ___\   /\  ___\   
\ \ \____  \ \ \/\ \  \ \ \____  \ \ \____  \ \  __ \  \ \ \__ \  \ \  __\   
 \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_____\ 
  \/_____/   \/_____/   \/_____/   \/_____/   \/_/\/_/   \/_____/   \/_____/ 
    """
    print(ascii_art)

def load_configuration(file_path):
    """
    Loads configuration data from a JSON file.

    Args:
    file_path (str): Path to the configuration file.

    Returns:
    dict: Dictionary containing the configuration data, or an empty dictionary if an error occurs.
    """
    try:
        with open(file_path, 'r') as conf_file:
            return json.load(conf_file)
    except FileNotFoundError:
        print(f"Configuration file not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
    return {}

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """
    Prints a progress bar to the console.

    Args:
    iteration (int): Current iteration (zero-based).
    total (int): Total iterations.
    prefix (str): Prefix string.
    suffix (str): Suffix string.
    length (int): Character length of the bar.
    fill (str): Bar fill character.
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end="\r")
    if iteration == total: 
        print()

class VicCollageCreator:
    def __init__(self, api_key, contract_address, contract_abi, vic_base_url):
        """
        Initializes the VicCollageCreator with necessary parameters.

        Args:
        api_key (str): API key for accessing the Ethereum blockchain.
        contract_address (str): Ethereum contract address.
        contract_abi (json): Contract ABI.
        vic_base_url (str): Base URL for Vic images.
        """
        self.api_key = api_key
        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.vic_base_url = vic_base_url

    async def download_vic(self, session, token_id, callback=None):
        """
        Asynchronously downloads a Vic image.

        Args:
        session (aiohttp.ClientSession): The session for making HTTP requests.
        token_id (int): Token ID of the Vic image.
        callback (function): Optional callback function to update progress.
        """
        try:
            call_url = f'{self.vic_base_url}/{token_id}.png'
            async with session.get(call_url) as response:
                if response.status == 200:
                    content = await response.read()
                    path = os.path.join('vics', f'{token_id}.png')
                    with open(path, 'wb') as file:
                        file.write(content)
                    print(f'Saved Vic {token_id}.png')
                else:
                    print(f'Failed to get {token_id}.png. Status code: {response.status}')
                if callback:
                    callback()
        except Exception as e:
            print(f'Error downloading Vic {token_id}.png: {e}')

    async def get_the_vics(self, target_wallet_address):
        """
        Retrieves and downloads Vics owned by a specific wallet address.

        Args:
        target_wallet_address (str): Target Ethereum wallet address.

        Returns:
        list: List of token IDs of the Vics owned by the wallet.
        """
        infura_url = f'https://mainnet.infura.io/v3/{self.api_key}'
        web3 = Web3(Web3.HTTPProvider(infura_url))

        checksum_contract_address = to_checksum_address(self.contract_address)
        checksum_wallet_address = to_checksum_address(target_wallet_address)

        contract = web3.eth.contract(address=checksum_contract_address, abi=self.contract_abi)

        token_ids = contract.functions.tokensOfOwner(checksum_wallet_address).call()
        token_ids.sort()

        output_dir = 'vics'
        os.makedirs(output_dir, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            total_vics = len(token_ids)
            print_progress_bar(0, total_vics, prefix='Progress:', suffix='Complete', length=50)

            def update_progress_bar():
                update_progress_bar.counter += 1
                print_progress_bar(update_progress_bar.counter, total_vics, prefix='Progress:', suffix='Complete', length=50)
            update_progress_bar.counter = 0

            tasks = [self.download_vic(session, token_id, callback=update_progress_bar) for token_id in token_ids]
            await asyncio.gather(*tasks)

        return token_ids

    def make_vic_collage(self, image_files, collage_scale=0.10):
        """
        Creates a collage from a list of Vic images.

        Args:
        image_files (list): List of image file paths.
        collage_scale (float): Scale factor for each image in the collage.

        The function creates a collage of Vic images, scales each image according to the given scale factor,
        and arranges them in a grid. The collage is saved in the 'output' directory.
        """
        if not image_files:
            print('No images to create a collage. Exiting...')
            return

        scaled_images = []
        for img_file in image_files:
            img_path = os.path.join('vics', img_file)
            if os.path.exists(img_path):
                with Image.open(img_path) as img:
                    scaled_image = img.resize(
                        (int(img.width * collage_scale), int(img.height * collage_scale)))
                    scaled_images.append(scaled_image)
            else:
                print(f"Warning: File not found {img_path}")

        if not scaled_images:
            print("No valid images found for collage. Exiting...")
            return

        num_images = len(scaled_images)
        num_rows = int(math.sqrt(num_images))
        num_cols = math.ceil(num_images / num_rows)

        collage_width = max(img.size[0] for img in scaled_images) * num_cols
        collage_height = max(img.size[1] for img in scaled_images) * num_rows

        collage = Image.new('RGB', (collage_width, collage_height), (0, 0, 0))
        draw = ImageDraw.Draw(collage)

        x_offset, y_offset = 0, 0
        for image_file, image in zip(image_files, scaled_images):
            if os.path.exists(os.path.join('vics', image_file)):
                collage.paste(image, (x_offset, y_offset))
                file_name = os.path.splitext(image_file)[0]
                draw.text((x_offset, y_offset), file_name, font=ImageFont.load_default(), fill=(255, 255, 255))
                x_offset += image.size[0]
                if x_offset >= collage_width:
                    x_offset = 0
                    y_offset += image.size[1]

        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        epoch_time = int(time.time())
        output_collage_path = os.path.join(output_dir, f'vics_collage_{epoch_time}.jpg')
        collage.save(output_collage_path)

        # Print collage details
        total_images = len(image_files)
        resolution = collage.size  # (width, height)
        file_size = os.path.getsize(output_collage_path)  # in bytes

        print()
        print(f'Total number of images: {total_images}')
        print(f'Image scale for collage: {collage_scale * 100:.0f}%')
        print(f'Total resolution: {resolution[0]}x{resolution[1]} pixels')
        print(f'File size: {file_size / 1024:.2f} KB')
        print(f'Collage saved to {output_collage_path}')
        print()

async def main_async():
    """
    Main asynchronous function to create a collage of Vic NFTs.
    """
    start_time = time.time()

    print_ascii_vic()

    config = load_configuration('config.json')
    creator = VicCollageCreator(
        api_key=config.get('infura_api_key'),
        contract_address=config.get('contract_address'),
        contract_abi=config.get('contract_abi'),
        vic_base_url=config.get('vic_base_url')
    )

    parser = argparse.ArgumentParser(description='Create a collage of Vic NFTs')
    parser.add_argument('target_wallet_addresses', type=str, nargs='+', help='Target wallet addresses containing the Vics')
    parser.add_argument('--collage_scale', type=float, default=0.10, help='Scale factor for the collage images')
    args = parser.parse_args()

    if not 0.010 <= args.collage_scale <= 1.0:
        parser.error('Collage scale must be a float between 0.010 and 1.0')

    all_image_files = []
    for wallet_address in args.target_wallet_addresses:
        print(f"Processing wallet: {wallet_address}")
        token_ids = await creator.get_the_vics(wallet_address)
        all_image_files.extend([f'{i}.png' for i in token_ids])

    if all_image_files:
        creator.make_vic_collage(all_image_files, collage_scale=args.collage_scale)
    else:
        print("No images to create a collage.")

    print(f'Total execution time: {time.time() - start_time:.2f} seconds')

if __name__ == '__main__':
    asyncio.run(main_async())
    shutil.rmtree('vics', ignore_errors=True)
    os.mkdir('vics')