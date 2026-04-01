"""
Discord bot for operating Claude Code via Discord messages.

Setup:
  1. Copy .env.example to .env and fill in DISCORD_TOKEN
  2. pip install -r requirements.txt
  3. python discord_bot.py

Usage in Discord:
  !claude <prompt>   - Send a prompt to Claude Code
  !claude help       - Show help
"""

import os
import asyncio
import subprocess
import textwrap
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLAUDE_COMMAND = os.getenv("CLAUDE_COMMAND", "claude")
ALLOWED_CHANNEL_IDS = os.getenv("ALLOWED_CHANNEL_IDS", "")  # comma-separated, empty = all channels
MAX_RESPONSE_LENGTH = 1900  # Discord limit is 2000, leave margin

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

allowed_channels: set[int] = set()
if ALLOWED_CHANNEL_IDS:
    allowed_channels = {int(c.strip()) for c in ALLOWED_CHANNEL_IDS.split(",") if c.strip()}


def is_channel_allowed(channel_id: int) -> bool:
    return not allowed_channels or channel_id in allowed_channels


async def run_claude(prompt: str, timeout: int = 120) -> str:
    """Run claude CLI with the given prompt and return the output."""
    try:
        proc = await asyncio.create_subprocess_exec(
            CLAUDE_COMMAND,
            "--print",
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return f"Error: Claude Code timed out after {timeout} seconds."

        if proc.returncode != 0:
            err = stderr.decode("utf-8", errors="replace").strip()
            return f"Error (exit {proc.returncode}): {err or 'unknown error'}"

        return stdout.decode("utf-8", errors="replace").strip()
    except FileNotFoundError:
        return f"Error: `{CLAUDE_COMMAND}` not found. Make sure Claude Code CLI is installed."
    except Exception as e:
        return f"Error: {e}"


def split_message(text: str, limit: int = MAX_RESPONSE_LENGTH) -> list[str]:
    """Split a long message into chunks that fit within Discord's limit."""
    if len(text) <= limit:
        return [text]
    return textwrap.wrap(text, width=limit, break_long_words=True, replace_whitespace=False)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    if allowed_channels:
        print(f"Restricted to channels: {allowed_channels}")
    else:
        print("Listening on all channels")


@bot.command(name="claude")
async def claude_command(ctx: commands.Context, *, prompt: str = ""):
    """Send a prompt to Claude Code and return the response."""
    if not is_channel_allowed(ctx.channel.id):
        return

    if not prompt or prompt.strip().lower() == "help":
        await ctx.send(
            "**Claude Code Bot**\n"
            "`!claude <prompt>` — Send a prompt to Claude Code\n"
            "`!claude help`    — Show this help message\n\n"
            "Example: `!claude Write a Python function to reverse a string`"
        )
        return

    async with ctx.typing():
        response = await run_claude(prompt)

    if not response:
        await ctx.send("_(No response from Claude Code)_")
        return

    chunks = split_message(response)
    for chunk in chunks:
        await ctx.send(f"```\n{chunk}\n```" if "\n" in chunk else chunk)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Error: {error}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    bot.run(DISCORD_TOKEN)
