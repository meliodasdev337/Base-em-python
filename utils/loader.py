import discord
from discord.ext import commands
import importlib
import os

class Loader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, cog: str):
        """Carrega um cog"""
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Cog `{cog}` carregado!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao carregar `{cog}`: {e}")
    
    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, cog: str):
        """Descarrega um cog"""
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Cog `{cog}` descarregado!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao descarregar `{cog}`: {e}")
    
    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Recarrega um cog"""
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Cog `{cog}` recarregado!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao recarregar `{cog}`: {e}")
    
    @commands.command(name="reloadall", hidden=True)
    @commands.is_owner()
    async def reload_all(self, ctx):
        """Recarrega todos os cogs"""
        cogs = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog = filename[:-3]
                try:
                    await self.bot.reload_extension(f"cogs.{cog}")
                    cogs.append(f"✅ {cog}")
                except Exception as e:
                    cogs.append(f"❌ {cog}: {e}")
        
        await ctx.send("**Recarregamento completo:**\n" + "\n".join(cogs))

async def setup(bot):
    await bot.add_cog(Loader(bot))
