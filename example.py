"""Example on how the world bank bot works."""

from wd_economy.world_bank import Database, Bot

db = Database('/data/project/dexbot/dd9626d3-a18d-428c-ac6c-387c41aff3a0_v2.csv')

bot = Bot('/data/project/dexbot/dd9626d3-a18d-428c-ac6c-387c41aff3a0_v2.csv',
          'http://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD',
          'P2299',
          'Q550207')
bot.run()
