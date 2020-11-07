#!/usr/bin/python
import argparse
import json

from collections import OrderedDict

CHANNEL_PARAMS = ["id", "name", "desc"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepath", help="path to the json list of channels", default="./channels"
    )
    parser.add_argument(
        "-c",
        "--create",
        nargs="+",
        help="create a new channel",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-d",
        "--delete",
        help="delete channel by id or name",
        default=None,
        required=False,
    )
    return parser.parse_args()


def create_channel(filepath, channel_args):
    data = load_json_data(filepath)
    print(channel_args)
    channel_zip = zip(CHANNEL_PARAMS, list(channel_args))
    channel = OrderedDict(channel_zip)
    if not data.get("channels"):
        data["channels"] = []
    data["channels"].append(channel)
    write_json_data(filepath, data)


def delete_channel(filepath, identifier):
    data = load_json_data(filepath)
    channels = data.get("channels", [])
    for i, channel in enumerate(channels):
        if identifier in [channel["id"], channel["name"]]:
            del channels[i]
            break
    write_json_data(filepath, data)


def load_json_data(filepath):
    with open(filepath, "r+") as f:
        return json.load(f)


def write_json_data(filepath, data):
    with open(filepath, "w+") as f:
        json.dump(data, f)


def main():
    args = parse_args()
    filepath = args.filepath
    if args.create:
        create_channel(filepath, args.create)
    elif args.delete:
        delete_channel(filepath, args.delete)


if __name__ == "__main__":
    main()