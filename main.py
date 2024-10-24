import config
from discord_components import ComponentsBot

from music_cog import music_cog


bot = ComponentsBot(command_prefix='!')

bot.add_cog(music_cog(bot))

bot.run(config.token)


