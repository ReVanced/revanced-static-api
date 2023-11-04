
import json
import re
import click


@click.group()
def announcement():
    pass


@click.command()
@click.option('--author', help='Author')
@click.option('--title', help='Title', required=True)
@click.option('--message', help='Message')
@click.option('--attachment-urls', help='Attachment URLs')
@click.option('--channel', help='Channel', required=True)
@click.option('--level', help='Level', type=int)
def create(author: str, title: str, message: str, attachment_urls: str, channel: str, level: int):
    config = {
        "configs": [
            {
                "generators": ["announcement"],
                "announcement":{
                    "author": author if author else "ReVanced",
                    "title": title,
                    "content": {
                        "message": message,
                        "attachment_urls": attachment_urls.split(' ') if attachment_urls else []
                    },
                    "channel": channel,
                    "level": level if level else 0
                }
            }
        ]
    }

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)


announcement.add_command(create)
