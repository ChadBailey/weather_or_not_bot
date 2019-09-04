import logging, os, traceback

import telegram
from telegram.ext import Updater, CommandHandler,InlineQueryHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode

import settings
from weather import Weather

class Weather_or_not:

    def __init__(self, token):
        self.me = "Weather or not bot"
        self.author = "[Kamel](https://t.me/astrokamel)"
        self.token = token
        self.bot = telegram.Bot(token=self.token)
        self.last_update = None
        self.last_context = None

    def start(self):
        self.updater = Updater(token=token, use_context=True)
        self.setup_dispatchers()
        self.updater.start_polling()


    def setup_dispatchers(self):
        self.dispatcher = self.updater.dispatcher

        # Create the handlers

        # 'start' is passed to the bot when someone initiates conversation
        # with the bot (might be inline-only?)
        start_handler = CommandHandler('start', self.hello)

        # Bot commands
        weekly_weather_handler = CommandHandler('weekly_forecast', self.weekly_weather)
        hourly_weather_handler = CommandHandler('hourly_forecast', self.hourly_weather)
        alerts_handler = CommandHandler('alerts', self.alerts)
        radar_url_handler = CommandHandler('radar', self.radar_url)
        radar_url_inline_handler = InlineQueryHandler(self.inline_radar_url)

        # filters.command basically acts as an "else" statement - if no other
        # handler was triggered, this one gets triggered accoring to my
        # limited understanding
        unknown_handler = MessageHandler(Filters.command, self.help)

        # Not enabled, only here for demonstration purposes
        # echo's back everything said
        echo_handler = MessageHandler(Filters.text, self.echo)

        # Apply the handlers
        active_handlers = [
            start_handler,
            weekly_weather_handler,
            hourly_weather_handler,
            alerts_handler,
            radar_url_handler,
            radar_url_inline_handler,
            unknown_handler
        ]
        for handler in active_handlers:
            self.dispatcher.add_handler(handler)

    def _reply(self, update, context, msg):
        context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.MARKDOWN, text=msg)

    def hello(self, update, context):
        self._reply(update,context,f"Hello, I'm {self.me}. I was made by {self.author}. My creator hopes that eventually I can help him determine 'weather or not' he should go home early to avoid inclimate weather on his trip. You will eventually be able to use `/help` to see a list of commands but I am still being made and that doesn't work yet.")

    # Not enabled, only here for demonstration purposes
    def echo(self, update, context):
        self._reply(update, context, update.message.text)

    def help(self, update, context):
        self._reply(update, context, "Sorry, that is not a valid command.")

    def alerts(self,update,context):
        try:
            zipcode = context.args[0]
            wtr = Weather(zipcode)
            alerts = wtr.alerts_text()
            self._reply(update,context,alerts)

        except Exception:
            self._reply(update,context,f"Error: {traceback.format_exc()}")

    def radar_url(self,update,context):
        try:
            zipcode = context.args[0]
            wtr = Weather(zipcode)
            self._reply(update,context,wtr.radar_url)
        except Exception:
            self._reply(update,context,f"Error: {traceback.format_exc()}")

    def inline_radar_url(self,update,context):
        query = update.inline_query.query
        if not query: return
        try:
            zipcode = query.split(' ')[1]
            wtr = Weather(zipcode)
            results = []
            results.append(
                InlineQueryResultArticle(
                    id=query,
                    title=f"Weather radar for {zipcode}",
                    input_message_content=InputTextMessageContent(wtr.radar_url)
                )
            )
            context.bot.answer_inline_query(update.inline_query.id, results)

        except Exception:
            self._reply(update,context,f"Error: {traceback.format_exc()}")

    def weekly_weather(self,update,context):
        try:
            zipcode = context.args[0]
            wtr = Weather(zipcode)
            weekly_forecast = wtr.weekly_forecast_text()
            self._reply(update,context,weekly_forecast)

        except Exception as e:
            self._reply(update,context,f"Error: {str(e)}")

    def hourly_weather(self,update,context):
        try:
            zipcode = context.args[0]
            wtr = Weather(zipcode)
            hourly_forecast = wtr.hourly_forecast_text()
            self._reply(update,context,hourly_forecast)

        except Exception as e:
            self._reply(update,context,f"Error: {str(e)}")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    token = os.environ['TELEGRAM_API_TOKEN']
    bot = Weather_or_not(token)
    bot.start()