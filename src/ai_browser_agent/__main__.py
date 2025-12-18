"""The main entry point. Invoke as `ai_agent' or `python -m ai_agent`

"""


async def main():
    from asyncio.exceptions import CancelledError
    try:
        from ai_browser_agent.composition import main
        exit_status = await main()
    except (CancelledError, KeyboardInterrupt):
        exit_status = "Turn off agent"
    except Exception as e:
        exit_status = f'Ошибка: {e}'

    return exit_status


if __name__ == "__main__":
    import sys
    from asyncio import run

    sys.exit(run(main()))
