#!/usr/bin/env python3
"""Utility to generate mawaqit JSON files for the adhan clock."""

import argparse
import asyncio
import json
import sys
from mawaqit import AsyncMawaqitClient


async def cmd_nearby(username, password, lat, lng):
    """List nearby mosques by coordinates."""
    client = AsyncMawaqitClient(
        username=username, password=password,
        latitude=lat, longitude=lng
    )
    try:
        await client.get_api_token()
        mosques = await client.all_mosques_neighborhood()
        print(f"Found {len(mosques)} nearby mosques:\n")
        for i, m in enumerate(mosques, 1):
            print(f"{i}. {m.get('name', 'Unknown')}")
            print(f"   UUID: {m['uuid']}")
            print(f"   Address: {m.get('localisation', 'N/A')}")
            print()
    finally:
        await client.close()


async def cmd_search(username, password, keyword):
    """Search mosques by keyword."""
    client = AsyncMawaqitClient(username=username, password=password)
    try:
        await client.get_api_token()
        mosques = await client.fetch_mosques_by_keyword(keyword)
        print(f"Found {len(mosques)} mosques matching '{keyword}':\n")
        for i, m in enumerate(mosques, 1):
            print(f"{i}. {m.get('name', 'Unknown')}")
            print(f"   UUID: {m['uuid']}")
            print(f"   Address: {m.get('localisation', 'N/A')}")
            print()
    finally:
        await client.close()


async def cmd_generate(username, password, uuid, output):
    """Generate JSON file from mosque UUID."""
    client = AsyncMawaqitClient(username=username, password=password)
    try:
        await client.get_api_token()
        client.mosque = uuid
        data = await client.fetch_prayer_times()
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Generated: {output}")
    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(
        description='Mawaqit utility for generating prayer times JSON'
    )
    parser.add_argument('-u', '--username', required=True, help='Mawaqit username')
    parser.add_argument('-p', '--password', required=True, help='Mawaqit password')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # nearby command
    p_nearby = subparsers.add_parser('nearby', help='List nearby mosques')
    p_nearby.add_argument('--lat', type=float, required=True, help='Latitude')
    p_nearby.add_argument('--lng', type=float, required=True, help='Longitude')

    # search command
    p_search = subparsers.add_parser('search', help='Search mosques by name')
    p_search.add_argument('keyword', help='Search keyword')

    # generate command
    p_gen = subparsers.add_parser('generate', help='Generate JSON from mosque UUID')
    p_gen.add_argument('uuid', help='Mosque UUID')
    p_gen.add_argument('-o', '--output', default='mawaqit.json', help='Output file')

    args = parser.parse_args()

    if args.command == 'nearby':
        asyncio.run(cmd_nearby(args.username, args.password, args.lat, args.lng))
    elif args.command == 'search':
        asyncio.run(cmd_search(args.username, args.password, args.keyword))
    elif args.command == 'generate':
        asyncio.run(cmd_generate(args.username, args.password, args.uuid, args.output))


if __name__ == '__main__':
    main()
