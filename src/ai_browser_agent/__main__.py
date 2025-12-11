"""The main entry point. Invoke as `ai_agent' or `python -m ai_agent`, also composition root

"""


async def main():
    try:
        from core import main
        exit_status = main()
    except KeyboardInterrupt:
        exit_status = "Turn off agent"

    return exit_status


if __name__ == "__main__":
    import sys
    from asyncio import run

    sys.exit(run(main()))
