import discord
from discord.ext import commands
import asyncio

import matplotlib
matplotlib.use("agg")

from matplotlib import pyplot as plt
import numpy as np

from io import BytesIO
from typing import Optional
from Equation import Expression

import math
import re

def data_check(data):
    data = [a.isdigit() for a in data]
    return all(data)

def bar(*args):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.bar(args, args1)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def pie(*args):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("Solarize_Light2")
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.pie(args1, labels=args, autopct = '%1.1f%%', shadow = True)
    plt.savefig(buffer, transparent=True)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def scatter(*args):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("bmh")
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    plt.scatter(args, args1, color='r')
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def line(*args):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("bmh")
    buffer = BytesIO()

    x_ = args
    y = [int(i) for i in args]

    plt.plot(x_, y, 'o-g')
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def linear(m: float, b: float):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("bmh")

    plt.xlim((-40, 40))
    plt.ylim((-40, 40))
    buffer = BytesIO()
    
    x_ = np.linspace(-100, 100, 50000)
    y  = [ (m*i + b) for i in x_]
        
    plt.plot(x_, y)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def quadratic(a: float, b: float, c: float):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("bmh")

    plt.xlim((-40, 40))
    plt.ylim((-40, 40))
    buffer = BytesIO()
    
    x_ = np.linspace(-100, 100, 50000)
    y  = [ (a * (i**2) + (b * i) + c) for i in x_]
        
    plt.plot(x_, y)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def equation_(equation: str):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("bmh")

    plt.xlim((-40, 40))
    plt.ylim((-40, 40))   
    buffer = BytesIO()

    def _mul(val):
        val = list(val.group())
        val.insert(-1, "*")
        return "".join(val)

    equation = str(re.sub(r"([0-9\.] ?x)",  _mul, equation))
    equation = str(re.sub(r"([0-9\.] ?\()", _mul, equation))
    equation = equation.replace(")(", ")*(")
    
    x_ = np.linspace(-100, 100, 50000)
    
    fn = Expression(equation, ["x"])
    y = [fn(x) for x in x_]
    
    plt.plot(x_, y)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def exponent(*args):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("bmh")
    buffer = BytesIO()
    x = np.array([int(i) for i in args])
    y = np.exp(x)
    plt.plot(x, y)
    plt.savefig(buffer)
    plt.close()
    buffer.seek(0)
    image = discord.File(buffer, "graph.png")
    return image

def contour(*args):
    plt.style.use(["fast", "fivethirtyeight", "ggplot"])
    plt.style.use("dark_background")
    buffer = BytesIO()
    args1 = [int(i) for i in args]
    X, Y = np.meshgrid(args1, args1)
    Z = np.sqrt(X**2 + Y**2)
    plt.contourf(X, Y, Z)
    plt.savefig(buffer, transparent=True)
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

    @commands.command(
        name="linegraph", 
        description=(
            "Plots a line-graph based on the data points that you input\n"
            "Accepts only numerical data-points\n"
            "EX: `%line 1 2 4 5 7 ...`\n"
            r"For other equation graphing use %equation"
        ), aliases=["line"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def linegraph(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        image = await self.loop.run_in_executor(None, line, *args)
        return await ctx.send(file=image)

    @commands.command(
        name="quadratic", 
        description=(
            "Plots a quadratic-line-graph based on the data points that you input\n"
            "Accepts only numerical `a, b, c` values\n"
            "EX: `%quad -1 2 1`\n"
            r"For other equation graphing use %equation"
        ), aliases=["quad"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quadratic(self, ctx, a: float, b: float, c: float):
        image = await self.loop.run_in_executor(None, quadratic, a, b, c)
        return await ctx.send(file=image)

    @commands.command(
        name="linear", 
        description=(
            "Plots a linear-line-graph based on the data points that you input\n"
            "Accepts only numerical `m, b` values\n"
            "EX: `%quad 2 1`\n"
            r"For other equation graphing use %equation"
        )
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def linear(self, ctx, m: float, b: float):
        image = await self.loop.run_in_executor(None, linear, m, b)
        return await ctx.send(file=image)

    @commands.command(
        name="equation", 
        description="Graphs your equation\nEx: `%eq 2x+1 ; %eq 2x^2 + 4x -3`", 
        aliases=["eq"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def equation(self, ctx, equation: str):
        try:
            image = await self.loop.run_in_executor(None, equation_, equation)
            return await ctx.send(file=image)
        except TypeError:
            return await ctx.send("Invalid equation\nMake sure the only variable present is `x`!")

    @commands.command(name="exponential", description="Plots an exponential-line-graph based on the data points that you input", aliases=["exp"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def exponential(self, ctx, *args):
        if not data_check(args):
            return await ctx.send("data points must be numerical values!")
        image = await self.loop.run_in_executor(None, exponent, *args)
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