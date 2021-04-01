import discord
from discord.ext import commands
import asyncio
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from io import BytesIO
import math

matplotlib.use("agg")

def data_check(data):
    data = [a.isdigit() for a in data]
    return all(data)

def bar(*args):
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.bar(args, args1)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def pie(*args):
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.pie(args1, labels=args, autopct = '%1.1f%%', shadow = True)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def scatter(*args):
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.scatter(args, args1, color='r')
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def line(*args):
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.plot(args, args1, 'o-g')
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def contour(*args):
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    X, Y = np.meshgrid(args1, args1)
    Z = np.sqrt(X**2 + Y**2)
    plt.contourf(X, Y, Z)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

class Graphing(commands.Cog):

    def __init__(self, client):
        self.PyBot = client
        self.loop = asyncio.get_running_loop()

    @commands.command(name="bar", description="Plots a bar-graph based on the data points that you input", aliases=["bargraph"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bar(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        image = await self.loop.run_in_executor(None, bar, *args)
        return await ctx.send(file=image)

    @commands.command(name="circle", description="Plots a pie-chart based on the data points that you input", aliases=["circlegraph", "piechart", "pie"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def circle(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        image = await self.loop.run_in_executor(None, pie, *args)
        return await ctx.send(file=image)

    @commands.command(name="scatterplot", description="Plots a scatter-plot based on the data points that you input", aliases=["scatter"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def scatterplot(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        image = await self.loop.run_in_executor(None, scatter, *args)
        return await ctx.send(file=image)

    @commands.command(name="linegraph", description="Plots a line-graph based on the data points that you input", aliases=["line"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def linegraph(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        image = await self.loop.run_in_executor(None, line, *args)
        return await ctx.send(file=image)

    @commands.command(name="contour", description="Plots a line-graph based on the data points that you input", aliases=["contourplot"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def contour(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        if len(args) < 2:
            return await ctx.send("please provide at least 2 numbers")
        image = await self.loop.run_in_executor(None, contour, *args)
        return await ctx.send(file=image)

def setup(client):
    client.add_cog(Graphing(client))