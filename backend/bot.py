import os
import sys
import traceback
from datetime import datetime
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
    ActivityHandler
)
from botbuilder.schema import Activity, ActivityTypes
from config import settings
import genie_client

# Settings are pre-loaded via pydantic-settings in config.py
APP_ID = settings.MicrosoftAppId
APP_PASSWORD = settings.MicrosoftAppPassword

class GenieBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_text = turn_context.activity.text
        if not user_text:
            return

        await turn_context.send_activity("Genie is processing... 🧞")
        
        try:
            # For Teams bot, we still use the standard full result logic
            # as simple streaming isn't as trivial over Bot Framework activities
            conversation_id, message_id = genie_client.start_conversation(user_text)
            answer = genie_client.get_message_result(conversation_id, message_id)
            await turn_context.send_activity(answer)
        except Exception as e:
            await turn_context.send_activity(f"Error: {str(e)}")

ADAPTER_SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(ADAPTER_SETTINGS)

async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error.")

ADAPTER.on_turn_error = on_error
BOT = GenieBot()

async def messages(request: web.Request) -> web.Response:
    if "application/json" in request.content_type:
        body = await request.json()
    else:
        return web.Response(status=415)

    activity = Activity().from_dict(body)
    auth_header = request.headers.get("Authorization", "")

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)

APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    print("Bot running on port 3978")
    web.run_app(APP, host="0.0.0.0", port=3978)
