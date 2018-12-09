# KYD bot by Pbzrpa

import os
import requests
import discord

from discord.ext.commands import Bot
from explorer import Explorer

BOT_PREFIX = "!"

client = Bot(command_prefix=BOT_PREFIX)


def localize(value, decimals = 2):
    str_format = "{0:,.%df}" % decimals
    return str_format.format(value)


def seconds_to_freq(s):
    d = int(s / 60 / 60 / 24 % 365)
    h = int(s / 60 / 60)
    m =int(s / 60 % 60)
    return '{}d {}h {}m'.format(d, h, m)


def get_btc_data():
    '''
    {"15m" : 3424.05, "last" : 3424.05, "buy" : 3424.05, "sell" : 3424.05, "symbol" : "$"}
    '''
    try:
        data = requests.get('https://blockchain.info/ticker', verify=False, timeout = 10).json()['USD']
    except Exception as e:
        print('BTC', e)
        data = None
    return data


def get_cb_data():
    '''
    data : {
        "id":"KYD_BTC",
        "last":"0.00000040",
        "volume":"0.01356439",
        "ask":"0.00000110",
        "bid":"0.00000020",
        "percentChange":-96
        }
    '''
    try:
        data = requests.get('https://api.crypto-bridge.org/api/v1/ticker/KYD_BTC', verify=False, timeout = 10).json()
    except Exception as e:
        print('CB', e)
        data = None
    return data


class Price:

    def __init__(self):
        self.cb_data = get_cb_data()
        self.btc_data = get_btc_data()
        self.explorer = Explorer()
        self.current_supply = None

    def is_valid(self):
        return self.cb_data is not None and self.btc_data is not None

    def get_current_supply(self):
        if self.current_supply is None:
            self.current_supply = self.explorer.get_current_supply()
        return self.current_supply

    def get_sat_value(self):
        return float(self.cb_data.get('last', 0))

    def get_btc_price(self):
        return self.btc_data['last']

    def get_market_cap(self):
        return self.get_btc_price() * self.get_sat_value() * self.get_current_supply()

    def get_volume(self):
        return float(self.cb_data.get('volume', 0))

    def get_ask(self):
        return float(self.cb_data.get('ask', 0))

    def get_bid(self):
        return float(self.cb_data.get('bid', 0))

    def get_usd_price(self):
        return self.get_btc_price() * self.get_sat_value()

    def get_24_diff(self):
        return float(self.cb_data.get('percentChange'))


class MNInfo:
    collateral = 10000
    mn_rewards = 10
    pos_rewards = 2.5

    def __init__(self):
        self.cb_data = get_cb_data()
        self.btc_data = get_btc_data()
        self.explorer = Explorer()
        self.current_supply = None
        self.mn_data = None

    def is_valid(self):
        return self.cb_data is not None and self.btc_data is not None

    def get_current_supply(self):
        if self.current_supply is None:
            self.current_supply = self.explorer.get_current_supply()
        return self.current_supply

    def get_mn_data(self):
        if self.mn_data is None:
            self.mn_data = self.explorer.get_mn_data()
        return self.mn_data

    def get_collateral(self):
        return self.collateral

    def get_mn_rewards(self):
        return self.mn_rewards

    def get_pos_rewards(self):
        return self.pos_rewards

    def get_block_count(self):
        return self.explorer.get_block_count()

    def get_mn_count(self):
        return self.get_mn_data().get('total', 0)

    def get_sat_value(self):
        return float(self.cb_data.get('last', 0))

    def get_btc_price(self):
        return self.btc_data['last']

    def get_usd_price(self):
        return self.get_btc_price() * self.get_sat_value()

    def get_daily_coins(self):
        return (1440.0 * self.get_mn_rewards()) / self.get_mn_count()

    def get_daily_reward(self):
        return self.get_daily_coins() * self.get_usd_price()

    def get_payout_freq(self):
        payments_days = 1440.0 / self.get_mn_count()
        payments_hours = 24 / payments_days
        return seconds_to_freq(payments_hours * 3600)

    def get_locked_coins(self):
        return self.get_mn_count() * self.get_collateral()

    def get_node_price(self):
        return self.get_usd_price() * self.get_collateral()

    def get_yearly_income(self):
        return self.get_daily_reward() * 365

    def get_roi(self):
        return ((self.get_daily_coins() * 365) / self.get_collateral()) * 100


# Bot Commands


@client.event
async def on_ready():
    print ("Bot is Ready")
    print ("I am running on " + client.user.name)


@client.command(name='price', pass_context=True)
async def ctsc_info(ctx):

    price_obj = Price()

    if price_obj.is_valid():
        embed = discord.Embed(color = 0x23DA79, title = 'Price Ticker')
        embed.add_field(name = "Market Cap", value = "$ {}".format(localize(price_obj.get_market_cap())))
        embed.add_field(name = "Volume", value = "{} BTC".format(localize(price_obj.get_volume(), decimals = 8)))
        embed.add_field(name = "Change", value = "{} %".format(localize(price_obj.get_24_diff(), decimals = 2)))
        embed.add_field(name = "Current", value = "{} BTC".format(localize(price_obj.get_sat_value(), decimals = 8)))
        embed.add_field(name = "Bid", value = "{} BTC".format(localize(price_obj.get_bid(), decimals = 8)))
        embed.add_field(name = "Ask", value = "{} BTC".format(localize(price_obj.get_ask(), decimals = 8)))
        embed.add_field(name = "Price", value = "$ {}".format(localize(price_obj.get_usd_price(), decimals = 6)))
        await client.say(embed = embed)
    else:
        await client.say(ctx.message.author.mention + ': Sorry we were unable to get the info. We will investigate')


@client.command(name='mninfo', pass_context=True)
async def ctsc_mninfo(ctx):

    mn_obj = MNInfo()

    if mn_obj.is_valid():
        embed = discord.Embed(color = 0x23DA79, title = "Masternode Info")
        embed.add_field(name = "Block Count", value = "{}".format(
            mn_obj.get_block_count()))
        embed.add_field(name = "MN Count", value = "{}".format(
            mn_obj.get_mn_count()))
        embed.add_field(name = "Supply", value = "{} KYD".format(
            localize(mn_obj.get_current_supply(), decimals = 0)))
        embed.add_field(name = "Collateral", value = "{} KYD".format(
            localize(mn_obj.get_collateral(), decimals = 0)))
        embed.add_field(name = "MN Reward", value = "{} KYD".format(
            localize(mn_obj.get_mn_rewards(), decimals = 2)))
        embed.add_field(name = "PoS Reward", value = "{} KYD".format(
            localize(mn_obj.get_pos_rewards(), decimals = 2)))
        embed.add_field(name = "MN Daily Reward", value = "$ {}".format(
            localize(mn_obj.get_daily_reward(), decimals = 2)))
        embed.add_field(name = "Payout Frequency", value = "{}".format(mn_obj.get_payout_freq()))
        embed.add_field(name = "Locked Coins", value = "{} KYD".format(
            localize(mn_obj.get_locked_coins(), decimals = 0)))
        embed.add_field(name = "ROI", value = "{} %".format(
            localize(mn_obj.get_roi(), decimals = 2)))
        embed.add_field(name = "Node Price", value = "$ {}".format(
            localize(mn_obj.get_node_price(), decimals = 2)))
        embed.add_field(name = "Yearly Income", value = "$ {}".format(
            localize(mn_obj.get_yearly_income(), decimals = 2)))
        await client.say(embed = embed)
    else:
        await client.say(ctx.message.author.mention + ': Sorry we were unable to get the info. We will investigate')


HASH_VALUES = [
    ('EH', 1000000000000000000),
    ('PH', 1000000000000000),
    ('TH', 1000000000000),
    ('GH', 1000000000),
    ('MH', 1000000),
    ('kH', 1000),
    ]


def resolve_hashrate(value):
    for symbol, amount in HASH_VALUES:
        if value >= amount:
            return (symbol, value / amount)
    return ('kH', float(0))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (
            message.content.upper().startswith('!PRICE') or
            message.content.upper().startswith('!MNINFO') or
            message.content.upper().startswith('!H')):
        await client.process_commands(message)


@client.event
async def on_command_error(error, *args, **kwargs):
    ctx = args[0]
    print(error)
    await client.send_message(
        ctx.message.channel,
        ctx.message.author.mention + ' Oops something went wrong. Please check !h')


@client.command(name='h', pass_context=True)
async def help(ctx):
    help_message = """```Here are list of available commands:

    !h - Displays this message

    *** Price Info ***

    !price - Displays price info

    *** Masternode Info ***

    !mninfo - Displays masternode info

    ```"""
    await client.say(help_message)


client.run(os.environ['KYDTOKEN'])
