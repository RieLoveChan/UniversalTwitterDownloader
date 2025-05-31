#!/usr/bin/env python3
"""
Universal Twitter Media Downloader
Automated script to download all media from any specified Twitter account.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

def check_gallery_dl():
    """Check if gallery-dl is installed and install if needed."""
    try:
        subprocess.run(['gallery-dl', '--version'], 
                      capture_output=True, check=True)
        print("✓ gallery-dl is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing gallery-dl...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'gallery-dl'], 
                          check=True)
            print("✓ gallery-dl installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install gallery-dl")
            return False

def get_twitter_account():
    """Get Twitter account from user input."""
    print("\n=== Twitter Account Input ===")
    while True:
        account_input = input("Enter Twitter account (username only or full URL): ").strip()
        
        if not account_input:
            print("Please enter a valid Twitter account.")
            continue
        
        # Extract username from various input formats
        username = None
        
        # Check if it's a URL
        if 'twitter.com/' in account_input or 'x.com/' in account_input:
            # Extract username from URL
            match = re.search(r'(?:twitter\.com/|x\.com/)([^/?]+)', account_input)
            if match:
                username = match.group(1)
        elif account_input.startswith('@'):
            # Remove @ symbol
            username = account_input[1:]
        else:
            # Assume it's just the username
            username = account_input
        
        if username and re.match(r'^[A-Za-z0-9_]+$', username):
            return username
        else:
            print("Invalid username format. Please use only letters, numbers, and underscores.")

def setup_authentication():
    """Set up Twitter authentication."""
    print("\n=== Twitter Authentication Setup ===")
    print("You need to provide your Twitter credentials for authentication.")
    print("These will be stored securely in a .netrc file.")
    
    username = input("Enter your Twitter username: ")
    password = input("Enter your Twitter password: ")
    
    # Create .netrc file for authentication
    netrc_path = Path.home() / '.netrc'
    netrc_content = f"machine twitter.com login {username} password {password}\n"
    
    with open(netrc_path, 'a') as f:
        f.write(netrc_content)
    
    # Set proper permissions
    os.chmod(netrc_path, 0o600)
    print("✓ Authentication configured")

def create_config(target_username):
    """Create gallery-dl configuration file for the specified account."""
    config = {
        "extractor": {
            "twitter": {
                "directory": [f"{target_username}_media", "{category}", "{date:%Y-%m-%d}"],
                "filename": "{tweet_id}_{num:>02}.{extension}",
                "retweets": True,
                "videos": True,
                "cards": True,
                "quoted": True,
                "replies": True,
                "twitpic": True,
                "postprocessors": [
                    {
                        "name": "metadata",
                        "mode": "json"
                    }
                ]
            }
        },
        "output": {
            "progress": True,
            "log": {"level": "info"}
        },
        "downloader": {
            "retries": 3,
            "timeout": 30,
            "rate": "1M"
        }
    }
    
    config_path = Path.home() / '.config' / 'gallery-dl' / 'config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration file created for @{target_username}")

def create_metadata_file(target_username):
    """Create metadata file for the target account."""
    metadata = {
        "account": {
            "username": target_username,
            "profile_url": f"https://twitter.com/{target_username}",
            "alt_url": f"https://x.com/{target_username}"
        },
        "download_info": {
            "attempted_date": "2025-05-31",
            "status": "ready_for_download",
            "tool_used": "gallery-dl",
            "script_version": "flexible_v1.0"
        },
        "recommended_tools": [
            {
                "name": "gallery-dl",
                "method": "command_line",
                "authentication_required": True,
                "reliability": "high"
            },
            {
                "name": "X Media Downloader",
                "method": "browser_extension",
                "authentication_required": False,
                "reliability": "medium"
            }
        ],
        "notes": "Please respect the account owner's rights and Twitter's Terms of Service when downloading content."
    }
    
    metadata_file = f"{target_username}_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata file created: {metadata_file}")

def download_media(target_username):
    """Download media from the specified Twitter account."""
    print(f"\n=== Starting Download from @{target_username} ===")
    
    # Create output directory
    output_dir = f"{target_username}_media"
    Path(output_dir).mkdir(exist_ok=True)
    
    # Construct Twitter URL
    twitter_url = f"https://twitter.com/{target_username}"
    
    try:
        subprocess.run(['gallery-dl', twitter_url], check=True)
        print(f"✓ Download completed successfully!")
        print(f"Media files have been saved to: ./{output_dir}/")
    except subprocess.CalledProcessError as e:
        print(f"✗ Download failed with error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your Twitter credentials are correct")
        print("2. Check if your account has access to the profile")
        print("3. Ensure the target account exists and is not private")
        print(f"4. Try running with verbose output: gallery-dl -v {twitter_url}")

def main():
    """Main execution function."""
    print("Universal Twitter Media Downloader")
    print("=" * 50)
    print("This script can download media from any public Twitter account.")
    
    # Get target Twitter account
    target_username = get_twitter_account()
    print(f"\n📱 Target account: @{target_username}")
    print(f"🔗 Profile URL: https://twitter.com/{target_username}")
    
    # Check and install gallery-dl
    if not check_gallery_dl():
        print("Please install gallery-dl manually and try again.")
        return
    
    # Setup authentication
    setup_auth = input("\nDo you need to set up Twitter authentication? (y/n): ")
    if setup_auth.lower() == 'y':
        setup_authentication()
    
    # Create configuration for this specific account
    create_config(target_username)
    
    # Create metadata file
    create_metadata_file(target_username)
    
    # Confirm before starting download
    print(f"\n📋 Summary:")
    print(f"   • Target: @{target_username}")
    print(f"   • Output folder: {target_username}_media/")
    print(f"   • Tool: gallery-dl with authentication")
    
    proceed = input(f"\nReady to download all media from @{target_username}? (y/n): ")
    if proceed.lower() == 'y':
        download_media(target_username)
    else:
        print("Download cancelled.")
        print(f"Configuration saved for future downloads of @{target_username}")

if __name__ == "__main__":
    main()